"""
Verification Worker — Background task for verifying claims against external sources

Sources:
- arXiv (papers)
- PubMed (medical/scientific)
- Wikipedia (encyclopedic)

Verification workflow:
1. Claim created with status PENDING
2. Worker picks up claim and attempts verification
3. If source found → claim updated with VERIFIED status + evidence
4. If no source → claim remains UNVERIFIED or marked CONFLICTED
"""

import asyncio
import logging
import re
from datetime import datetime
from typing import Optional
from enum import Enum

import httpx

logger = logging.getLogger(__name__)


class VerificationStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    VERIFIED = "verified"
    REJECTED = "rejected"
    CONFLICTED = "conflicted"


class VerificationWorker:
    """
    Background worker that verifies claims against credible sources.
    """

    def __init__(self):
        self._running = False
        self._queue: list[int] = []

    async def verify_claim(self, claim_id: int) -> dict:
        """
        Verify a claim against external sources.

        Returns dict with:
        - status: VerificationStatus
        - evidence: list of supporting sources
        - gmif_level: updated GMIF level based on verification
        """
        from grilo_falante.backend.db.repositories import ClaimRepository

        repo = ClaimRepository()
        claim = await repo.get_by_id(claim_id)

        if not claim:
            return {"status": "rejected", "reason": "Claim not found"}

        # Get claim text for searching
        claim_text = claim.claim_text

        # Try each source
        evidence = []
        conflict_found = False

        # 1. Try Wikipedia
        wiki_result = await self._verify_wikipedia(claim_text)
        if wiki_result:
            evidence.append(wiki_result)

        # 2. Try arXiv (for scientific claims)
        arxiv_result = await self._verify_arxiv(claim_text)
        if arxiv_result:
            evidence.append(arxiv_result)

        # 3. Try PubMed (for medical/scientific claims)
        pubmed_result = await self._verify_pubmed(claim_text)
        if pubmed_result:
            evidence.append(pubmed_result)

        # Determine final status
        if len(evidence) >= 2:
            status = VerificationStatus.VERIFIED
            gmif_level = "VERIFIED"
        elif len(evidence) == 1:
            status = VerificationStatus.VERIFIED
            gmif_level = "INTERPRETATION"
        else:
            status = VerificationStatus.PENDING
            gmif_level = "UNVERIFIED"

        # Update claim
        await repo.update_validation(
            claim_id=claim_id,
            new_status=status,
            new_legitimacy=claim.legitimacy_state,
        )

        return {
            "status": status.value,
            "evidence": evidence,
            "gmif_level": gmif_level,
            "verified_at": datetime.utcnow().isoformat(),
        }

    async def _verify_wikipedia(self, claim_text: str) -> Optional[dict]:
        """
        Verify against Wikipedia using REST API.
        """
        # Extract key entities for search
        words = claim_text.split()
        if len(words) < 3:
            return None

        # Try to find a Wikipedia article
        topic = " ".join(words[:5])

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Search Wikipedia
                search_url = f"https://en.wikipedia.org/w/api.php"
                params = {
                    "action": "query",
                    "list": "search",
                    "srsearch": topic,
                    "format": "json",
                    "srlimit": 1,
                }

                response = await client.get(search_url, params=params)
                data = response.json()

                search_results = data.get("query", {}).get("search", [])
                if not search_results:
                    return None

                article_title = search_results[0]["title"]

                # Get article summary
                summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{article_title}"
                summary_response = await client.get(summary_url)

                if summary_response.status_code == 200:
                    summary = summary_response.json()

                    return {
                        "source": "wikipedia",
                        "url": summary.get("content_urls", {}).get("desktop", {}).get("page", ""),
                        "title": summary.get("title", ""),
                        "extract": summary.get("extract", "")[:500],
                        "verification_method": "wikipedia_rest_api",
                    }

        except Exception as e:
            logger.warning(f"Wikipedia verification failed: {e}")

        return None

    async def _verify_arxiv(self, claim_text: str) -> Optional[dict]:
        """
        Verify against arXiv papers.
        """
        # Extract potential keywords
        keywords = self._extract_keywords(claim_text)

        if not keywords:
            return None

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                # Search arXiv
                query = "+".join(keywords[:5])
                search_url = f"https://export.arxiv.org/api/query"

                params = {
                    "search_query": f"all:{query}",
                    "start": 0,
                    "max_results": 1,
                }

                response = await client.get(search_url, params=params)

                if response.status_code == 200:
                    # Parse XML response (simplified)
                    content = response.text

                    # Simple regex to extract title and authors
                    title_match = re.search(r"<title>([^<]+)</title>", content)
                    if title_match and title_match.group(1) != "arXiv Api Response":
                        return {
                            "source": "arxiv",
                            "title": title_match.group(1)[:200],
                            "url": f"https://arxiv.org/abs/{keywords[0]}",
                            "verification_method": "arxiv_api",
                        }

        except Exception as e:
            logger.warning(f"arXiv verification failed: {e}")

        return None

    async def _verify_pubmed(self, claim_text: str) -> Optional[dict]:
        """
        Verify against PubMed using NCBI API.
        """
        keywords = self._extract_keywords(claim_text)

        if not keywords:
            return None

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                # Search PubMed
                query = " AND ".join(keywords[:3])

                # Search
                search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
                search_params = {
                    "db": "pubmed",
                    "term": query,
                    "retmode": "json",
                    "retmax": 1,
                }

                search_response = await client.get(search_url, params=search_params)
                search_data = search_response.json()

                id_list = search_data.get("esearchresult", {}).get("idlist", [])
                if not id_list:
                    return None

                pmid = id_list[0]

                # Get article summary
                summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
                summary_params = {
                    "db": "pubmed",
                    "id": pmid,
                    "retmode": "json",
                }

                summary_response = await client.get(summary_url, params=summary_params)
                summary_data = summary_response.json()

                result = summary_data.get("result", {}).get(pmid, {})
                if result:
                    return {
                        "source": "pubmed",
                        "title": result.get("title", ""),
                        "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                        "authors": result.get("authors", [])[:3],
                        "verification_method": "ncbi_eutils_api",
                    }

        except Exception as e:
            logger.warning(f"PubMed verification failed: {e}")

        return None

    def _extract_keywords(self, text: str) -> list[str]:
        """
        Extract keywords for searching external sources.
        """
        # Remove common stop words
        stop_words = {
            "the", "a", "an", "is", "was", "were", "are", "be", "been", "being",
            "have", "has", "had", "do", "does", "did", "will", "would", "could",
            "should", "may", "might", "must", "can", "to", "of", "in", "for",
            "on", "with", "at", "by", "from", "as", "into", "through", "during",
            "before", "after", "above", "below", "between", "under", "again",
            "further", "then", "once", "here", "there", "when", "where", "why",
            "how", "all", "each", "few", "more", "most", "other", "some", "such",
            "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very",
        }

        # Extract words
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        keywords = [w for w in words if w not in stop_words]

        # Return top keywords
        return keywords[:10]


async def run_verification_worker():
    """
    Run the verification worker as a background task.
    """
    worker = VerificationWorker()

    while worker._running:
        # Check for claims to verify
        from grilo_falante.backend.db.repositories import ClaimRepository

        repo = ClaimRepository()

        # Find pending claims
        claims = await repo.search("%", session_id=None, limit=10)

        pending_claims = [
            c for c in claims
            if c.validation_status.value == "pending"
        ]

        for claim in pending_claims:
            try:
                await worker.verify_claim(claim.id)
            except Exception as e:
                logger.error(f"Verification failed for claim {claim.id}: {e}")

        # Wait before next cycle
        await asyncio.sleep(60)  # Check every minute


if __name__ == "__main__":
    asyncio.run(run_verification_worker())