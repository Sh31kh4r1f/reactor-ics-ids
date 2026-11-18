#!/usr/bin/env python3
"""
Rule Engine
===========
rules.json pore reactor er obostha (state) er against e check kore.
Notun detection logic ekhane noy -- rules.json e likho (Sherlock pattern).

3 rokom rule:
  threshold : ekta field ekta value theke boro/choto kina
  combo     : koyekta condition EK shathe sotti kina (AND)
  rate      : ekta field khub druto bodlalo kina (history lage)
"""
import json
import time
from pathlib import Path

DEFAULT_RULES = Path(__file__).parent / "data" / "rules.json"

_OPS = {
    "gt": lambda a, b: a > b,
    "lt": lambda a, b: a < b,
    "ge": lambda a, b: a >= b,
    "le": lambda a, b: a <= b,
    "eq": lambda a, b: a == b,
    "ne": lambda a, b: a != b,
}


class Alert:
    def __init__(self, rule_id, severity, field, value, message):
        self.id = rule_id
        self.severity = severity
        self.field = field
        self.value = value
        self.message = message
        self.ts = time.strftime("%H:%M:%S")

    def __repr__(self):
        return f"<{self.severity} {self.id} {self.field}={self.value}>"


class RuleEngine:
    def __init__(self, rules_path=DEFAULT_RULES):
        data = json.loads(Path(rules_path).read_text())
        self.fields = data["fields"]
        self.rules = data["rules"]
        self._history = {}   # field -> (value, timestamp) for rate rules

    def field_map(self):
        """Monitor ke bole kon register/coil porte hobe."""
        return self.fields

    def _check_one(self, cond, state):
        val = state.get(cond["field"])
        if val is None:
            return False
        return _OPS[cond["op"]](val, cond["value"])

    def evaluate(self, state):
        """state = {field_name: value}. Alert list return kore."""
        alerts = []
        now = time.monotonic()
        for r in self.rules:
            rtype = r["type"]
            hit = False
            field = r.get("field", "-")
            value = state.get(field, "-")

            if rtype == "threshold":
                hit = _OPS[r["op"]](state.get(field), r["value"])

            elif rtype == "combo":
                hit = all(self._check_one(c, state) for c in r["all"])
                value = ", ".join(f"{c['field']}={state.get(c['field'])}" for c in r["all"])

            elif rtype == "rate":
                cur = state.get(field)
                prev = self._history.get(field)
                if prev is not None and cur is not None:
                    pval, pts = prev
                    dt = max(now - pts, 0.001)
                    delta_per_sec = abs(cur - pval) / dt
                    if delta_per_sec > r["max_delta"]:
                        hit = True
                        value = f"{pval}->{cur} ({delta_per_sec:.0f}/s)"
                self._history[field] = (cur, now)

            if hit:
                alerts.append(Alert(r["id"], r["severity"], field, value, r["message"]))
        return alerts
