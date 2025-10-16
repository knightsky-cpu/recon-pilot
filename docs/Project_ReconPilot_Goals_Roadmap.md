# Project ReconPilot — Goals, Integration Plans, and Roadmap

## Vision
A **passive-first, scope-aware recon helper** that produces **explainable, evidence-backed reports** with minimal noise—useful for solo practitioners and small teams, safe by default, and easy to iterate in the open.

## Success Criteria
- **Safety-first** defaults: no active scanning unless explicitly enabled in the future.
- **Explainability**: every finding includes “why it matters” and suggested next steps.
- **Repeatability**: saved artifacts + consistent reports; supports weekly changefeed workflows.
- **Low-friction**: one-command bootstrap, simple CLI, minimal dependencies.

---

## Current Project Goals (near-term)
1. **Consolidate Patch 1** across docs and examples (ensure README mentions delta+HTML).
2. **Patch 2 – MX hygiene**
   - Detect obvious consumer MX or misconfigs.
   - Add light SPF/DMARC posture hints.
   - Render clear, actionable guidance in the casefile.
3. **HTML export polish**
   - Improve typography and layout; optional logo slot.
   - Add CLI flag for HTML-only / MD-only output.
4. **Developer ergonomics**
   - `doctor` diagnostics to validate environment and scope config.
   - Scripts for reproducible local tests and sample runs.

---

## Future Integration Plans (mid-term)
- **Optional imports** (Amass, Nuclei JSONL) to enrich context *while staying passive on our side*.
- **AI Writer (opt-in, artifact-grounded)**
  - Only reads saved artifacts (`delta.json`, inventory, findings).
  - Must cite evidence; redaction pass; human approval required.
- **CI/CD**
  - GitHub Actions: lint, unit tests, smoke `run` (with sample scope), artifact checks.
- **Packaging & distribution**
  - Publish to PyPI; provide `pipx` instructions.
  - Homebrew/Linuxbrew tap for the `recon` runner (optional).
- **Pluggable findings**
  - Rule pack model for low-noise heuristics (DNS posture, CT anomalies, takeover risk hints).
- **Export formats**
  - PDF via headless HTML; optional Jira/SARIF exporters for teams.

---

## Roadmap (proposed)
### v0.2.x — Polish & Prep
- Refine HTML template; improve casefile structure for delta section.
- Add CI smoke test; ensure stable outputs.
- Document seeds/lab flow more visibly in README/docs.

### v0.3.0 — MX Hygiene
- Add MX posture checks with clear “why it matters” and remediation steps.
- Surface results in both Markdown and HTML reports.

### v0.4.0 — Export & Distribution
- HTML/PDF export improvements and CLI flags.
- Prep for PyPI distribution and `pipx` install guide.

### v0.5.0 — Enrichment & Integrations
- Optional Amass/Nuclei importers (opt-in) with provenance tagging.
- Begin rule pack structure for more heuristics (SPF/DMARC cues, DNSSEC presence, wildcard DNS flags).

### v0.6.0 — AI Writer (Opt-in, Guardrailed)
- Introduce AI writer behind a flag with strict artifact-only context, redaction, and evidence references.
- Human-in-the-loop publishing flow.

### v1.0 — Stability & Adoption
- Hardened CLI, docs, and CI.
- Clear extension points for rule packs and exporters.
- Documented safety and authorization flow for any future active checks.

---

## Non-Goals / Guardrails
- No default **active scanning** or fuzzing.
- No collection beyond declared **scope**.
- Avoid noisy heuristics; prioritize precision over breadth.

---

## Repo & Identity (for future sessions)
- **GitHub user:** `knightsky-cpu`
- **Repository:** `recon-pilot`
- **Repo URL:** https://github.com/knightsky-cpu/recon-pilot
- **Primary branch:** `main`
- **Current tag:** `v0.2.0` (Patch 1)
