from __future__ import annotations
import typer
from pathlib import Path
from datetime import datetime
from rich.console import Console
from typing import Set
from collections import Counter

from .scope import Scope
from .modules.ct import fetch_ct_domains
from .modules.dns import query_dns
from .render import render_casefile
from .rules_loader import load_rules
from .utils import write_json, read_json

app = typer.Typer(help="ReconPilot v0 — Passive-first recon autopilot")

console = Console()

def _stamp() -> str:
    return datetime.utcnow().strftime("%Y%m%d-%H%M%SZ")

@app.command()
def run(
    scope: Path = typer.Option(..., exists=True, readable=True, help="Path to scope.yaml"),
    out: Path = typer.Option(Path("runs"), help="Output directory base"),
    tag: str = typer.Option("", help="Optional run tag, appended to run folder name"),
):
    """Run passive recon against the defined scope."""
    scope_obj = Scope.load(str(scope))
    run_dir = out / f"run-{_stamp()}{('-' + tag) if tag else ''}"
    artifacts_dir = run_dir / "artifacts"
    run_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    console.rule("ReconPilot v0 — Passive run") 
    console.print(f"[bold]Org:[/] {scope_obj.org}")
    console.print(f"[bold]Domains:[/] {', '.join(scope_obj.domains)}\n")


    all_hosts: Set[str] = set()

    # 1) CT discovery
    for base in scope_obj.domains:
        console.print(f"[cyan]ct:[/] querying crt.sh for {base}...")
        hosts = fetch_ct_domains(base)
        hosts = [h for h in hosts if scope_obj.in_scope_domain(h)]
        console.print(f"  found {len(hosts)} hosts in-scope")
        write_json(artifacts_dir / f"ct_{base}.json", hosts)
        all_hosts.update(hosts)

    # Include seed hosts from scope.yaml (filtered to in-scope)
    seed_hosts = {h.strip().lower() for h in scope_obj.seeds.get("hosts", []) if h.strip()}
    seed_hosts = {h for h in seed_hosts if scope_obj.in_scope_domain(h)}
    all_hosts.update(seed_hosts)
    write_json(artifacts_dir / "seed_hosts.json", sorted(list(seed_hosts)))

    all_hosts = sorted(all_hosts)
    write_json(artifacts_dir / "inventory_hosts.json", all_hosts)

    # 2) DNS records
    inventory = []
    dns_issues = []
    for h in all_hosts:
        recs = query_dns(h, scope_obj.resolvers)
        inventory.append({"host": h, "records": recs})
        # simple heuristics for potential dangling CNAMEs
        if any(v for v in recs.get("CNAME", []) if any(s in v.lower() for s in ["amazonaws.com","github.io","herokuapp.com","azurewebsites.net"])):
            dns_issues.append({"host": h, "type": "dangling_cname_potential", "evidence": recs.get("CNAME", [])})
    write_json(artifacts_dir / "dns_records.json", inventory)
    write_json(artifacts_dir / "dns_issues.json", dns_issues)

    # 3) Findings: map to rules/explanations
    rules = load_rules(Path(__file__).parent / "rules" / "recon_rules.yaml")
    findings = []

    # wildcard exposure hint (naive): if many subdomains for a base
    counts = Counter([h.split(".", maxsplit=1)[1] if "." in h else h for h in all_hosts])
    for base, cnt in counts.items():
        if cnt >= 30 and base in scope_obj.domains:
            rule = rules["findings"].get("wildcard_cert",{})
            findings.append({
                "title": "Potential Wildcard Exposure",
                "asset": base,
                "why": rule.get("why",""),
                "evidence": f"{cnt} subdomains observed in CT for {base}",
                "next_steps": rule.get("next_steps",[])
            })

    for issue in dns_issues:
        rule = rules["findings"].get("dangling_cname",{})
        findings.append({
                "title": "Potential Dangling CNAME",
                "asset": issue["host"],
                "why": rule.get("why",""),
                "evidence": ", ".join(issue.get("evidence",[])),
                "next_steps": rule.get("next_steps",[])
        })

    # Inventory summary lines
    inv_summary = []
    for item in inventory:
        host = item["host"]
        recs = item["records"]
        summary_bits = []
        for rt in ["A","AAAA","CNAME","MX","TXT","NS"]:
            if recs.get(rt):
                summary_bits.append(f"{rt}:{len(recs[rt])}")
        inv_summary.append({"host": host, "records_summary": ", ".join(summary_bits) if summary_bits else "(no records)"})

    # 4) Compute simple stats
    stats = {
        "total_subdomains": len(all_hosts),
        "new_subdomains": len(all_hosts),  # placeholder until 'diff' is integrated into run
        "dns_issues": dns_issues,
    }

    # 5) Render casefile
    context = {
        "org": scope_obj.org,
        "run_time": datetime.utcnow().isoformat() + "Z",
        "scope_domains": scope_obj.domains,
        "stats": stats,
        "findings": findings,
        "inventory": inv_summary,
    }
    report_md = render_casefile(Path(__file__).parent / "templates", context)
    with open(run_dir / "casefile.md", "w", encoding="utf-8") as f:
        f.write(report_md)

    console.print(f"\n[green]✔[/] Wrote artifacts → {artifacts_dir}")
    console.print(f"[green]✔[/] Wrote report → {run_dir / 'casefile.md'}")

@app.command()
def diff(
    a: Path = typer.Option(..., exists=True, help="Path to older run dir"),
    b: Path = typer.Option(..., exists=True, help="Path to newer run dir"),
    out: Path = typer.Option(Path("diff.md"), help="Output markdown path"),
):
    """Diff two runs to see what's new/removed."""
    hosts_a = set(read_json(a / "artifacts" / "inventory_hosts.json"))
    hosts_b = set(read_json(b / "artifacts" / "inventory_hosts.json"))
    new = sorted(list(hosts_b - hosts_a))
    gone = sorted(list(hosts_a - hosts_b))

    lines = ["# ReconPilot Diff\n"]
    lines.append(f"**New hosts:** {len(new)}\n")
    for h in new: lines.append(f"- `{h}`\n")
    lines.append("\n")
    lines.append(f"**Removed hosts:** {len(gone)}\n")
    for h in gone: lines.append(f"- `{h}`\n")

    with open(out, "w", encoding="utf-8") as f:
        f.writelines(lines)

    console.print(f"[green]✔[/] Wrote diff → {out}")

if __name__ == "__main__":
    app()
