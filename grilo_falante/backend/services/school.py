"""
School Mode Service — "Ir à Escola" 8-step workflow

Steps:
0. Trigger - Gap identified or user requests
1. Query Formulation - Extract search keywords
2. Source Discovery - Search arXiv, OpenAlex, WoS
3. Source Selection - Flag top results as CANDIDATA
4. Materialization - Download and parse
5. Double Feynman Validation - F1 + F2 extraction
6. GMIF Classification - Classify each claim
7. Claim Creation - Create governed claims
8. Gap Resolution - Update gap status
"""

import hashlib
import json
import re
from dataclasses import dataclass, field
from typing import Optional

import httpx

from grilo_falante.models import (
    Gap,
    GapStatus,
    GovernedSource,
    GovernedClaim,
    ShadowDocument,
    StudyPlan,
    StudyPlanStep,
    GMIFLevel,
    ClaimType,
    Attribution,
    EpistemicRole,
    LegitimacyState,
    ValidationState,
)
from grilo_falante.backend.db.repositories import (
    GapRepository,
    SourceRepository,
    ClaimRepository,
    ShadowDocumentRepository,
    StudyPlanRepository,
    generate_key,
)
from grilo_falante.backend.services.feynman import FeynmanService


ARXIV_API = "http://export.arxiv.org/api/query"
OPENALEX_API = "https://api.openalex.org"


@dataclass
class SourceDiscoveryResult:
    """Discovered source from search."""

    source_key: str
    title: str
    authors: list[str]
    year: Optional[int]
    doi: Optional[str]
    abstract: str
    url: str
    relevance_score: float = 0.0


@dataclass
class SchoolModeResult:
    """Result of school mode execution."""

    success: bool
    gap: Gap
    study_plan: Optional[StudyPlan] = None
    sources_found: int = 0
    claims_created: int = 0
    error: Optional[str] = None


