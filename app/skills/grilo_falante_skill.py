"""
Grilo Falante Skill

Main skill for epistemic analysis of content.
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any
from pathlib import Path

from app.services.pipeline import Pipeline, get_pipeline, AnalysisResult
from app.data.memory.semantic import get_semantic_memory

logger = logging.getLogger(__name__)


class GriloFalanteSkill:
    """
    Skill for Grilo Falante analysis.
    
    Applies GMIF classification and MemPalace persistence
    to any content.
    """
    
    def __init__(self):
        self.pipeline = get_pipeline()
        self.memory = get_semantic_memory()
    
    async def analyse(
        self,
        content: Any,
        type: str = "text",
        metadata: Optional[Dict] = None,
    ) -> Dict:
        """
        Analyse content.
        
        Args:
            content: Text, List[Dict], or Dict
            type: text, chat, article, decision
            metadata: Additional metadata
            
        Returns:
            Analysis result with GF-IDs
        """
        result = await self.pipeline.analyse(content, type, metadata)
        
        return {
            "gf_ids": result.gf_ids,
            "total_claims": len(result.claims),
            "classifications": {
                k: {
                    "type": v.type.value,
                    "description": v.description,
                    "confidence": v.confidence,
                }
                for k, v in result.classifications.items()
            },
            "graph": result.graph.to_dict(),
            "objeto_digital": result.objeto_digital.to_dict(),
        }
    
    async def analyse_file(
        self,
        path: str,
        type: Optional[str] = None,
    ) -> Dict:
        """Analyse a file."""
        file_path = Path(path)
        
        if not file_path.exists():
            return {"error": f"File not found: {path}"}
        
        # Determine type from extension
        if type is None:
            suffix = file_path.suffix.lower()
            if suffix == ".py":
                type = "code"
            elif suffix == ".md":
                type = "text"
            else:
                type = "text"
        
        # Read content
        content = file_path.read_text()
        
        return await self.analyse(
            content,
            type=type,
            metadata={"name": file_path.name},
        )
    
    async def analyse_chat(
        self,
        messages: List[Dict],
        session_id: str,
    ) -> Dict:
        """Analyse chat messages."""
        return await self.analyse(
            messages,
            type="chat",
            metadata={
                "session_id": session_id,
                "total_messages": len(messages),
            },
        )
    
    async def analyse_article(
        self,
        article: Dict,
        doi: Optional[str] = None,
    ) -> Dict:
        """Analyse scientific article."""
        return await self.analyse(
            article,
            type="article",
            metadata={"doi": doi},
        )
    
    def search(
        self,
        query: str,
        wing: Optional[str] = None,
    ) -> List[Dict]:
        """Search stored memories."""
        return self.pipeline.search_memory(query, wing=wing)
    
    def list_claims(
        self,
        wing: Optional[str] = None,
        gmif_type: Optional[str] = None,
    ) -> List[Dict]:
        """List stored claims."""
        results = self.memory.search("", wing=wing, limit=100)
        
        if gmif_type:
            results = [r for r in results if r.get("gmif_type") == gmif_type]
        
        return results
    
    def get_stats(self) -> Dict:
        """Get skill statistics."""
        return {
            "memory": self.memory.get_stats(),
        }


# Initialize singleton
_skill: Optional[GriloFalanteSkill] = None


def get_skill() -> GriloFalanteSkill:
    global _skill
    if _skill is None:
        _skill = GriloFalanteSkill()
    return _skill


# CLI interface
async def main():
    """CLI entry point."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: grilo_falante <command> [args]")
        print("Commands:")
        print("  analyse <file>    Analyse file")
        print("  search <query>   Search memories")
        print("  stats           Show statistics")
        return
    
    skill = get_skill()
    command = sys.argv[1]
    
    if command == "analyse":
        if len(sys.argv) < 3:
            print("Usage: grilo_falante analyse <file>")
            return
        
        result = await skill.analyse_file(sys.argv[2])
        print(json.dumps(result, indent=2, default=str))
    
    elif command == "search":
        if len(sys.argv) < 3:
            print("Usage: grilo_falante search <query>")
            return
        
        results = skill.search(sys.argv[2])
        print(json.dumps(results, indent=2))
    
    elif command == "stats":
        stats = skill.get_stats()
        print(json.dumps(stats, indent=2))
    
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    asyncio.run(main())