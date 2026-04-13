#!/usr/bin/env python3
"""
Minimal LOADER/KERNEL runtime for Grilo Falante.

This module does three things only:
1. materialize an explicit LOAD act
2. resolve authoritative artefacts from KERNEL.md
3. produce SystemUseRecord traces for runtime governance
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import re


DEFAULT_SYSTEM_PATH = Path("/home/rodolfo/src/ambrosio_v2.5.0/system.md")
DEFAULT_LOADER_PATH = Path("/home/rodolfo/src/ambrosio_v2.5.0/loader/LOADER.md")
DEFAULT_KERNEL_PATH = Path("/home/rodolfo/src/ambrosio_v2.5.0/system/KERNEL.md")


@dataclass
class SystemUseRecord:
    artefact_type: str = "Objeto Digital"
    record_type: str = "SystemUseRecord"
    source: str = ""
    context: str = ""
    effect: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class LoaderResult:
    loaded: bool
    active: bool
    blocked: bool
    system_name: str
    system_path: str
    loader_path: str
    kernel_path: str
    authoritative_artefacts: Dict[str, List[str]]
    use_records: List[Dict]
    block_reason: Optional[str] = None
    block_details: Optional[Dict] = None
    error: Optional[str] = None


class GriloLoaderKernel:
    def __init__(
        self,
        system_path: Path = DEFAULT_SYSTEM_PATH,
        loader_path: Path = DEFAULT_LOADER_PATH,
        kernel_path: Path = DEFAULT_KERNEL_PATH,
    ):
        self.system_path = Path(system_path)
        self.loader_path = Path(loader_path)
        self.kernel_path = Path(kernel_path)
        self.use_records: List[SystemUseRecord] = []

    def load(self, command: str = 'LOAD GriloFalante FROM system.md') -> LoaderResult:
        normalized = self._normalize_command(command)
        if normalized != 'LOAD GriloFalante FROM system.md':
            return LoaderResult(
                loaded=False,
                active=False,
                blocked=True,
                system_name="GriloFalante",
                system_path=str(self.system_path),
                loader_path=str(self.loader_path),
                kernel_path=str(self.kernel_path),
                authoritative_artefacts={},
                use_records=[],
                block_reason="invalid_load_act",
                block_details={"expected": "LOAD GriloFalante FROM system.md", "received": normalized},
                error="Invalid LOAD act. Expected explicit LOAD GriloFalante FROM system.md",
            )

        for path in [self.system_path, self.loader_path, self.kernel_path]:
            if not path.exists():
                return LoaderResult(
                    loaded=False,
                    active=False,
                    blocked=True,
                    system_name="GriloFalante",
                    system_path=str(self.system_path),
                    loader_path=str(self.loader_path),
                    kernel_path=str(self.kernel_path),
                    authoritative_artefacts={},
                    use_records=[],
                    block_reason="missing_required_artefact",
                    block_details={"missing_path": str(path)},
                    error=f"Missing required artefact: {path}",
                )

        authoritative = self._resolve_kernel_authority()
        self._materialize_use(
            source="LOADER.md",
            context="Explicit activation of governed cycle",
            effect="Regime became operational through explicit LOAD act",
        )
        self._materialize_use(
            source="KERNEL.md",
            context="Authority resolution for current governed cycle",
            effect="Operational authority resolved to kernel-listed artefacts",
        )

        return LoaderResult(
            loaded=True,
            active=True,
            blocked=False,
            system_name="GriloFalante",
            system_path=str(self.system_path),
            loader_path=str(self.loader_path),
            kernel_path=str(self.kernel_path),
            authoritative_artefacts=authoritative,
            use_records=[record.__dict__ for record in self.use_records],
        )

    def materialize_graph_use(self, graph_name: str, state: str, transition: str) -> Dict:
        record = self._materialize_use(
            source=graph_name,
            context=f"State={state}",
            effect=f"Validated transition={transition}",
        )
        return record.__dict__

    def _normalize_command(self, command: str) -> str:
        command = command.strip()
        if command == 'LOAD ""':
            return 'LOAD GriloFalante FROM system.md'
        return command

    def _materialize_use(self, source: str, context: str, effect: str) -> SystemUseRecord:
        record = SystemUseRecord(source=source, context=context, effect=effect)
        self.use_records.append(record)
        return record

    def _resolve_kernel_authority(self) -> Dict[str, List[str]]:
        content = self.kernel_path.read_text()
        sections: Dict[str, List[str]] = {}
        current_section: Optional[str] = None

        for raw_line in content.splitlines():
            line = raw_line.strip()
            section_match = re.match(r"#\s+\d+\.\s+(.*)", line)
            if section_match:
                current_section = section_match.group(1)
                sections.setdefault(current_section, [])
                continue

            if current_section and line.startswith("*"):
                item = line.lstrip("* ").strip()
                if item:
                    sections[current_section].append(item)

        return {
            "constitutional_layer": sections.get("Constitutional Layer", []),
            "execution_pipeline": sections.get("Execution Pipeline", []),
            "epistemic_graph_infrastructure": sections.get("Epistemic Graph Infrastructure", []),
            "validation_mechanisms": sections.get("Validation Mechanisms", []),
        }
