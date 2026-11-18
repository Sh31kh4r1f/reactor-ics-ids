# ☢️ Reactor ICS Guardian

> A self-contained **Industrial Control System (ICS) security lab + intrusion-detection tool** that simulates a nuclear-reactor PLC over **Modbus TCP**, lets you launch realistic attacks against it, and detects them in real time — all in pure Python, **no Docker or hardware required**.

![python](https://img.shields.io/badge/python-3.9%2B-blue) ![license](https://img.shields.io/badge/license-MIT-green) ![status](https://img.shields.io/badge/scope-education%20%2F%20defensive-orange)

---

## Why this exists

Real OT/ICS security labs (GRFICSv3, etc.) need Docker or full VMs. This project packs the whole **attack → effect → detection** loop into three small Python programs so anyone can learn ICS security on a laptop:

```
 attacker.py  ──Modbus write──▶  reactor_plc.py  ──Modbus read──▶  guardian (IDS)
  (red team)                      (simulated PLC)                    (blue team)
```

A background physics loop makes the reactor behave realistically: cut the coolant pump and the core temperature actually climbs; yank the control rods and power spikes — just like a real plant's cause-and-effect.

## Architecture (code vs data)

Detection logic lives in **`guardian/data/rules.json`**, not in code. Adding a new detection is a few lines of JSON — the same *code-and-data separation* that lets tools like Sherlock scale to hundreds of checks.

```
reactor-ics-ids/
├── simulator/reactor_plc.py   # fake reactor PLC (Modbus TCP server + physics)
├── attacks/attacker.py        # red-team: pump-off, rod-eject, overheat, safety-off
├── guardian/
│   ├── monitor.py             # live IDS dashboard (polls PLC, raises alerts)
│   ├── rules.py               # rule engine (threshold / combo / rate)
│   ├── logger.py              # forensic CSV logging (telemetry + alerts)
│   ├── report.py              # standalone HTML incident report generator
│   └── data/rules.json        # ← detection rules live here (edit this, not the code)
├── logs/                      # generated: telemetry.csv, alerts.csv, report.html
└── tests/
```

## Quick start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Terminal 1 — start the reactor PLC
python simulator/reactor_plc.py

# Terminal 2 — start the Guardian IDS dashboard
python -m guardian.monitor

# Terminal 3 — launch an attack and watch the alerts fire
python attacks/attacker.py pump-off
python attacks/attacker.py rod-eject
python attacks/attacker.py spoof        # sensor spoofing / false data injection

# Run the monitor with forensic logging, then build an HTML report
python -m guardian.monitor --log
python -m guardian.report               # -> logs/report.html
```

## Detections included

| Rule | Severity | Models |
|------|----------|--------|
| `PUMP_TRIP_AT_POWER` | CRITICAL | Loss-of-coolant attack |
| `ROD_EJECTION` | CRITICAL | Rapid control-rod withdrawal (Stuxnet-style) |
| `OVERHEAT_NO_SAFETY` | CRITICAL | Safety-system sabotage |
| `SENSOR_SPOOF` | CRITICAL | Fake sensor data hiding an attack |
| `FLOW_LOW`, `TEMP_CRITICAL` | CRITICAL | Core cooling failure |
| `PUMP_ACTUATOR_MISMATCH` | WARNING | Sensor/actuator spoofing |
| `TEMP_HIGH`, `PRESS_LOW/HIGH`, `ROD_WITHDRAWN` | WARNING | Unsafe operating band |

## Tests

```bash
python -m pytest -q      # or:  python tests/test_rules.py
```

## Background — real ICS security

The attacks mirror real history: **Stuxnet (2010)** sabotaged PLCs at Natanz; **Kudankulam (2019)** saw malware on a nuclear plant's IT network. Standards that govern this space: **IEC 62443**, **IAEA NSS 17**, **NIST SP 800-82**.

## ⚠️ Scope & ethics

100% simulation. It talks only to its own local Modbus server (`127.0.0.1:5020`) and touches **no real hardware**. The attack scripts exist to test the defensive IDS. Running Modbus writes against systems you do not own is illegal — keep it to this lab.

## License

MIT — see [LICENSE](LICENSE).
