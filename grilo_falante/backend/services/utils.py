"""
Utilities - Timeout, Retry, HTML Export

Features from prototype:
- Timeout handling with signal.SIGALRM
- Retry decorator with exponential backoff
- HTML export for dashboard visualization
"""

import functools
import signal
import time
from typing import Callable, Any, Optional, List, Dict
from pathlib import Path
from dataclasses import dataclass


class TimeoutError(Exception):
    """Raised when an operation times out."""
    pass


@dataclass
class RetryResult:
    success: bool
    result: Any
    attempts: int
    total_time: float
    error: Optional[str] = None


def timeout_handler(signum, frame):
    raise TimeoutError("Operation timed out")


def with_timeout(seconds: int):
    """
    Decorator that applies timeout to a function using signal.SIGALRM.

    Usage:
        @with_timeout(30)
        def my_function():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                signal.alarm(0)
        return wrapper
    return decorator


def with_retry(
    max_retries: int = 3,
    backoff_factor: float = 1.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator that retries a function on failure with exponential backoff.

    Usage:
        @with_retry(max_retries=3, backoff_factor=2.0)
        def my_function():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        sleep_time = backoff_factor * (2 ** (attempt - 1))
                        time.sleep(sleep_time)
            raise last_exception
        return wrapper
    return decorator


def retry_operation(
    func: Callable,
    *args,
    max_retries: int = 3,
    backoff_factor: float = 1.0,
    **kwargs
) -> RetryResult:
    """
    Execute an operation with retry logic.

    Returns RetryResult with success status, result, attempts, and timing.
    """
    import time
    start_time = time.time()
    last_exception = None

    for attempt in range(1, max_retries + 1):
        try:
            result = func(*args, **kwargs)
            return RetryResult(
                success=True,
                result=result,
                attempts=attempt,
                total_time=time.time() - start_time
            )
        except Exception as e:
            last_exception = e
            if attempt < max_retries:
                sleep_time = backoff_factor * (2 ** (attempt - 1))
                time.sleep(sleep_time)

    return RetryResult(
        success=False,
        result=None,
        attempts=max_retries,
        total_time=time.time() - start_time,
        error=str(last_exception)
    )


def export_html(
    nodes: List[Dict],
    edges: List[Dict],
    output_path: str = "graphify-out/grilo_graph.html",
    title: str = "Grilo Falante Dashboard"
) -> str:
    """
    Export claims as an interactive HTML dashboard.

    Features:
    - GMIF color-coded badges (M1-M7)
    - Search/filter functionality
    - Summary statistics
    - Verification status indicators
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    by_type: Dict[str, int] = {}
    for n in nodes:
        t = n.get("gmif_type", n.get("gmif_level", "M3"))
        if isinstance(t, str) and t.startswith("M"):
            by_type[t] = by_type.get(t, 0) + 1

    type_colors = {
        "M1": "#4CAF50",
        "M2": "#FFC107",
        "M3": "#FF9800",
        "M4": "#F44336",
        "M5": "#8BC34A",
        "M6": "#03A9F4",
        "M7": "#9C27B0",
    }

    type_badges = "".join(
        f'<div class="card"><span class="badge" style="background:{type_colors.get(t, "#999")}">{t}</span> = <strong>{c}</strong></div>'
        for t, c in sorted(by_type.items())
    )

    node_cards = ""
    for n in nodes:
        t = n.get("gmif_type", n.get("gmif_level", "M3"))
        color = type_colors.get(t, "#999")
        v = n.get("verified", False)
        label = (n.get("label", "") or n.get("claim_text", "") or "")[:100]
        gf_id = n.get("gf_id", n.get("claim_key", ""))

        node_cards += f'''<div class="card" data-search="{label.lower()}">
<span class="badge" style="background:{color}">{t}</span>
{"<span class='verified'>✓</span>" if v else ""}
<br><small>{gf_id}</small>
<p>{label}</p>
</div>'''

    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>{title}</title>
<style>
body{{font-family:-apple-system,BlinkMacSystemFont,sans-serif;margin:0;padding:20px;background:#fafafa}}
h1{{color:#333;display:flex;align-items:center;gap:10px}}
h3{{margin-top:20px}}
.badge{{display:inline-block;padding:2px 8px;border-radius:4px;font-size:12px;color:#fff}}
.stats{{background:#fff;padding:20px;border-radius:8px;margin:20px 0;box-shadow:0 2px 4px rgba(0,0,0,0.1)}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:15px;margin:20px 0}}
.card{{background:#fff;padding:15px;border-radius:8px;box-shadow:0 2px 4px rgba(0,0,0,0.1)}}
.verified{{color:#4CAF50;font-weight:bold}}
.warning{{color:#F44336;font-weight:bold}}
.search{{padding:10px;border:2px solid #ddd;border-radius:8px;width:100%;font-size:16px;box-sizing:border-box}}
button{{padding:10px 20px;border:none;background:#007bff;color:#fff;border-radius:4px;cursor:pointer}}
button:hover{{background:#0056b3}}
</style></head>
<body>
<h1>📊 {title} <button onclick="location.reload()">↻ Refresh</button></h1>
<input class="search" id="search" placeholder="Search claims..." oninput="filter()">
<div class="stats">
<h3>Summary</h3>
<p>Total Nodes: <strong>{len(nodes)}</strong></p>
<p>Total Edges: <strong>{len(edges)}</strong></p>
</div>
<h3>By GMIF Type</h3>
<div class="grid">
{type_badges or '<p>No classifications yet.</p>'}
</div>
<h3>Claims</h3>
<div class="grid" id="grid">
{node_cards or '<p>No claims yet.</p>'}
</div>
<script>
function filter(){{
var q=document.getElementById("search").value.toLowerCase();
document.querySelectorAll(".card").forEach(function(c){{
c.style.display=q&&c.dataset.search.indexOf(q)<0?"none":"block"}});
}}
</script>
</body></html>"""

    output_path.write_text(html)
    return str(output_path)