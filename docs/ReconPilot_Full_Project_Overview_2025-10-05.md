# ReconPilot — Full Project Overview (as of 2025-10-05)

## Purpose & focus
ReconPilot is a **passive-first, scope-aware recon helper**. It gathers Certificate Transparency (CT) and DNS data strictly within a declared `scope.yaml`, then produces **explainable, evidence-backed** Markdown/HTML reports that are suitable for weekly change-tracking and safe by default (no active scanning). fileciteturn0file4

## Repo & identity (established for handoffs)
- **GitHub user:** `knightsky-cpu`  
- **Repository:** `recon-pilot`  
- **URL:** https://github.com/knightsky-cpu/recon-pilot  
- **Default branch:** `main`  
- **Latest tag:** `v0.2.0` (kept as the “release” snapshot)  
- **Latest commit on main:** `4646c23` (adds interactive `-i` run mode)  
These are the canonical values to reuse in future sessions unless we explicitly change them. fileciteturn0file1

## What it does today
**Passive recon pipeline**
1) Pulls CT data from crt.sh (now resilient with retries/timeouts/UA).  
2) Merges **seed hosts** (from YAML or prompted input).  
3) Performs DNS queries (A/AAAA/CNAME/MX/TXT/NS) using chosen resolvers.  
4) Applies lightweight rules (e.g., wildcard hints, potential dangling CNAME).  
5) Saves artifacts under each run directory.  
6) Writes **casefile.md** and **casefile.html**.  
7) Computes **delta vs. previous run** (new/removed hosts). fileciteturn0file1

**Recent improvements (since the reset)**
- **Interactive run mode** (`-i`) prompts for org, domains, seeds, resolvers, and notes.  
- **Scope loader** accepts both **top-level** (`domains:`) and **nested** (`scope.domains`) schemas.  
- **Timezone-aware UTC** timestamps (future-proof for Python updates).  
- Hardened **CT client** (retries/timeouts, safe failure → empty list). fileciteturn0file0

## Current state & decisions
- Project was hard-reset to **v0.2.0**; “Prep & Polish” artifacts and the CI workflow were removed.  
- The **v0.2.0 tag stays frozen**; ongoing work continues on **main**.  
- **Passive-only** remains the default posture.  
- Prefer **top-level** `scope.yaml`; loader still supports nested layouts. fileciteturn0file0

## Outputs & layout (per run)
```
runs/run-YYYYMMDD-HHMMSSZ-<tag>/
  artifacts/ct_<domain>.json
  artifacts/seed_hosts.json
  artifacts/dns_records.json
  artifacts/dns_issues.json
  artifacts/inventory_hosts.json
  artifacts/delta.json
  casefile.md
  casefile.html
```
This structure underpins repeatability and easy diffing across runs. fileciteturn0file1


## Setup & helper scripts (repo root)
The project includes convenience scripts in the repository root so you can get running quickly on any machine:

```
./recon
./setup_venv.sh
./requirements.txt
```

### `setup_venv.sh` — quick automated virtualenv
- **Run from the repo root:** `./setup_venv.sh`  
- **Virtualenv location:** uses `$VENV` if set, otherwise defaults to `.venv`.  
- **What it does:** checks `python3` and `python3-venv`, creates/updates the venv, and installs Python packages from `requirements.txt`. If the file is missing, it installs the core dependencies directly (Typer, Rich, Jinja2, PyYAML, Requests, dnspython, Markdown).  
- **After it finishes:** activate with `source .venv/bin/activate` (or `source "$VENV"/bin/activate` if you set `VENV`).  
- **Dependencies from `requirements.txt`:** `typer>=0.12`, `rich>=13.0`, `jinja2>=3.1`, `PyYAML>=6.0`, `requests>=2.31`, `dnspython>=2.4`, `markdown>=3.5`. fileciteturn1file0

> Tip: you can override the env directory per-run: `VENV=$HOME/.virtualenvs/reconpilot ./setup_venv.sh`

### `recon` — smart launcher + auto-venv helper
- **Global-friendly:** resolves its own location even when symlinked, so you can link it into `~/.local/bin` (done on your system already).  
- **Auto-venv behavior:** if the expected venv isn’t available, it will run the setup script and then invoke the CLI with the venv’s Python.  
- **Doctor passthrough:** `recon doctor` runs a diagnostic report immediately. (Note: `recon doctor --help` is not a separate help screen; it executes the checks.)  
- **CLI entrypoint:** ultimately executes `python -m recon_pilot.cli ...` under the venv.

