"""
Grilo Falante Skill

Main skill for epistemic analysis of content.
Includes /grilo chat command for governed conversations.
"""

import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from app.services.pipeline import Pipeline, get_pipeline, AnalysisResult
from app.data.memory.semantic import get_semantic_memory
from app.skills.chat_shell import ChatShell

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


async def run_chat_shell(shell: ChatShell) -> None:
    """
    Executar shell conversacional interativo.

    Args:
        shell: ChatShell instance
    """
    import sys

    print("=" * 60)
    print("GRILO FALANTE - CHAT GOVERNADO")
    print("=" * 60)
    print()
    print("Este chat é governado pelo regime Grilo Falante.")
    print("Todas as mensagens são analisadas para claims")
    print("e classificadas com GMIF (M1-M7).")
    print()
    print("Comandos:")
    print("  :quit, :exit    Sair")
    print("  :save           Guardar sessão")
    print("  :export         Exportar script de resume")
    print("  :status         Ver estado")
    print("  :ilhas          Listar ilhas ativas")
    print("  :dormir         Forçar ciclo dormir")
    print("  :acordar        Ver estado das ilhas")
    print("=" * 60)
    print()

    start_result = await shell.start()
    if not start_result.get("success"):
        print(f"Erro ao iniciar: {start_result.get('message')}")
        return

    print(f"Sessão iniciada: {start_result.get('session_id')}")
    print(f"Cycle ID: {start_result.get('cycle_id')}")
    print(f"Estado: {start_result.get('state')}")
    print()

    while True:
        try:
            user_input = input("> ")
        except (EOFError, KeyboardInterrupt):
            print("\n")
            break

        if not user_input.strip():
            continue

        if user_input.strip() in (":quit", ":exit", "/quit", "/exit"):
            end_result = await shell.end()
            print(f"Sessão terminada. Claims guardadas: {end_result.get('stats', {}).get('claims_count', 0)}")
            break

        if user_input.strip() == ":save":
            save_result = await shell.save()
            print(f"Sessão guardada: {json.dumps(save_result, indent=2, default=str)}")
            continue

        if user_input.strip() == ":export":
            script = shell.export_session()
            print(script)
            continue

        if user_input.strip() == ":status":
            status = shell.get_status()
            print(json.dumps(status, indent=2, default=str))
            continue

        if user_input.strip() == ":ilhas":
            resultado = await shell.acordar_ilhas()
            if resultado.get("success"):
                print(f"Ilhas ativas: {resultado.get('ilhas_ativas')}")
                print(f"Ilhas dormintes: {resultado.get('ilhas_dormintes')}")
                if resultado.get("bundle"):
                    print(f"Bundle disponível: {len(resultado.get('bundle', {}).get('ilhas', []))} ilhas")
            else:
                print(f"Erro: {resultado.get('error')}")
            continue

        if user_input.strip() == ":dormir":
            resultado = await shell.ir_dormir_ilhas()
            if resultado.get("sucesso"):
                print(f"Ciclo dormir: {resultado.get('pedras_criadas')} pedras, {resultado.get('ilhas_criadas')} ilhas")
            else:
                print(f"Erro: {resultado.get('error')}")
            continue

        if user_input.strip() == ":acordar":
            resultado = await shell.acordar_ilhas()
            if resultado.get("success"):
                print(f"Contexto restaurado: {resultado.get('ilhas_ativas')} ativas")
            else:
                print(f"Erro: {resultado.get('error')}")
            continue

        response = await shell.send_message(user_input, role="user")
        print(f"[{response.gmif_summary}] ", end="")
        print(response.message)
        print()


# Initialize singleton
_skill: Optional[GriloFalanteSkill] = None


def get_skill() -> GriloFalanteSkill:
    global _skill
    if _skill is None:
        _skill = GriloFalanteSkill()
    return _skill


async def list_ilhas(args: List[str]) -> None:
    """List memory islands."""
    only_ativas = "--ativas" in args or "-a" in args

    try:
        from grilo_falante.backend.db.ilhas_repository import IlhaRepository

        repo = IlhaRepository()
        if only_ativas:
            ilhas = await repo.listar_ativas(threshold=0.5)
            print(f"Ativas (score >= 0.5): {len(ilhas)}")
        else:
            ilhas = await repo.listar(limit=100)
            print(f"Total: {len(ilhas)}")

        print()
        for ilha in ilhas:
            print(f"  [{ilha.estado.value}] {ilha.id}")
            print(f"    Nome: {ilha.nome or '(sem nome)'}")
            print(f"    Score: {ilha.score_ativação:.3f}")
            print(f"    Membros: {len(ilha.membros)}")
            print(f"    Consolidação: {ilha.grau_consolidação:.2f}")
            print()

    except Exception as e:
        print(f"Erro ao listar ilhas: {e}")


