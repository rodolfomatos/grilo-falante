#!/usr/bin/env python3
"""
State Machine Engine for Grilo Falante
======================================
Parses .dot files and executes as state machine.

Usage:
    from state_machine import DotParser, StateMachine
    
    parser = DotParser("g7_grilo_falante_cognitive_model_v7.dot")
    states, transitions = parser.parse()
    
    sm = StateMachine(states, transitions)
    result = sm.run(initial_input)
"""

import re
import json
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from pathlib import Path
from enum import Enum


class TransitionType(Enum):
    NORMAL = "normal"
    ACCEPT = "accept"
    REJECT = "reject"
    REEXECUTE = "reexecute"
    PROMOTE = "promote"
    BLOCK = "block"


@dataclass
class State:
    name: str
    label: str
    is_entry: bool = False
    is_exit: bool = False
    is_decision: bool = False
    metadata: Dict = field(default_factory=dict)


@dataclass
class Transition:
    from_state: str
    to_state: str
    label: Optional[str] = None
    transition_type: TransitionType = TransitionType.NORMAL
    condition: Optional[str] = None
    is_forbidden: bool = False


@dataclass
class StateMachineResult:
    current_state: str
    output: Any
    accepted: bool
    rejected: bool
    reexecute: bool
    blocked: bool
    history: List[Dict]
    error: Optional[str] = None


class DotParser:
    """Parser for Graphviz .dot files."""
    
    def __init__(self, dot_path: str):
        self.dot_path = Path(dot_path)
        self.states: Dict[str, State] = {}
        self.transitions: List[Transition] = []
        
    def parse(self) -> tuple:
        """Parse .dot file and return (states, transitions)."""
        if not self.dot_path.exists():
            raise FileNotFoundError(f"Dot file not found: {self.dot_path}")
        
        content = self.dot_path.read_text()
        
        # Parse states (nodes)
        self._parse_nodes(content)
        
        # Parse transitions (edges)
        self._parse_edges(content)
        
        return self.states, self.transitions
    
    def _parse_nodes(self, content: str):
        """Extract nodes from dot file."""
        node_pattern = r'(\w+)\s*\[([^\]]*)\]'
        
        for match in re.finditer(node_pattern, content):
            node_id = match.group(1)
            attrs_str = match.group(2)
            
            # Extract label
            label_match = re.search(r'label="([^"]*)"', attrs_str)
            label = label_match.group(1) if label_match else node_id
            
            # Check shape for decision points
            is_decision = 'shape=diamond' in attrs_str
            
            # Check for entry/exit points
            is_entry = node_id in ['F_M1', 'F0', 'ACORDAR', 'USER']
            is_exit = node_id in ['F8', 'ARTIFACTS']
            
            self.states[node_id] = State(
                name=node_id,
                label=label,
                is_entry=is_entry,
                is_exit=is_exit,
                is_decision=is_decision
            )
    
    def _parse_edges(self, content: str):
        """Extract edges from dot file."""
        
        # Remove comments first
        content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        
        # Handle multi-edge chains: A -> B -> C -> D;
        # Expand to individual edges
        chain_pattern = r'(\w+)\s*->\s*(\w+)\s*(?:->\s*(\w+)\s*)*;'
        
        # Replace chains with individual edges
        def expand_chain(match):
            nodes = re.findall(r'\w+', match.group(0))
            # Remove duplicates and keep sequential pairs
            result = []
            for i in range(len(nodes) - 1):
                result.append(f"{nodes[i]} -> {nodes[i+1]};")
            return "\n".join(result)
        
        content = re.sub(r'(\w+)\s*->\s*(\w+)\s*(?:->\s*\w+\s*)+;', expand_chain, content)
        
        # Now parse individual edges
        edge_pattern = r'(\w+)\s*->\s*(\w+)(?:\s*\[([^\]]*)\])?'
        
        for match in re.finditer(edge_pattern, content):
            from_state = match.group(1)
            to_state = match.group(2)
            attrs_str = match.group(3) if match.group(3) else ""
            
            # Skip if this was part of a chain (already processed)
            chain_match = re.search(r'(\w+)\s*->\s*(\w+)\s*->', attrs_str + " " + content[match.start():match.end()+50])
            if chain_match:
                continue
            
            # Extract label
            label_match = re.search(r'label="([^"]*)"', attrs_str)
            label = label_match.group(1) if label_match else None
            
            # Determine transition type
            transition_type = TransitionType.NORMAL
            is_forbidden = False
            
            if label:
                upper_label = label.upper()
                if 'FORBIDDEN' in upper_label:
                    is_forbidden = True
                elif 'ACCEPT' in upper_label:
                    transition_type = TransitionType.ACCEPT
                elif 'REJECT' in upper_label:
                    transition_type = TransitionType.REJECT
                elif 'REEXECUTE' in upper_label:
                    transition_type = TransitionType.REEXECUTE
                elif 'PROMOTE' in upper_label:
                    transition_type = TransitionType.PROMOTE
                elif 'BLOCK' in upper_label:
                    transition_type = TransitionType.BLOCK
            
            self.transitions.append(Transition(
                from_state=from_state,
                to_state=to_state,
                label=label,
                transition_type=transition_type,
                is_forbidden=is_forbidden
            ))
    
    def get_entry_state(self) -> Optional[str]:
        """Get the entry state."""
        # Try F_M1, F0, ACORDAR, USER in order
        for candidate in ['F_M1', 'F0', 'ACORDAR', 'USER']:
            if candidate in self.states:
                return candidate
        return list(self.states.keys())[0] if self.states else None
    
    def to_json(self) -> str:
        """Export to JSON."""
        return json.dumps({
            "states": {k: {"name": v.name, "label": v.label} for k, v in self.states.items()},
            "transitions": [
                {"from": t.from_state, "to": t.to_state, "label": t.label, "type": t.transition_type.value}
                for t in self.transitions
            ]
        }, indent=2)


