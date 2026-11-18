"""ForensicLogger + report test."""
import sys, os, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from guardian.logger import ForensicLogger
from guardian.rules import Alert
from guardian import report


def test_logger_writes_csv():
    d = tempfile.mkdtemp()
    fields = {"temp": {}, "pump_on": {}}
    lg = ForensicLogger(log_dir=d, fields=fields)
    lg.log_state({"temp": 330, "pump_on": 1})
    lg.log_alerts([Alert("X", "CRITICAL", "temp", 420, "hot")])
    assert os.path.exists(os.path.join(d, "telemetry.csv"))
    rows = open(os.path.join(d, "alerts.csv")).read()
    assert "CRITICAL" in rows and "X" in rows


def test_report_builds_html():
    d = tempfile.mkdtemp()
    fields = {"temp": {}}
    lg = ForensicLogger(log_dir=d, fields=fields)
    lg.log_alerts([Alert("Y", "WARNING", "temp", 365, "warm")])
    out, total, counts = report.build(log_dir=d)
    assert os.path.exists(out) and total == 1
    assert "<html" in open(out).read().lower()


if __name__ == "__main__":
    test_logger_writes_csv(); print("PASS test_logger_writes_csv")
    test_report_builds_html(); print("PASS test_report_builds_html")
    print("OK")
