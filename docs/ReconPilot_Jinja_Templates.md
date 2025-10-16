# ReconPilot — Jinja Templates & Usage

This doc packages the Jinja-related bits for ReconPilot, including a **ready-to-use `templates/casefile.md.j2`** that matches the rendering flow in `render.py`.

---

## 1) Jinja usage in `render.py`

```python
from jinja2 import Environment, FileSystemLoader, select_autoescape

def render_casefile(template_dir: Path, context: dict) -> str:
    """Render the Markdown report from templates/casefile.md.j2."""
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(disabled_extensions=("md",))
    )
    tpl = env.get_template("casefile.md.j2")
    return tpl.render(**context)
```

> `render_casefile_html(...)` converts the rendered Markdown to HTML (via `markdown` module if present). The HTML wrapper is assembled in Python (not Jinja), so **only `casefile.md.j2` is required** under `templates/`.

Expected call sites create a `context` dict (see below for suggested keys) and pass `template_dir` pointing to a folder that contains `casefile.md.j2`.

---

## 2) Template: `templates/casefile.md.j2`

**Place this file at:** `templates/casefile.md.j2`

```jinja
{# -------------------------------------------------------------- #}
{# ReconPilot Casefile (Markdown)                                 #}
{# Compatible with render.py -> render_casefile(template_dir, ctx) #}
{# -------------------------------------------------------------- #}

# {{ org | default('Organization not set') }} — ReconPilot Casefile

- **Run ID:** `{{ run_id | default('run-unknown') }}`  
- **Created at (UTC):** {{ created_at | default('unknown') }}  
- **Engagement:** {{ engagement | default('—') }}  
- **Domains in scope:** {% if domains %}{{ domains | join(', ') }}{% else %}—{% endif %}

---

## Summary

- **Total hosts (inventory):** {{ inventory_count | default(0) }}
- **Delta vs previous run:** {% if delta and delta.prev_run %}
  prev=`{{ delta.prev_run }}`, **+{{ delta.counts.new }}** new / **-{{ delta.counts.removed }}** removed
  {% else %}no prior run found{% endif %}

{% if delta and (delta.new_hosts or delta.removed_hosts) %}
### Changes since previous run
{% if delta.new_hosts %}
**New hosts ({{ delta.new_hosts | length }}):**
{% for h in delta.new_hosts %}- `{{ h }}`{% endfor %}
{% endif %}
{% if delta.removed_hosts %}
**Removed hosts ({{ delta.removed_hosts | length }}):**
{% for h in delta.removed_hosts %}- `{{ h }}`{% endfor %}
{% endif %}
{% endif %}

---

## Certificate Transparency (CT) Highlights

{% if ct and ct.hosts %}
Discovered **{{ ct.hosts | length }}** hostnames via CT.

{% for item in ct.hosts[:200] %}
- `{{ item }}`
{% endfor %}

{% if ct.hosts|length > 200 %}
…and **{{ ct.hosts|length - 200 }}** more.
{% endif %}
{% else %}
_No CT results recorded for this run._
{% endif %}

---

## DNS Notes

{% if dns and (dns.issues or dns.records) %}
{% if dns.issues %}
### Issues
{% for i in dns.issues %}
- **{{ i.kind | default('issue') }}**: {{ i.message | default(i | string) }}
{% endfor %}
{% endif %}

{% if dns.records %}
### Records (sample)
{% for rec in dns.records[:200] %}
- `{{ rec.name }}` → {{ rec.type }}/{{ rec.value }}
{% endfor %}
{% if dns.records|length > 200 %}
…and **{{ dns.records|length - 200 }}** more.
{% endif %}
{% endif %}
{% else %}
_No DNS data recorded for this run._
{% endif %}

---

## External Imports (RP Dock)

{% if dock and dock.rollups %}
{% for tool in dock.rollups %}
### {{ tool.name | upper }}
- **Policy:** `{{ tool.policy }}`
- **Kept:** {{ tool.kept | default(0) }} / **Total:** {{ tool.total | default(0) }}
- **Source file:** `{{ tool.source | default('n/a') }}`

{% if tool.rows %}
#### Sample (first {{ tool.rows|length }} rows shown)
| Host | Port | Severity | Summary | Evidence |
|------|------|----------|---------|----------|
{% for r in tool.rows[:50] %}
| {{ r.host | default('—') }} | {{ r.port | default('—') }} | {{ r.severity | default('—') }} | {{ r.summary | default('—') }} | {{ r.evidence | default('—') }} |
{% endfor %}
{% if tool.rows|length > 50 %}
| … | … | … | … | … |
{% endif %}
{% else %}
_No rows kept for this tool (policy or filters may have excluded them)._
{% endif %}

{% endfor %}
{% else %}
_No external imports were attached to this run._
{% endif %}

---

## Evidence Index

Paths of raw/normalized artifacts for auditing.
{% if evidence and evidence.items %}
{% for ev in evidence.items[:300] %}
- `{{ ev.path }}` — sha256={{ ev.sha256 | default('n/a') }}
{% endfor %}
{% if evidence.items|length > 300 %}
…and **{{ evidence.items|length - 300 }}** more.
{% endif %}
{% else %}
_No evidence recorded._
{% endif %}

---

## Appendix

- ReconPilot version: {{ version | default('unknown') }}
- Resolvers: {% if resolvers %}{{ resolvers | join(', ') }}{% else %}—{% endif %}
- Notes: {{ notes | default('—') }}
```

