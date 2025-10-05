from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

def render_casefile(template_dir: Path, context: dict) -> str:
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(disabled_extensions=("md",))
    )
    tpl = env.get_template("casefile.md.j2")
    return tpl.render(**context)
