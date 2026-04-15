"""
PDF Ingestion Service — Uses OpenDataLoader for PDF parsing

Supports:
- Local mode: Fast Java processing (0.015s/page)
- Output: JSON + Markdown + HTML

PDF parsing results are used to generate:
- Semantic chunks for embedding
- Shadow documents
- Extracted claims
"""

import asyncio
import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict, Any

from grilo_falante.config import settings


@dataclass
class PDFParseResult:
    success: bool
    file_path: str
    output_dir: str
    json_path: Optional[str] = None
    markdown_path: Optional[str] = None
    html_path: Optional[str] = None
    pages_processed: int = 0
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class PDFChunk:
    id: str
    type: str
    page_number: int
    content: str
    bounding_box: Optional[List[float]] = None
    heading_level: Optional[str] = None
    font: Optional[str] = None


class PDFIngestionService:
    """
    PDF ingestion using OpenDataLoader in local mode.

    Local mode uses Java-only processing (no AI backend required).
    Speed: ~0.015s per page for simple documents.
    """

    def __init__(
        self,
        java_path: Optional[str] = None,
        opendataloader_jar: Optional[str] = None,
    ):
        self.java_path = java_path or "java"
        self.jar_path = opendataloader_jar or os.getenv("OPENEDATALOADER_JAR", "")
        self.mode = settings.opendataloader_mode

    def is_available(self) -> bool:
        """Check if OpenDataLoader is available."""
        try:
            result = subprocess.run(
                [self.java_path, "-version"],
                capture_output=True,
                timeout=5,
            )
            return result.returncode == 0
        except Exception:
            return False

    async def parse(
        self,
        pdf_path: str,
        output_dir: Optional[str] = None,
        formats: tuple = ("json", "markdown"),
    ) -> PDFParseResult:
        """
        Parse a PDF file using OpenDataLoader.

        Args:
            pdf_path: Path to the PDF file
            output_dir: Directory for output files
            formats: Tuple of output formats ("json", "markdown", "html")

        Returns:
            PDFParseResult with parsed content and metadata
        """
        if not os.path.exists(pdf_path):
            return PDFParseResult(
                success=False,
                file_path=pdf_path,
                output_dir=output_dir or "",
                error="PDF file not found",
            )

        if output_dir is None:
            output_dir = tempfile.mkdtemp(prefix="grilo_ingestion_")

        os.makedirs(output_dir, exist_ok=True)

        if not self.is_available():
            return PDFParseResult(
                success=False,
                file_path=pdf_path,
                output_dir=output_dir,
                error="Java not available - install OpenJDK 11+",
            )

        cmd = self._build_command(pdf_path, output_dir, formats)

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=300,
            )

            if process.returncode != 0:
                return PDFParseResult(
                    success=False,
                    file_path=pdf_path,
                    output_dir=output_dir,
                    error=f"OpenDataLoader failed: {stderr.decode()[:500]}",
                )

            result = PDFParseResult(
                success=True,
                file_path=pdf_path,
                output_dir=output_dir,
                json_path=os.path.join(output_dir, f"{Path(pdf_path).stem}.json"),
                markdown_path=os.path.join(output_dir, f"{Path(pdf_path).stem}.md"),
                pages_processed=self._count_pages(os.path.join(output_dir, f"{Path(pdf_path).stem}.json")) if "json" in formats else 0,
                metadata=self._extract_metadata(os.path.join(output_dir, f"{Path(pdf_path).stem}.json")) if "json" in formats else {},
            )

            return result

        except asyncio.TimeoutError:
            return PDFParseResult(
                success=False,
                file_path=pdf_path,
                output_dir=output_dir,
                error="Timeout parsing PDF (file may be too large)",
            )
        except Exception as e:
            return PDFParseResult(
                success=False,
                file_path=pdf_path,
                output_dir=output_dir,
                error=str(e),
            )

    def _build_command(
        self,
        pdf_path: str,
        output_dir: str,
        formats: tuple,
    ) -> List[str]:
        """Build OpenDataLoader command."""
        cmd = [
            self.java_path,
            "-jar" if self.jar_path else "-jar",  # Placeholder for actual jar
            self.jar_path or "opendataloader-pdf-cli.jar",
            "-i", pdf_path,
            "-o", output_dir,
        ]

        format_str = ",".join(formats)
        cmd.extend(["-f", format_str])

        if self.mode == "local":
            cmd.append("--mode=local")

        return cmd

    def _count_pages(self, json_path: str) -> int:
        """Count pages in parsed JSON output."""
        if not os.path.exists(json_path):
            return 0

        try:
            with open(json_path) as f:
                data = json.load(f)
                if isinstance(data, list):
                    return len(set(item.get("page_number", 0) for item in data))
                return 0
        except Exception:
            return 0

    def _extract_metadata(self, json_path: str) -> Dict[str, Any]:
        """Extract metadata from JSON output."""
        if not os.path.exists(json_path):
            return {}

        try:
            with open(json_path) as f:
                data = json.load(f)

            metadata = {
                "total_elements": len(data) if isinstance(data, list) else 0,
                "element_types": {},
                "headings": [],
            }

            if isinstance(data, list):
                for item in data:
                    item_type = item.get("type", "unknown")
                    metadata["element_types"][item_type] = (
                        metadata["element_types"].get(item_type, 0) + 1
                    )
                    if item.get("type") == "heading":
                        metadata["headings"].append({
                            "level": item.get("heading level"),
                            "text": item.get("content", "")[:100],
                        })

            return metadata
        except Exception:
            return {}

    async def chunk_text(
        self,
        json_path: str,
        markdown_path: Optional[str] = None,
    ) -> List[PDFChunk]:
        """
        Convert parsed JSON to semantic chunks.

        Chunks are created by heading hierarchy for semantic coherence.
        """
        chunks = []

        if not json_path or not os.path.exists(json_path):
            return chunks

        try:
            with open(json_path) as f:
                elements = json.load(f)

            if not isinstance(elements, list):
                return chunks

            current_heading = None
            current_content = []
            current_page = 1

            for element in elements:
                elem_type = element.get("type", "paragraph")
                page = element.get("page number", 1)
                content = element.get("content", "").strip()

                if not content:
                    continue

                if elem_type == "heading":
                    if current_content:
                        chunks.append(PDFChunk(
                            id=f"chunk_{len(chunks)}",
                            type="section",
                            page_number=current_page,
                            content="\n".join(current_content),
                            heading_level=current_heading,
                        ))
                        current_content = []

                    current_heading = element.get("heading level", "h2")
                    current_page = page

                    chunks.append(PDFChunk(
                        id=f"chunk_{len(chunks)}",
                        type="heading",
                        page_number=page,
                        content=content,
                        heading_level=current_heading,
                    ))
                else:
                    current_content.append(content)
                    current_page = page

            if current_content:
                chunks.append(PDFChunk(
                    id=f"chunk_{len(chunks)}",
                    type="section",
                    page_number=current_page,
                    content="\n".join(current_content),
                    heading_level=current_heading,
                ))

        except Exception as e:
            pass

        return chunks

    async def extract_markdown(self, markdown_path: str) -> str:
        """Extract full markdown content."""
        if not markdown_path or not os.path.exists(markdown_path):
            return ""

        try:
            with open(markdown_path) as f:
                return f.read()
        except Exception:
            return ""

    def cleanup(self, output_dir: str) -> None:
        """Clean up temporary output directory."""
        try:
            shutil.rmtree(output_dir)
        except Exception:
            pass
