# Lab Setup Guide

## Option A — This repo (no Docker, recommended to start)
See the Quick start in the main README. Runs on any machine with Python 3.9+.

## Option B — GRFICSv3 (full OT lab, needs Docker)
GRFICSv3 simulates a full chemical/industrial process with real PLC + SCADA + HMI.

### 1. Install Docker Desktop (macOS)
- Download: https://www.docker.com/products/docker-desktop/
- Install, open it, wait until the whale icon says "Docker Desktop is running".
- Verify in a terminal:
  ```bash
  docker --version
  docker compose version
  ```

### 2. Get GRFICSv3
```bash
git clone https://github.com/Fortiphyd/GRFICSv3.git
cd GRFICSv3
# follow the repo's README — it ships docker-compose files per component
```

### 3. Other great practice labs
| Lab | Notes |
|-----|-------|
| zakharb/labshock | Ready-made ICS lab, Docker-based |
| Fortiphyd/GRFICSv3 | Realistic PLC + SCADA + HMI |
| conpot (mushorg/conpot) | SCADA honeypot — pretends to be a real PLC |
| nsacyber/GRASSMARLIN | NSA tool: passive ICS network mapping |

## Learn the protocols
- **Modbus** and **DNP3** are the "languages" PLCs speak.
- Read with Wireshark (it decodes Modbus/DNP3) while this lab runs.
- Standard to study for jobs: **IEC 62443**.