class StateMachine:
    """State machine engine."""
    
    def __init__(self, states: Dict[str, State], transitions: List[Transition]):
        self.states = states
        self.transitions = transitions
        self.current_state: Optional[str] = None
        self.history: List[Dict] = []
        self.handlers: Dict[str, Callable] = {}
        
        # Build transition lookup
        self._transitions_by_from: Dict[str, List[Transition]] = {}
        for t in transitions:
            if t.from_state not in self._transitions_by_from:
                self._transitions_by_from[t.from_state] = []
            self._transitions_by_from[t.from_state].append(t)
    
    def set_handler(self, state: str, handler: Callable):
        """Register a handler for a state."""
        self.handlers[state] = handler
    
    def start(self, initial_state: Optional[str] = None):
        """Start the state machine."""
        if initial_state:
            self.current_state = initial_state
        else:
            # Find entry state - prefer F_M1, then F0, then others
            for state_name in ['F_M1', 'F0', 'ACORDAR', 'USER']:
                if state_name in self.states:
                    self.current_state = state_name
                    break
        
        if not self.current_state:
            raise ValueError("No entry state found")
        
        self.history = [{"state": self.current_state, "action": "START"}]
        return self.current_state
    
    def step(self, input_data: Any = None, context: Dict = None) -> StateMachineResult:
        """Execute one step."""
        context = context or {}
        
        if not self.current_state:
            return StateMachineResult(
                current_state="NONE",
                output=None,
                accepted=False,
                rejected=False,
                reexecute=False,
                blocked=True,
                history=self.history,
                error="No current state"
            )
        
        state = self.states.get(self.current_state)
        
        # Execute handler if exists
        output = None
        if self.current_state in self.handlers:
            try:
                handler = self.handlers[self.current_state]
                output = handler(input_data, context)
            except Exception as e:
                print(f"[ERROR] Handler for {self.current_state} failed: {e}", file=sys.stderr)
                return StateMachineResult(
                    current_state=self.current_state,
                    output=None,
                    accepted=False,
                    rejected=False,
                    reexecute=False,
                    blocked=True,
                    history=self.history,
                    error=str(e)
                )
        
        # Find next transition
        next_transition = self._find_transition(output, context)
        
        if next_transition is None:
            # No valid transition - blocked
            self.history.append({
                "state": self.current_state,
                "action": "BLOCKED",
                "reason": "No valid transition"
            })
            return StateMachineResult(
                current_state=self.current_state,
                output=output,
                accepted=False,
                rejected=False,
                reexecute=False,
                blocked=True,
                history=self.history
            )
        
        # Check forbidden transitions
        if next_transition.is_forbidden:
            self.history.append({
                "state": self.current_state,
                "action": "BLOCKED",
                "reason": f"Forbidden transition: {next_transition.from_state} -> {next_transition.to_state}"
            })
            return StateMachineResult(
                current_state=self.current_state,
                output=output,
                accepted=False,
                rejected=False,
                reexecute=False,
                blocked=True,
                history=self.history,
                error="Forbidden transition"
            )
        
        # Move to next state
        old_state = self.current_state
        self.current_state = next_transition.to_state
        
        self.history.append({
            "state": old_state,
            "next": self.current_state,
            "transition": next_transition.label,
            "type": next_transition.transition_type.value
        })
        
        # Determine result
        accepted = next_transition.transition_type == TransitionType.ACCEPT
        rejected = next_transition.transition_type == TransitionType.REJECT
        reexecute = next_transition.transition_type == TransitionType.REEXECUTE
        blocked = next_transition.transition_type == TransitionType.BLOCK
        
        return StateMachineResult(
            current_state=self.current_state,
            output=output,
            accepted=accepted,
            rejected=rejected,
            reexecute=reexecute,
            blocked=blocked,
            history=self.history
        )
    
    def _find_transition(self, output: Any, context: Dict) -> Optional[Transition]:
        """Find the appropriate next transition based on output."""
        available = self._transitions_by_from.get(self.current_state, [])
        
        # Handle dict output with explicit "next" state
        if isinstance(output, dict):
            explicit_next = output.get("next")
            if explicit_next:
                # Find transition to explicit next state
                for t in available:
                    if t.to_state == explicit_next:
                        return t
                # If no direct transition, create implicit one (for GATES -> F_M1)
                return Transition(
                    from_state=self.current_state,
                    to_state=explicit_next,
                    label="implicit",
                    transition_type=TransitionType.NORMAL
                )
            
            # Check for terminal statuses
            status = output.get("status", "").upper()
            if status == "ACCEPT":
                for t in available:
                    if t.transition_type == TransitionType.ACCEPT:
                        return t
            elif status == "REJECT":
                for t in available:
                    if t.transition_type == TransitionType.REJECT:
                        return t
            elif status == "REEXECUTE":
                for t in available:
                    if t.transition_type == TransitionType.REEXECUTE:
                        return t
            elif status == "PROMOTE":
                for t in available:
                    if t.transition_type == TransitionType.PROMOTE:
                        return t
            elif status == "BLOCK":
                for t in available:
                    if t.transition_type == TransitionType.BLOCK:
                        return t
        
        # If no handler output, try normal transition
        if output is None:
            # Return first non-forbidden transition
            for t in available:
                if not t.is_forbidden:
                    return t
            return None
        
        # If output is a dict with status "continue" or "DONE", use default transition
        if isinstance(output, dict):
            status = output.get("status", "").upper()
            if status in ("CONTINUE", "DONE"):
                # Find first non-forbidden transition
                for t in available:
                    if not t.is_forbidden:
                        return t
                # If no available transitions, we're at a terminal - return None to trigger blocked
                return None
        
        # Use output to determine transition
        # Common patterns: "ACCEPT", "REJECT", "REEXECUTE", "PROMOTE", "BLOCK"
        output_upper = str(output).upper()
        
        for t in available:
            if t.label and output_upper in t.label.upper():
                return t
        
        # Default: return first non-forbidden
        for t in available:
            if not t.is_forbidden:
                return t
        
        return None
    
    def run(self, initial_input: Any = None, max_steps: int = 100) -> StateMachineResult:
        """Run until terminal state."""
        step_count = 0
        
        while step_count < max_steps:
            result = self.step(initial_input)
            
            # Check terminal conditions
            if result.accepted or result.rejected or result.blocked:
                return result
            
            # Check if we've reached an exit state
            if self.current_state in self.states:
                state = self.states[self.current_state]
                if state.is_exit:
                    return result
            
            step_count += 1
        
        return StateMachineResult(
            current_state=self.current_state,
            output=None,
            accepted=False,
            rejected=False,
            reexecute=False,
            blocked=True,
            history=self.history,
            error="Max steps exceeded"
        )


