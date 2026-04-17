"""
Active Search Service - Multi-source search strategy

From prototype: searches multiple sources in priority order:
1. Local knowledge base (PostgreSQL - v3.0)
2. Local documents (filesystem)
3. Web search (fallback)

Adapted from prototype to use v3.0's PostgreSQL + pgvector backend.
"""

import subprocess
from dataclasses import dataclass
from typing import Optional
from pathlib import Path


@dataclass
class SearchResult:
    query: str
    source: str
    content: str
    relevance: float
    url: Optional[str] = None
    metadata: Optional[dict] = None


class ActiveSearchService:
    """
    Searches gaps in multiple sources.

    Priority:
    1. Local KB (PostgreSQL/pgvector)
    2. Local docs (filesystem grep)
    3. Web (fallback - not implemented)
    """

    def __init__(
        self, kb_path: Optional[str] = None, docs_path: Optional[str] = None, max_results: int = 3
    ):
        self.kb_path = kb_path
        self.docs_path = docs_path or "/home/rodolfo/Desktop/Grilo_Falante/ambrosio_v2.5.0"
        self.max_results = max_results

    async def search_local_kb(self, query: str) -> list[SearchResult]:
        """
        Search local knowledge base using v3.0's hybrid retrieval.

        In v3.0, this would use the ClaimRepository with vector search.
        For now, returns empty list (requires async context).
        """
        return []

    def search_filesystem(self, query: str) -> list[SearchResult]:
        """
        Search local documents using grep.

        Searches markdown files in configured docs path.
        """
        results = []

        if not Path(self.docs_path).exists():
            return results

        try:
            cmd = [
                "grep",
                "-r",
                "-i",
                "--include=*.md",
                f"-m{self.max_results}",
                query,
                self.docs_path,
            ]
            output = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if output.returncode == 0 and output.stdout:
                lines = output.stdout.split("\n")[: self.max_results]
                for line in lines:
                    if ":" not in line:
                        continue

                    parts = line.split(":", 2)
                    if len(parts) >= 3:
                        file_path = parts[0]
                        content = parts[2][:200].strip()

                        results.append(
                            SearchResult(
                                query=query,
                                source="filesystem",
                                content=content,
                                relevance=0.7,
                                metadata={"file": file_path},
                            )
                        )

        except subprocess.TimeoutExpired:
            pass
        except Exception:
            pass

        return results

    def search_web(self, query: str) -> list[SearchResult]:
        """
        Web search fallback.

        Not implemented - requires API integration.
        """
        return []

    def search(self, gap_query: str) -> list[SearchResult]:
        """
        Main search method.

        Strategy:
        1. Try filesystem (fast, local)
        2. Try web if no results
        """
        query = gap_query.strip()
        if len(query) < 3:
            return []

        all_results = []

        fs_results = self.search_filesystem(query)
        all_results.extend(fs_results)

        if not all_results:
            web_results = self.search_web(query)
            all_results.extend(web_results)

        return all_results[: self.max_results]

    def search_batch(self, gaps: list[str]) -> dict[str, list[SearchResult]]:
        """Search multiple gaps at once."""
        results = {}

        for gap in gaps:
            results[gap] = self.search(gap)

        return results