### Suggested `context` shape

This template is resilient to missing keys (uses `default`). Here’s a **suggested context** layout that matches typical ReconPilot runs and the planned RP Dock rollups:

```json
{
  "org": "My lab",
  "run_id": "run-20251008-074300Z",
  "created_at": "2025-10-08T07:43:00Z",
  "engagement": "Q4-Redteam",
  "domains": ["example.com"],
  "inventory_count": 224,

  "delta": {
    "prev_run": "run-20251008-073949Z",
    "counts": {"new": 0, "removed": 0},
    "new_hosts": [],
    "removed_hosts": []
  },

  "ct": {
    "hosts": ["a.example.com", "b.example.com"]
  },

  "dns": {
    "issues": [{"kind": "NXDOMAIN", "message": "foo.example.com → NX"}],
    "records": [{"name":"www.example.com","type":"A","value":"203.0.113.10"}]
  },

  "dock": {
    "rollups": [
      {
        "name": "nmap",
        "policy": "owned",
        "kept": 12,
        "total": 12,
        "source": "runs/.../artifacts/imports/nmap/2025-10-08/raw.xml",
        "rows": [
          {"host":"203.0.113.10","port":"443/tcp","severity":null,"summary":"https open","evidence":"nginx/1.24"}
        ]
      },
      {
        "name": "nuclei",
        "policy": "all",
        "kept": 2,
        "total": 2,
        "source": "runs/.../artifacts/imports/nuclei/2025-10-08/raw.jsonl",
        "rows": [
          {"host":"app.example.com","port":"443","severity":"medium","summary":"template-id: x","evidence":"...payload redacted..."}
        ]
      }
    ]
  },

  "evidence": {
    "items": [
      {"path":"runs/.../artifacts/ct_hosts.json","sha256":"..."},
      {"path":"runs/.../artifacts/imports/nmap/.../normalized.jsonl","sha256":"..."}
    ]
  },

  "version": "v0",
  "resolvers": ["1.1.1.1","8.8.8.8"],
  "notes": "this is just a test"
}
```

> You can feed fewer keys; the template uses `default` and conditional blocks so it degrades gracefully.

---

## 3) Folder layout

```
your-project/
  templates/
    casefile.md.j2
  render.py
  cli.py
  ...
```

In your CLI, set `template_dir` to `Path(__file__).parent / "templates"` (or your chosen path).

---

## 4) Tips

- If you later add partials/macros (e.g., `templates/_imports_table.j2`), just `include` them from `casefile.md.j2` and keep using the same `Environment` and `FileSystemLoader` setup.
- To keep shareable reports clean, consider redacting sensitive evidence strings in the `rows` you feed the template (or inject a `redact` boolean and conditionalize output).

— End —