### Fresh-clone bootstrap (example)
```bash
git clone https://github.com/knightsky-cpu/recon-pilot
cd recon-pilot
chmod +x recon setup_venv.sh
./setup_venv.sh
recon doctor
```

## Environment & ergonomics
- `.env.recon` tunables for CT: `RECON_CT_TIMEOUT`, `RECON_CT_RETRIES`, `RECON_CT_SLEEP`, `RECON_CT_UA`.  
- On this system, `sensible-browser` is more reliable than `xdg-open` for opening HTML reports. fileciteturn0file0

## Quick commands (resume-friendly)
```bash
# Interactive run (prompts for org/domains/seeds/resolvers/notes)
recon run -i --out runs --tag lab1

# Run with a YAML scope file
recon run --scope scope.yaml --out runs --tag nightly

# Open the newest HTML casefile (uses sensible-browser)
firefox --new-window "$(ls -td runs/* | head -n1)/casefile.html"

# Environment/health check
recon doctor

# Diff two runs -> diff.md
recon diff --a runs/<older-run> --b runs/<newer-run> --out diff.md
```
fileciteturn0file1

## Global availability
`recon` is on your **PATH**, so you can run it from anywhere.

### Project‑local runs (writes `./runs` in the current directory)
```bash
# Interactive flow
recon run -i --out runs --tag lab1

# Use a scope file in the current directory
recon run --scope ./scope.yaml --out runs --tag nightly

# Open the newest HTML casefile (Firefox, new window)
firefox --new-window "$(ls -td runs/* | head -n1)/casefile.html"

# Diff the last two runs in this folder → diff.md
recon diff --a "$(ls -td runs/* | sed -n '2p')"            --b "$(ls -td runs/* | sed -n '1p')"            --out diff.md

# Health check
recon doctor
```

### Centralized runs (optional; always write under one directory)
```bash
# Choose a central place for all runs
export RUNS_ROOT="$HOME/ReconPilot-runs"
mkdir -p "$RUNS_ROOT"

# Interactive run → writes to $RUNS_ROOT
recon run -i --out "$RUNS_ROOT" --tag lab1

# Scope-file run (absolute path recommended)
recon run --scope "$HOME/Projects/ReconPilot-v0/scope.yaml" --out "$RUNS_ROOT" --tag nightly

# Open newest casefile from the central runs directory
firefox --new-window "$(ls -td "$RUNS_ROOT"/* | head -n1)/casefile.html"

# Diff the newest two central runs → $RUNS_ROOT/diff.md
recon diff --a "$(ls -td "$RUNS_ROOT"/* | sed -n '2p')"            --b "$(ls -td "$RUNS_ROOT"/* | sed -n '1p')"            --out "$RUNS_ROOT/diff.md"
```

## Help usage
- **Top-level help** (shows subcommands):
```bash
recon --help
```
- **Subcommand help**:
```bash
recon run --help
recon diff --help
```
- **Doctor note:** `recon doctor` prints a diagnostic report and currently has **no separate help screen**; running `recon doctor --help` will just execute the doctor checks.

## What’s next (near-term and roadmap)
**Near-term options**
- Re-introduce a **minimal CI** (smoke run + artifact upload, trigger on tags).  
- **HTML polish** (surface notes/resolvers, highlight delta, table styling).  
- **DNS** module improvements (timeouts/backoff; better dangling-CNAME detection).  
- Expand **rules** for more precise findings.  
- **Docs**: README snippets for `-i` flow and the sslip.io lab example. fileciteturn0file0

**Roadmap snapshot**
- **v0.2.x — Polish & Prep:** HTML template refinements; CI smoke test; document seeds/lab flow.  
- **v0.3.0 — MX hygiene:** flag consumer MX/misconfigs; SPF/DMARC posture hints with clear explainers.  
- **v0.4.0 — Export & Distribution:** HTML/PDF export refinements; prep for PyPI/`pipx`.  
- **v0.5.0 — Enrichment:** optional Amass/Nuclei importers; pluggable rule packs.  
- **v0.6.0 — AI Writer (opt-in):** artifact-grounded summaries with evidence citations and human approval. fileciteturn0file3

## Handoff checklist for the next session
- Confirm repo/remote match the identity above; keep `v0.2.0` as the last tagged snapshot.  
- Decide whether to prioritize **CI + HTML polish** or begin **MX hygiene** for `v0.3.0`.  
- Track open items: README/doc updates, HTML template choice, and MX heuristics/fixtures. fileciteturn0file4
