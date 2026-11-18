#!/usr/bin/env python3
"""
Forensic logger
===============
Reactor er telemetry ar alert gula CSV file e rakhe, jate pore
incident investigation / report banano jay.

  logs/telemetry.csv : proti poll er reactor obostha
  logs/alerts.csv    : jotobar alert utheche
"""
import csv
import time
from pathlib import Path

LOG_DIR = Path(__file__).parent.parent / "logs"


class ForensicLogger:
    def __init__(self, log_dir=LOG_DIR, fields=None):
        self.dir = Path(log_dir)
        self.dir.mkdir(exist_ok=True)
        self.telemetry = self.dir / "telemetry.csv"
        self.alerts = self.dir / "alerts.csv"
        self._field_names = list(fields.keys()) if fields else []
        self._init_files()

    def _init_files(self):
        if not self.telemetry.exists():
            with open(self.telemetry, "w", newline="") as f:
                csv.writer(f).writerow(["timestamp"] + self._field_names)
        if not self.alerts.exists():
            with open(self.alerts, "w", newline="") as f:
                csv.writer(f).writerow(["timestamp", "severity", "rule_id", "field", "value", "message"])

    def log_state(self, state):
        with open(self.telemetry, "a", newline="") as f:
            csv.writer(f).writerow([time.strftime("%Y-%m-%d %H:%M:%S")] +
                                   [state.get(n) for n in self._field_names])

    def log_alerts(self, alerts):
        if not alerts:
            return
        with open(self.alerts, "a", newline="") as f:
            w = csv.writer(f)
            for a in alerts:
                w.writerow([time.strftime("%Y-%m-%d %H:%M:%S"),
                            a.severity, a.id, a.field, a.value, a.message])
