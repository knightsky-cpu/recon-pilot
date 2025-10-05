# ReconPilot v0 — Passive-first Recon Autopilot (Safety-First)

> **Purpose**: Turn mundane recon into a safe, repeatable, *passive-first* workflow that produces a clean **casefile.md** with clear next steps.  
> **Ethics**: For **authorized** use only. Scope is strictly enforced by `scope.yaml`.

## Features (v0)
- **Scope guard**: refuses out-of-scope targets.
- **Passive modules**: CT logs (crt.sh), DNS (A/AAAA/CNAME/MX/TXT/NS) lookups.
- **Explainable findings**: each item includes *why it matters* and suggested, approval-gated **next steps**.
- **Evidence pack**: JSON artifacts + Markdown report.
- **Changefeed**: simple diff between runs.

## Quickstart
```bash
# 1) Create and activate a venv (recommended)
python3 -m venv .venv && source .venv/bin/activate

# 2) Install
pip install -e .

# 3) Copy & edit scope
cp fixtures/scope.example.yaml scope.yaml
# -> edit org/domains, notes; keep it authorized!

# 4) Run (passive-only)
recon-pilot run --scope scope.yaml --out runs

# 5) Open your casefile
ls runs/*/casefile.md
```

## Safety & Ethics
- **Passive-first**: v0 only queries public data sources and DNS. No active scanning.  
- **Scope.yaml** is the law: domains outside scope are ignored.  
- Logs/artifacts are stored locally by default. You own your data.

## Roadmap
- Weekly scheduled runs + diffs
- Optional **active** checks with explicit `--allow-active` flag and rate limits
- HTTP header/tech fingerprint module
- Integrations: Amass, Nuclei, Shodan/Censys (with user-provided keys)
- HTML/PDF export and SARIF/STIX emitters
