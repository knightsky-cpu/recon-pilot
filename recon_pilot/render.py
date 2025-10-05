from __future__ import annotations
from pathlib import Path
from typing import Dict, Any
from jinja2 import Environment, FileSystemLoader, select_autoescape
import html

# --- Markdown (Jinja) ---

def render_casefile(template_dir: Path, context: dict) -> str:
    """
    Render the Markdown report from templates/casefile.md.j2.
    The template can now reference 'delta' provided by cli.py.
    """
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(disabled_extensions=("md",))
    )
    tpl = env.get_template("casefile.md.j2")
    return tpl.render(**context)

# --- HTML helpers ---

def render_casefile_html(template_dir: Path, context: Dict[str, Any]) -> str:
    """
    Convert the Jinja-rendered Markdown to HTML.
    Uses the 'markdown' package if present; otherwise falls back to <pre>.
    """
    md = render_casefile(template_dir, context)
    try:
        from markdown import markdown as md_to_html
        body = md_to_html(md, extensions=["fenced_code", "tables"])
    except Exception:
        body = f"<pre>{html.escape(md)}</pre>"

    org = str(context.get("org", ""))
    html_doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>ReconPilot Casefile — {html.escape(org)}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  :root {{ --bg:#0b0e11; --fg:#e6e6e6; --muted:#9aa3ac; --card:#12161c; --accent:#4ea1ff; }}
  html, body {{ background: var(--bg); color: var(--fg); font: 16px/1.6 system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, sans-serif; }}
  a {{ color: var(--accent); }}
  .container {{ max-width: 960px; margin: 2rem auto; padding: 0 1rem; }}
  h1, h2, h3 {{ line-height: 1.25; }}
  table {{ width: 100%; border-collapse: collapse; margin: 1rem 0; }}
  th, td {{ border: 1px solid #2a2f36; padding: .5rem .6rem; }}
  code {{ background: #1a1f26; padding: .15rem .3rem; border-radius: .25rem; }}
  pre code {{ display: block; padding: 1rem; overflow-x: auto; }}
  .muted {{ color: var(--muted); }}
  .card {{ background: var(--card); border: 1px solid #1e242c; border-radius: .75rem; padding: 1rem; }}
</style>
</head>
<body>
  <div class="container">
    {body}
  </div>
</body>
</html>"""
    return html_doc

def write_casefile_html(path: Path, template_dir: Path, context: Dict[str, Any]) -> None:
    """Write the HTML report to disk."""
    html_doc = render_casefile_html(template_dir, context)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html_doc, encoding="utf-8")

