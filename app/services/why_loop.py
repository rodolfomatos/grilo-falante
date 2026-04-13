#!/usr/bin/env python3
"""
Why Loop - Loop de perguntas "porquê?"

O Why Loop é o quarto passo do "Ir à Escola" loop.
Funciona assim:
1. Recebe síntese Feynman
2. Gera perguntas "porquê?"
3. Repete até 3x ou até não haver mais perguntas

Autor: Rodolfo
Data: 2026-04-13
"""

import logging
from typing import List, Optional, Dict
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


@dataclass
class WhyQuestion:
    """Uma pergunta 'porquê?'."""
    question: str
    depth: int        # 1, 2, 3
    status: str       # "pending", "answered", "dropped"


class WhyLoop:
    """
    Loop de perguntas "porquê?".
    
    Estratégia:
    - Para cada afirmação,pergunte "mas porquê?"
    - Até 3 iterações
    - Ou até não haver mais perguntas legítimas
    
    Perguntas de exemplo:
    "Mas porquê?" → "Porque X"
    "E como sabemos que X?" → "Porque Y"
    "E Y é sempre verdade?" → ?
    """
    
    # Templates de perguntas por profundidade
    QUESTION_TEMPLATES = [
        # Depth 1
        "Mas porquê?",
        "Porque é que {topic}?",
        "O que faz {topic} ser assim?",
        
        # Depth 2
        "E como sabemos que isso é verdade?",
        "Qual é a evidência para isso?",
        "Existe exceção?",
        
        # Depth 3
        "E se a exceção for verdade?",
        "Há alguma teoria rival?",
        "O que acontece quando não se cumpre?",
    ]
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.max_depth = 3
        
    def generate_why_questions(
        self,
        synthesis_content: str,
        topic: str,
        current_depth: int = 1
    ) -> List[WhyQuestion]:
        """
        Gera perguntas "porquê?" para uma síntese.
        
        Args:
            synthesis_content: O conteúdo da síntese
            topic: O tema base
            current_depth: Profundidade atual
            
        Returns:
            Lista de WhyQuestion objects
        """
        if current_depth > self.max_depth:
            return []
        
        questions = []
        
        # Simple heuristic: find key claims
        import re
        
        # Extrai afirmações-chave
        claims = re.findall(
            r'([^.]+(?:é|foi|foi|cria|descobre)[^.]+\.)',
            synthesis_content
        )
        
        if not claims:
            # Fallback: generic why
            questions.append(WhyQuestion(
                question=f"Mas porquê? O que acontece se não for verdade?",
                depth=current_depth,
                status="pending"
            ))
            return questions
                
        # Generate questions for each claim
        for i, claim in enumerate(claims[:3]):
            if current_depth == 1:
                question_text = f"Mas porquê? ({claim[:50]}...)"
            elif current_depth == 2:
                question_text = f"E como sabemos que isso é verdade?"
            else:
                question_text = f"Há alguma exceção?"
            
            questions.append(WhyQuestion(
                question=question_text,
                depth=current_depth,
                status="pending"
            ))
            
        return questions
    
    def run_loop(
        self,
        synthesis,
        topic: str,
        max_iterations: int = 3
    ) -> Dict:
        """
        Run the full "porquê?" loop.
        
        Args:
            synthesis: FeynmanSynthesis object
            topic: O tema
            max_iterations: Máximo de iterações
            
        Returns:
            Dict com:
            - questions: Lista de perguntas
            - answers: Respostas encontradas
            - final_depth: Profundidade alcançada
            - status: "complete" ou "incomplete"
        """
        logger.info(f"Starting why loop for: {topic}")
        
        all_questions = []
        iteration = 0
        current_content = synthesis.for_expert
        
        while iteration < max_iterations:
            # Generate why questions
            questions = self.generate_why_questions(
                current_content,
                topic,
                iteration + 1
            )
            
            if not questions:
                break
                
            all_questions.extend(questions)
            
            # Check if we should continue
            # Por agora,simplificado: sempre parar após 1 iteração
            # (em produção, usaria LLM para validar)
            break
            
        return {
            "questions": [
                {"q": q.question, "depth": q.depth, "status": q.status}
                for q in all_questions
            ],
            "final_depth": iteration + 1,
            "status": "complete"
        }
    
    def format_why_output(self, loop_result: Dict) -> str:
        """Formata output para mostrar ao utilizador."""
        if not loop_result.get("questions"):
            return "Nenhuma pergunta gerada."
        
        lines = ["**Perguntas de Profundidade:**"]
        
        for item in loop_result["questions"]:
            depth = item["depth"]
            q = item["q"]
            lines.append(f"\n{depth}. {q}")
        
        return "\n".join(lines)


def demo():
    """Demo do WhyLoop."""
    print("=" * 60)
    print("WHY LOOP - Demo")
    print("=" * 60)
    
    from feynman_synthesize import FeynmanSynthesizer, FeynmanSynthesis
    
    synth = FeynmanSynthesizer()
    
    test = {
        "gap": "Alan Turing",
        "results": [
            {
                "content": "Alan Turing foi um matemático inglês que criou a máquina de Turing. Morreu em 1954.",
                "source": "wikipedia"
            }
        ]
    }
    
    synthesis = synth.synthesize(test["gap"], test["results"])
    
    loop = WhyLoop()
    result = loop.run_loop(synthesis, test["gap"])
    
    print(f"Topic: {test['gap']}")
    print(f"Questions: {result['questions']}")
    print(f"Final depth: {result['final_depth']}")
    print(f"\nFormatted:")
    print(loop.format_why_output(result))


if __name__ == "__main__":
    demo()