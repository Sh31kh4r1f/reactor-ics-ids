#!/usr/bin/env python3
"""
Reactor Guardian -- ICS Intrusion Detection System
==================================================
Modbus diye reactor PLC er obostha proti second e pore, rules.json er
niyom apply kore, ar attack/anomaly dhorle alert dekhay.

Cholao:  python -m guardian.monitor
(Age alada terminal e PLC chalu rakho: python simulator/reactor_plc.py)
"""
import argparse
import time

from pymodbus.client import ModbusTcpClient
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from guardian.rules import RuleEngine
from guardian.logger import ForensicLogger

console = Console()

SEV_STYLE = {"CRITICAL": "bold white on red", "WARNING": "bold black on yellow", "INFO": "cyan"}


def read_state(client, slave, fields):
    """PLC theke holding register + coil pore {field:value} banay."""
    hr = client.read_holding_registers(0, 6, slave=slave)
    co = client.read_coils(0, 3, slave=slave)
    if hr.isError() or co.isError():
        return None
    regs, coils = hr.registers, [int(b) for b in co.bits[:3]]
    state = {}
    for name, meta in fields.items():
        src = regs if meta["source"] == "hr" else coils
        idx = meta["index"]
        state[name] = src[idx] if idx < len(src) else None
    return state


def render(state, alerts, fields, polls):
    t = Table(title="☢  REACTOR GUARDIAN  —  live ICS monitor", expand=True)
    t.add_column("Sensor / Tag", style="cyan", no_wrap=True)
    t.add_column("Value", justify="right")
    # kon field e alert ache
    flagged = {a.field for a in alerts}
    for name, meta in fields.items():
        v = state.get(name)
        style = "red bold" if name in flagged else "green"
        t.add_row(meta["label"], Text(str(v), style=style))

    if alerts:
        a = Table.grid(padding=(0, 1))
        for al in alerts:
            a.add_row(Text(f" {al.severity} ", style=SEV_STYLE.get(al.severity, "white")),
                      Text(al.id, style="bold"), Text(al.message))
        alert_panel = Panel(a, title=f"🚨 {len(alerts)} ALERT(S)", border_style="red")
    else:
        alert_panel = Panel(Text("✓ Shob normal. Kono anomaly nei.", style="green"),
                            title="status", border_style="green")

    grid = Table.grid(expand=True)
    grid.add_row(t)
    grid.add_row(alert_panel)
    grid.add_row(Text(f"polls: {polls}   (Ctrl+C to stop)", style="dim"))
    return grid


def main():
    ap = argparse.ArgumentParser(description="Reactor Guardian ICS IDS")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=5020)
    ap.add_argument("--slave", type=int, default=1)
    ap.add_argument("--interval", type=float, default=1.0)
    ap.add_argument("--once", action="store_true", help="ekbar check kore ber hoye jao (test er jonno)")
    ap.add_argument("--log", action="store_true", help="telemetry + alert CSV te log koro (forensics)")
    args = ap.parse_args()

    engine = RuleEngine()
    fields = engine.field_map()
    logger = ForensicLogger(fields=fields) if args.log else None
    client = ModbusTcpClient(args.host, port=args.port)
    if not client.connect():
        console.print(f"[red]PLC te connect holo na ({args.host}:{args.port}). PLC chalu ache to?[/]")
        return

    polls = 0
    try:
        if args.once:
            state = read_state(client, args.slave, fields)
            alerts = engine.evaluate(state) if state else []
            if logger and state:
                logger.log_state(state); logger.log_alerts(alerts)
            console.print(render(state or {}, alerts, fields, 1))
            return
        with Live(console=console, refresh_per_second=4, screen=False) as live:
            while True:
                state = read_state(client, args.slave, fields)
                polls += 1
                if state is None:
                    live.update(Panel(Text("PLC read error / disconnected", style="red")))
                else:
                    alerts = engine.evaluate(state)
                    if logger:
                        logger.log_state(state); logger.log_alerts(alerts)
                    live.update(render(state, alerts, fields, polls))
                    for a in alerts:
                        if a.severity == "CRITICAL":
                            console.log(f"[red]LOG {a.ts} {a.id}: {a.message}[/]")
                time.sleep(args.interval)
    except KeyboardInterrupt:
        console.print("\n[dim]guardian stopped.[/]")
    finally:
        client.close()


if __name__ == "__main__":
    main()