def load_graph(graph_name: str, graphs_dir: str = None) -> StateMachine:
    """Load a graph by name and return a StateMachine."""
    if graphs_dir is None:
        graphs_dir = Path(__file__).parent / "graphs"
    else:
        graphs_dir = Path(graphs_dir)
    
    dot_file = graphs_dir / f"{graph_name}.dot"
    
    if not dot_file.exists():
        # Try in ambrosio
        ambrosio_graphs = Path("/home/rodolfo/src/ambrosio_v2.5.0/graphs")
        dot_file = ambrosio_graphs / f"{graph_name}.dot"
    
    if not dot_file.exists():
        raise FileNotFoundError(f"Graph not found: {graph_name}")
    
    parser = DotParser(str(dot_file))
    states, transitions = parser.parse()
    return StateMachine(states, transitions)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        graph_name = sys.argv[1]
        sm = load_graph(graph_name)
        print(f"Loaded: {graph_name}")
        print(f"States: {len(sm.states)}")
        print(f"Transitions: {len(sm.transitions)}")
        print(f"Entry: {sm.start()}")
        print(sm.states)
    else:
        # Test with g7
        sm = load_graph("g7_grilo_falante_cognitive_model_v7")
        print(f"States: {list(sm.states.keys())}")
        print(f"Transitions: {len(sm.transitions)}")
        sm.start()
        print(f"Started at: {sm.current_state}")