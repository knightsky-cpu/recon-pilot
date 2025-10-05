from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
import yaml

@dataclass
class Scope:
    org: str
    domains: List[str]
    policy: dict = field(default_factory=lambda: {"passive_only": True})
    notes: str = ""
    resolvers: List[str] = field(default_factory=lambda: ["1.1.1.1","8.8.8.8"])
    seeds: dict = field(default_factory=lambda: {"hosts": []})

    @staticmethod
    def load(path: str) -> "Scope":
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return Scope(
            org=data.get("org",""),
            domains=data.get("domains", []),
            policy=data.get("policy", {"passive_only": True}),
            notes=data.get("notes", ""),
            resolvers=data.get("resolvers", ["1.1.1.1","8.8.8.8"]),
            seeds=data.get("seeds", {"hosts": []}),
        )

    def in_scope_domain(self, host: str) -> bool:
        host = host.lower().strip(".")
        return any(host == d or host.endswith("." + d) for d in self.domains)
