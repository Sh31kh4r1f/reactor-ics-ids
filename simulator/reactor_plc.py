#!/usr/bin/env python3
"""
Nuclear Reactor PLC Simulator (Modbus TCP)
==========================================
Eta ekta NOKOL (simulated) nuclear reactor control PLC.
Real plant er moto Modbus TCP server khule boshe thake, ar
background e ekta simple physics loop reactor er obostha update kore.

Attacker ei PLC te Modbus command pathiye reactor er obostha
bদলাতে pare -- ar amader Guardian IDS seta dhorbe.

!!! Eta 100% simulation. Kono real hardware er sathe jogajog nei. !!!

Register map (Holding Registers, slave id = 1):
  HR0  core_temp_c      core temperature (deg C)   normal ~300
  HR1  pressure_bar     coolant pressure (bar)     normal ~155
  HR2  coolant_flow_pct coolant flow (%)           normal 100
  HR3  rod_position_pct control rod position (%)   0=in(safe) 100=out(hot)
  HR4  power_mw         reactor power (MW)          normal ~1000
  HR5  pump_rpm         coolant pump speed (RPM)    normal ~1800

Coils (slave id = 1):
  C0   coolant_pump     main coolant pump ON/OFF   normal ON
  C1   safety_injection emergency cooling          normal OFF
  C2   scram            emergency shutdown trip     normal OFF
"""
import threading
import time
import random

from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusSlaveContext,
    ModbusServerContext,
)
from pymodbus.server import StartTcpServer

HOST = "127.0.0.1"
PORT = 5020
SLAVE_ID = 1

# --- register index names (holding registers) ---
HR_TEMP, HR_PRESS, HR_FLOW, HR_ROD, HR_POWER, HR_PUMP = range(6)
# --- coil index names ---
CO_PUMP, CO_SAFETY, CO_SCRAM = range(3)


def build_context():
    """Reactor er starting (normal/safe) obostha toiri kore."""
    hr = ModbusSequentialDataBlock(0, [300, 155, 100, 65, 1000, 1800] + [0] * 10)
    co = ModbusSequentialDataBlock(0, [1, 0, 0] + [0] * 10)  # pump ON
    slave = ModbusSlaveContext(hr=hr, co=co, zero_mode=True)
    return ModbusServerContext(slaves={SLAVE_ID: slave}, single=False)


def physics_loop(context):
    """
    Proti 1 second e reactor er obostha update kore.
    Attacker jodi rod tene newd / pump bondho kore, physics
    temperature/pressure barabe -- ekdom real plant er moto cause->effect.
    """
    store = context[SLAVE_ID]
    while True:
        time.sleep(1.0)
        hr = store.getValues(3, 0, count=6)       # holding registers
        co = store.getValues(1, 0, count=3)       # coils
        temp, press, flow, rod, power, pump = hr
        pump_on, safety_on, scram = co

        # SCRAM = emergency shutdown: rod gula poro ঢুকiye dao
        if scram:
            rod = max(0, rod - 20)

        # Control rod joto beshi bera, toto beshi power + heat
        target_power = int(rod * 15.4)            # rod 65 -> ~1000 MW
        power += (target_power - power) // 3

        # Pump off / low flow hole cooling kome -> temp bare
        if not pump_on or flow < 30:
            pump = max(0, pump - 300)
            temp += 8 + power // 400
        else:
            pump = min(1800, pump + 200)
            # cooling: temp target power er upor base kore
            target_temp = 250 + power // 10        # 1000 MW -> ~350
            temp += (target_temp - temp) // 4

        # Safety injection on hole druto thanda
        if safety_on:
            temp -= 25
            press = min(press + 5, 180)

        # Pressure temperature follow kore (simplified)
        press += (int(150 + (temp - 300) * 0.4) - press) // 5

        # choto noise
        temp += random.randint(-1, 1)

        # bounds (register 0..65535)
        temp = max(0, min(2000, temp))
        press = max(0, min(400, press))
        power = max(0, power)

        store.setValues(3, 0, [temp, press, flow, rod, power, pump])


def run():
    context = build_context()
    t = threading.Thread(target=physics_loop, args=(context,), daemon=True)
    t.start()
    print(f"[reactor-plc] Modbus TCP server listening on {HOST}:{PORT} (slave {SLAVE_ID})")
    print("[reactor-plc] Reactor online. Ctrl+C to stop.")
    StartTcpServer(context=context, address=(HOST, PORT))


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n[reactor-plc] shutdown.")
