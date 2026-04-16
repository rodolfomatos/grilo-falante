"""
OpenDataLoader PDF Service.

Integrates with opendataloader-pdf for PDF extraction:
- https://github.com/opendataloader-project/opendataloader-pdf
- Extracts PDF to Markdown + JSON with bounding boxes
- Supports OCR, tables, formulas, multi-column
- #1 in benchmarks (0.907 overall)

Falls back to basic text extraction if opendataloader is not available.
"""

import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

OPENDATALOADER_AVAILABLE = False
opendataloader_pdf = None

try:
    import opendataloader_pdf
    OPENDATALOADER_AVAILABLE = True
    logger.info("OpenDataLoader PDF is available")
except ImportError:
    logger.warning(
        "OpenDataLoader PDF not installed. "
        "Install with: pip install opendataloader-pdf"
    )


class OpenDataLoaderService:
    """
    Service for processing PDF documents using OpenDataLoader.

    OpenDataLoader extracts PDF content to:
    - Markdown (structured text)
    - JSON (with bounding boxes, metadata)

    Supports:
    - OCR for scanned documents
    - Table extraction
    - Formula extraction
    - Multi-column layout handling
    """

    def __init__(self, output_dir: str = "/tmp/grilo_pdf_output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    async def process_pdf(
        self,
        file_path: str,
        extract_tables: bool = True,
        extract_formulas: bool = False,
        enable_ocr: bool = False,
    ) -> Dict[str, Any]:
        """
        Process a PDF file using OpenDataLoader.

        Args:
            file_path: Path to the PDF file
            extract_tables: Whether to extract tables
            extract_formulas: Whether to extract formulas
            enable_ocr: Whether to enable OCR for scanned pages

        Returns:
            Dict with:
            - markdown: Extracted text in markdown format
            - json_path: Path to JSON output file
            - pages: Number of pages processed
            - success: Whether processing succeeded
            - error: Error message if failed
        """
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"File not found: {file_path}",
                "markdown": "",
                "json_path": None,
                "pages": 0,
            }

        file_name = Path(file_path).stem
        output_subdir = os.path.join(self.output_dir, file_name)
        os.makedirs(output_subdir, exist_ok=True)

        if OPENDATALOADER_AVAILABLE:
            return await self._process_with_opendataloader(
                file_path=file_path,
                output_subdir=output_subdir,
                extract_tables=extract_tables,
                extract_formulas=extract_formulas,
                enable_ocr=enable_ocr,
            )
        else:
            return await self._process_fallback(
                file_path=file_path,
                output_subdir=output_subdir,
            )

    async def _process_with_opendataloader(
        self,
        file_path: str,
        output_subdir: str,
        extract_tables: bool,
        extract_formulas: bool,
        enable_ocr: bool,
    ) -> Dict[str, Any]:
        """Process PDF using opendataloader_pdf library."""
        try:
            result = opendataloader_pdf.convert(
                input_path=[file_path],
                output_dir=output_subdir,
                format="markdown,json",
                extract_tables=extract_tables,
                extract_formulas=extract_formulas,
                ocr=enable_ocr,
            )

            markdown_path = os.path.join(output_subdir, f"{Path(file_path).stem}.md")
            json_path = os.path.join(output_subdir, f"{Path(file_path).stem}.json")

            markdown_content = ""
            if os.path.exists(markdown_path):
                with open(markdown_path, "r", encoding="utf-8") as f:
                    markdown_content = f.read()

            json_data = {}
            if os.path.exists(json_path):
                with open(json_path, "r", encoding="utf-8") as f:
                    json_data = json.load(f)

            pages = json_data.get("metadata", {}).get("pages", 0)

            logger.info(f"Processed PDF: {file_path} ({pages} pages)")

            return {
                "success": True,
                "markdown": markdown_content,
                "json_data": json_data,
                "json_path": json_path,
                "markdown_path": markdown_path,
                "pages": pages,
                "error": None,
            }

        except Exception as e:
            logger.error(f"OpenDataLoader error: {e}")
            return {
                "success": False,
                "error": str(e),
                "markdown": "",
                "json_path": None,
                "pages": 0,
            }

    async def _process_fallback(
        self,
        file_path: str,
        output_subdir: str,
    ) -> Dict[str, Any]:
        """Fallback extraction using pdftotext or basic methods."""
        try:
            if shutil.which("pdftotext"):
                result = subprocess.run(
                    ["pdftotext", "-layout", file_path, "-"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                markdown = result.stdout
            else:
                markdown = await self._extract_basic_pdf(file_path)

            json_path = os.path.join(output_subdir, f"{Path(file_path).stem}_fallback.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump({
                    "metadata": {"source": "fallback_extraction"},
                    "content": markdown,
                }, f)

            return {
                "success": True,
                "markdown": markdown,
                "json_data": {"content": markdown},
                "json_path": json_path,
                "pages": markdown.count("\f") + 1 if "\f" in markdown else 1,
                "error": "Used fallback extraction (opendataloader-pdf not installed)",
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "markdown": "",
                "json_path": None,
                "pages": 0,
            }

    async def _extract_basic_pdf(self, file_path: str) -> str:
        """Basic PDF text extraction without external tools."""
        try:
            import PyPDF2
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                text_parts = []
                for page in reader.pages:
                    text_parts.append(page.extract_text())
                return "\n\n".join(text_parts)
        except ImportError:
            logger.warning("PyPDF2 not installed, using raw bytes extraction")
            with open(file_path, "rb") as f:
                content = f.read()
            import re
            text = re.sub(rb'[^\x20-\x7E\n\r]', b' ', content)
            return text.decode("ascii", errors="ignore")

    def extract_chunks(
        self,
        markdown: str,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Split markdown content into chunks for RAG indexing.

        Args:
            markdown: Markdown content to chunk
            chunk_size: Target size for each chunk (words)
            chunk_overlap: Overlap between chunks

        Returns:
            List of chunks with metadata
        """
        words = markdown.split()
        chunks = []

        if len(words) <= chunk_size:
            return [{
                "content": markdown,
                "chunk_index": 0,
                "word_count": len(words),
            }]

        start = 0
        chunk_index = 0
        while start < len(words):
            end = start + chunk_size
            chunk_words = words[start:end]
            chunk_content = " ".join(chunk_words)

            chunks.append({
                "content": chunk_content,
                "chunk_index": chunk_index,
                "word_count": len(chunk_words),
                "start_word": start,
                "end_word": end,
            })

            start = end - chunk_overlap
            chunk_index += 1

        return chunks


import shutil