class SchoolModeService:
    """
    Implements the 8-step "Ir à Escola" workflow.

    For gap resolution through source discovery and validation.
    """

    def __init__(self):
        self.gap_repo = GapRepository()
        self.source_repo = SourceRepository()
        self.claim_repo = ClaimRepository()
        self.shadow_repo = ShadowDocumentRepository()
        self.study_plan_repo = StudyPlanRepository()
        self.feynman_service = FeynmanService()

    async def execute(self, gap: Gap) -> SchoolModeResult:
        """
        Execute full school mode workflow for a gap.

        Args:
            gap: The gap to resolve

        Returns:
            SchoolModeResult with execution details
        """
        try:
            # Update gap status
            gap = await self.gap_repo.update_status(gap.gap_key, GapStatus.IN_PROGRESS)

            # Step 1: Formulate queries
            queries = self._formulate_queries(gap)

            # Step 2: Discover sources
            sources = await self._discover_sources(queries)

            if not sources:
                return SchoolModeResult(
                    success=False,
                    gap=gap,
                    error="No sources found for gap",
                )

            # Step 3-4: Materialize sources and create claims
            claims_count = 0
            for source in sources[:5]:  # Top 5
                await self._materialize_source(source)
                claims = await self._double_feynman_validation(source)
                claims_count += len(claims)

            # Step 5: Create study plan
            study_plan = await self._create_study_plan(gap, sources)

            # Update gap status
            gap = await self.gap_repo.update_status(gap.gap_key, GapStatus.RESOLVED)

            return SchoolModeResult(
                success=True,
                gap=gap,
                study_plan=study_plan,
                sources_found=len(sources),
                claims_created=claims_count,
            )

        except Exception as e:
            return SchoolModeResult(
                success=False,
                gap=gap,
                error=str(e),
            )

    def _formulate_queries(self, gap: Gap) -> list[str]:
        """Step 1: Formulate search queries from gap."""
        queries = [gap.query]

        # Extract from claim template
        template = gap.claim_template
        if template:
            subject = template.get("subject", "")
            obj = template.get("object", "")
            if subject:
                queries.append(subject)
            if obj:
                queries.append(obj)

        # Extract keywords
        keywords = self._extract_keywords(gap.query)
        queries.extend(keywords[:3])

        # Deduplicate
        seen = set()
        unique = []
        for q in queries:
            q_lower = q.lower()
            if q_lower not in seen and len(q) > 3:
                seen.add(q_lower)
                unique.append(q)

        return unique[:3]

    def _extract_keywords(self, text: str) -> list[str]:
        """Extract keywords from text."""
        stopwords = {
            "the",
            "a",
            "an",
            "is",
            "are",
            "was",
            "were",
            "what",
            "how",
            "why",
            "when",
            "where",
            "does",
            "do",
            "did",
        }
        words = re.findall(r"\b\w+\b", text.lower())
        return [w for w in words if w not in stopwords and len(w) > 3]

    async def _discover_sources(self, queries: list[str]) -> list[SourceDiscoveryResult]:
        """Step 2: Discover sources from APIs."""
        all_sources = []

        for query in queries:
            # Search arXiv
            arxiv_sources = await self._search_arxiv(query)
            all_sources.extend(arxiv_sources)

            # Search OpenAlex
            openalex_sources = await self._search_openalex(query)
            all_sources.extend(openalex_sources)

        # Sort by relevance and deduplicate
        all_sources.sort(key=lambda s: s.relevance_score, reverse=True)

        unique = []
        seen_titles = set()
        for source in all_sources:
            title_lower = source.title.lower()[:50]
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                unique.append(source)

        return unique[:10]

    async def _search_arxiv(self, query: str) -> list[SourceDiscoveryResult]:
        """Search arXiv API."""
        sources = []
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    ARXIV_API,
                    params={
                        "search_query": f"all:{query}",
                        "start": 0,
                        "max_results": 5,
                        "sortBy": "relevance",
                    },
                    timeout=30.0,
                )
                response.raise_for_status()

                content = response.text
                entries = re.findall(r"<entry>(.*?)</entry>", content, re.DOTALL)

                for entry in entries:
                    title_match = re.search(r"<title>(.*?)</title>", entry, re.DOTALL)
                    summary_match = re.search(r"<summary>(.*?)</summary>", entry, re.DOTALL)
                    author_matches = re.findall(r"<name>(.*?)</name>", entry)
                    published_match = re.search(r"<published>(.*?)</published>", entry)
                    id_match = re.search(r"<id>(.*?)</id>", entry)

                    if title_match and id_match:
                        title = title_match.group(1).replace("\n", " ").strip()
                        abstract = (
                            summary_match.group(1).replace("\n", " ").strip()
                            if summary_match
                            else ""
                        )

                        year = None
                        if published_match:
                            year_match = re.search(r"(\d{4})", published_match.group(1))
                            if year_match:
                                year = int(year_match.group(1))

                        url = id_match.group(1)
                        source_key = f"arxiv:{hashlib.md5(url.encode()).hexdigest()[:12]}"

                        sources.append(
                            SourceDiscoveryResult(
                                source_key=source_key,
                                title=title,
                                authors=author_matches[:5],
                                year=year,
                                doi=None,
                                abstract=abstract[:500],
                                url=url,
                                relevance_score=0.8,
                            )
                        )

        except Exception:
            pass

        return sources

    async def _search_openalex(self, query: str) -> list[SourceDiscoveryResult]:
        """Search OpenAlex API."""
        sources = []
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{OPENALEX_API}/works",
                    params={"search": query, "per_page": 5, "sort": "relevance_score:desc"},
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()

                for work in data.get("results", []):
                    authors = []
                    for author in work.get("authorships", [])[:5]:
                        if "display_name" in author.get("author", {}):
                            authors.append(author["author"]["display_name"])

                    doi = work.get("doi", "")
                    if doi:
                        doi = doi.split("/")[-1]

                    title = work.get("title", "Untitled")
                    source_key = (
                        f"openalex:{work['id'].split('/')[-1]}"
                        if work.get("id")
                        else f"openalex:{hashlib.md5(title.encode()).hexdigest()[:12]}"
                    )

                    sources.append(
                        SourceDiscoveryResult(
                            source_key=source_key,
                            title=title,
                            authors=authors,
                            year=work.get("publication_year"),
                            doi=doi,
                            abstract="",
                            url=work.get("doi", ""),
                            relevance_score=(work.get("relevance_score", 0) or 0) / 100.0,
                        )
                    )

        except Exception:
            pass

        return sources

    async def _materialize_source(self, source: SourceDiscoveryResult) -> GovernedSource:
        """Step 4: Materialize source as governed source."""
        existing = await self.source_repo.get_by_key(source.source_key)
        if existing:
            return existing

        governed_source = GovernedSource(
            source_key=source.source_key,
            title=source.title,
            authors=source.authors,
            year=source.year,
            doi=source.doi,
            source_type="paper",
            source_origin=source.source_key.split(":")[0],
            ingestion_origin="school_mode",
            raw_metadata={
                "abstract": source.abstract,
                "url": source.url,
                "relevance_score": source.relevance_score,
            },
        )
        return await self.source_repo.create(governed_source)

    async def _double_feynman_validation(
        self, source: SourceDiscoveryResult
    ) -> list[GovernedClaim]:
        """Step 5: Double Feynman validation."""
        governed_source = await self._materialize_source(source)

        # F1: Extract explicit claims (simplified)
        f1_claims = []
        if source.abstract:
            sentences = source.abstract.split(".")
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 30 and any(
                    kw in sentence.lower() for kw in ["shows", "data", "study", "results"]
                ):
                    f1_claims.append(sentence)

        # F2: Identify projections (simplified)
        f2_claims = []
        if source.abstract:
            sentences = source.abstract.split(".")
            for sentence in sentences:
                sentence = sentence.strip()
                if any(
                    kw in sentence.lower() for kw in ["therefore", "thus", "all", "always", "never"]
                ):
                    f2_claims.append(f"[PROJECTION] {sentence}")

        claims = []
        session_id = f"school_mode:{source.source_key}"

        # Create F1 claims (M1)
        for i, text in enumerate(f1_claims):
            claim_key = f"{source.source_key}:f1:{i}"
            claim = GovernedClaim(
                claim_key=claim_key,
                claim_text=text,
                claim_type=ClaimType.CORE_CLAIM,
                source_id=governed_source.id,
                session_id=session_id,
                gmif_level=GMIFLevel.M1_PRIMARY,
                gmif_confidence=0.8,
                attribution=Attribution.SOURCE_EXPLICIT,
                epistemic_role=EpistemicRole.DESCRIPTIVE,
                legitimacy_state=LegitimacyState.ASSERTED,
                validation_status=ValidationState.APPROVED,
                provenance={"f1_source": source.title},
            )
            created = await self.claim_repo.create(claim)
            claims.append(created)

        # Create F2 claims (M4)
        for i, text in enumerate(f2_claims):
            claim_key = f"{source.source_key}:f2:{i}"
            claim = GovernedClaim(
                claim_key=claim_key,
                claim_text=text,
                claim_type=ClaimType.PROJECTION,
                source_id=governed_source.id,
                session_id=session_id,
                gmif_level=GMIFLevel.M4_DOUBTFUL,
                gmif_confidence=0.3,
                attribution=Attribution.EDITORIAL_INFERENCE,
                epistemic_role=EpistemicRole.LIMITATION,
                legitimacy_state=LegitimacyState.SUSPENDED,
                validation_status=ValidationState.PENDING,
                provenance={"f2_warning": "Potential over-interpretation"},
            )
            created = await self.claim_repo.create(claim)
            claims.append(created)

        # Create shadow document
        shadow = ShadowDocument(
            source_id=governed_source.id,
            factual_summary=source.abstract[:500] if source.abstract else "",
            projected_claims=f2_claims,
            citations=[],
            limits=["Limited to abstract analysis"],
            misuse_risks=["Over-generalization", "Causal inference error"],
            status=ValidationState.APPROVED if f1_claims else ValidationState.PENDING,
            validation_notes=f"School Mode: F1={len(f1_claims)}, F2={len(f2_claims)}",
            f1_count=len(f1_claims),
            f2_count=len(f2_claims),
        )
        await self.shadow_repo.create(shadow)

        return claims

    async def _create_study_plan(self, gap: Gap, sources: list[SourceDiscoveryResult]) -> StudyPlan:
        """Create study plan from discovered sources."""
        steps = []
        for i, source in enumerate(sources[:5]):
            steps.append(
                StudyPlanStep(
                    order=i + 1,
                    description=f"Review: {source.title[:80]}...",
                    resources=[source.source_key],
                    estimated_time="15-30 min",
                    status="pending",
                    gap_key=gap.gap_key if i == 0 else None,
                )
            )

        steps.append(
            StudyPlanStep(
                order=len(steps) + 1,
                description="Synthesize findings",
                resources=[],
                estimated_time="10 min",
                status="pending",
            )
        )

        plan = StudyPlan(
            plan_key=generate_key("plan"),
            gap_key=gap.gap_key,
            topic=gap.query,
            steps=steps,
            status=GapStatus.IN_PROGRESS,
        )
        return await self.study_plan_repo.create(plan)