async def cmd_dormir(args: List[str]) -> None:
    """Force sleep cycle."""
    session_id = None

    for i, arg in enumerate(args):
        if arg == "--session" and i + 1 < len(args):
            session_id = args[i + 1]

    session_id = session_id or f"cli_{datetime.now().strftime('%y%m%d_%H%M%S')}"

    try:
        from app.regime.dormir import ir_dormir

        interações = [{
            "tipo": "COMANDO_CLI",
            "conteúdo": "Forçado via comando dormir",
            "frequência": 0.5,
            "intensidade": 0.5,
            "novidade": 0.3,
            "relevância": 0.4,
        }]

        resultado = await ir_dormir(session_id=session_id, interações=interações)

        print("Ciclo Ir Dormir executado:")
        print(f"  Sucesso: {resultado.get('sucesso')}")
        print(f"  Pedras criadas: {resultado.get('pedras_criadas')}")
        print(f"  Ilhas criadas: {resultado.get('ilhas_criadas')}")
        print(f"  Ilhas atualizadas: {resultado.get('ilhas_actualizadas')}")
        print(f"  Agregações: {resultado.get('agregações_feitas')}")

    except Exception as e:
        print(f"Erro no ciclo dormir: {e}")


async def cmd_acordar(args: List[str]) -> None:
    """Wake cycle."""
    session_id = None
    tarefa = None

    for i, arg in enumerate(args):
        if arg == "--session" and i + 1 < len(args):
            session_id = args[i + 1]
        elif arg == "--tarefa" and i + 1 < len(args):
            tarefa = args[i + 1]

    session_id = session_id or f"cli_{datetime.now().strftime('%y%m%d_%H%M%S')}"

    try:
        from app.regime.acordar import acordar

        resultado = await acordar(session_id=session_id, tarefa=tarefa)

        print("Ciclo Acordar executado:")
        print(f"  Session: {resultado.session_id}")
        print(f"  Ilhas ativas: {len(resultado.ilhas_ativas)}")
        print(f"  Ilhas dormintes: {len(resultado.ilhas_dormintes)}")

        if resultado.bundle:
            print(f"  Bundle tarefa: {resultado.bundle.get('tarefa', 'N/A')}")
            print(f"  Ilhas no bundle: {len(resultado.bundle.get('ilhas', []))}")

    except Exception as e:
        print(f"Erro no ciclo acordar: {e}")


async def cmd_estado(args: List[str]) -> None:
    """Show system state."""
    try:
        from grilo_falante.backend.db.ilhas_repository import IlhaRepository, PedraRepository

        ilha_repo = IlhaRepository()
        pedra_repo = PedraRepository()

        ilhas = await ilha_repo.listar(limit=100)
        pedras = await pedra_repo.listar(limit=100)

        ilhas_ativas = [i for i in ilhas if i.score_ativação >= 0.5]
        ilhas_erodendo = [i for i in ilhas if 0.1 <= i.score_ativação < 0.5]
        ilhas_dormintes = [i for i in ilhas if i.score_ativação < 0.1]

        pedras_pendentes = await pedra_repo.listar_pendentes(limit=100)

        print("=" * 50)
        print("ESTADO DO SISTEMA - MEMÓRIA INSULAR")
        print("=" * 50)
        print()
        print(f"ILHAS:")
        print(f"  Total: {len(ilhas)}")
        print(f"  Ativas: {len(ilhas_ativas)}")
        print(f"  Erodindo: {len(ilhas_erodendo)}")
        print(f"  Dormintes: {len(ilhas_dormintes)}")
        print()
        print(f"PEDRAS:")
        print(f"  Total: {len(pedras)}")
        print(f"  Pendentes: {len(pedras_pendentes)}")
        print()
        print("ILHAS ATIVAS:")
        for ilha in ilhas_ativas[:5]:
            print(f"  - {ilha.nome or ilha.id} (score: {ilha.score_ativação:.3f})")
        if len(ilhas_ativas) > 5:
            print(f"  ... e mais {len(ilhas_ativas) - 5}")
        print()

    except Exception as e:
        print(f"Erro ao obter estado: {e}")


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
        print("  chat            Start governed chat session")
        print("  chat --session <id>  Resume chat session")
        print("  ilhas            List memory islands")
        print("  ilhas --ativas   List active islands only")
        print("  dormir           Force sleep cycle")
        print("  acordar [--tarefa X]  Wake cycle")
        print("  estado           Show system state")
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

    elif command == "chat":
        session_id = None
        if len(sys.argv) >= 3 and sys.argv[2] == "--session":
            if len(sys.argv) >= 4:
                session_id = sys.argv[3]

        shell = ChatShell(session_id=session_id)
        await run_chat_shell(shell)

    elif command == "ilhas":
        await list_ilhas(sys.argv)

    elif command == "dormir":
        await cmd_dormir(sys.argv)

    elif command == "acordar":
        await cmd_acordar(sys.argv)

    elif command == "estado":
        await cmd_estado(sys.argv)

    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    asyncio.run(main())