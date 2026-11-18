"""Rule engine er test. Cholao:  python -m pytest -q  (ba)  python tests/test_rules.py"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from guardian.rules import RuleEngine


def _engine():
    return RuleEngine()


def test_normal_state_no_alerts():
    e = _engine()
    normal = {"temp": 330, "press": 155, "flow": 100, "rod": 65,
              "power": 1000, "pump_rpm": 1800, "pump_on": 1, "safety": 0, "scram": 0}
    assert e.evaluate(normal) == []


def test_pump_trip_is_critical():
    e = _engine()
    st = {"temp": 330, "press": 155, "flow": 100, "rod": 65,
          "power": 1000, "pump_rpm": 100, "pump_on": 0, "safety": 0, "scram": 0}
    ids = {a.id for a in e.evaluate(st)}
    assert "PUMP_TRIP_AT_POWER" in ids


def test_temp_critical():
    e = _engine()
    st = {"temp": 420, "press": 155, "flow": 100, "rod": 65,
          "power": 1000, "pump_rpm": 1800, "pump_on": 1, "safety": 1, "scram": 0}
    sev = {a.id: a.severity for a in e.evaluate(st)}
    assert sev.get("TEMP_CRITICAL") == "CRITICAL"


def test_rod_ejection_rate():
    e = _engine()
    base = {"temp": 330, "press": 155, "flow": 100, "rod": 65,
            "power": 1000, "pump_rpm": 1800, "pump_on": 1, "safety": 0, "scram": 0}
    e.evaluate(base)                    # history seed: rod=65
    base2 = dict(base); base2["rod"] = 100   # jump 35 in one tick
    ids = {a.id for a in e.evaluate(base2)}
    assert "ROD_EJECTION" in ids


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn(); print("PASS", fn.__name__)
    print(f"\nAll {len(fns)} tests passed.")
