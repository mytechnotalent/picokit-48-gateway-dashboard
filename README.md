![picokit-48-gateway-dashboard](https://raw.githubusercontent.com/mytechnotalent/picokit-48-gateway-dashboard/main/picokit-48-gateway-dashboard.png)

<br>

## FREE Reverse Engineering Self-Study Course [HERE](https://github.com/mytechnotalent/reverse-engineering)
## FREE Embedded Hacking Course [HERE](https://github.com/mytechnotalent/Embedded-Hacking)

<br>

# PICOKIT-48 GATEWAY DASHBOARD

### Sensor Node and Charted Gateway
#### Lesson 48 of the Picokit Series

<br>

***
**LEGAL DISCLAIMER:**
The information, tools, and code provided in this repository and course are strictly for educational, research, and defensive purposes only.

You are explicitly prohibited from using any materials contained herein to access, test, modify, or exploit any device, network, or system that you do not own 100% or for which you do not have explicit, documented, and legally binding authorization to interact with.

By using this repository and course, you acknowledge and agree that:

1. Any illegal, unauthorized, or malicious use of this information is solely your responsibility.
2. The author(s) and contributor(s) of this repository and course shall not be held liable for any damages, legal repercussions, criminal charges, or unauthorized actions resulting from the use, misuse, or abuse of the contents herein.
3. You will comply with all applicable local, state, national, and international laws regarding cybersecurity and computer fraud.

**IF YOU DO NOT AGREE WITH THESE TERMS, DO NOT USE THIS REPOSITORY AND COURSE.**
***

<br>
<br>

## Overview

The dashboard capstone. The node samples the DHT11, drives the red, yellow,
and green comfort LEDs, and transmits an authenticated heartbeat with the
temperature and humidity. The richer gateway is the star: the terminal
dashboard adds a live temperature and humidity sparkline, and the web
dashboard adds a signal chart and a per-node trend summary on top of the
climate chart it already served.

<br>

## What it teaches

- A full temperature and humidity node with comfort LED annunciation.
- A heartbeat that carries both readings: `{"n":48,"s":<seq>,"t":<t>,"h":<h>}`.
- A richer gateway: TUI sparklines plus web charts and a trend summary.
- The gateway side: receive, authenticate, reject, log, and chart.

<br>

## Hardware

| Peripheral | Pico 2 pin | Role |
| --- | --- | --- |
| DHT11 | GP4 | temperature and humidity |
| Red / Yellow / Green | GP16 / GP18 / GP17 | comfort annunciator |
| Onboard LED | GP25 | heartbeat, one blink per transmit |
| RYLR998 | GP8 TX / GP9 RX | LoRa heartbeat |
| Debug Probe | SWCLK/SWDIO/GND, GP0/GP1 | SWD and the console |

<br>

## How it works

The node runs `monitor_step` in a loop. Every 2 seconds it samples the DHT11
and lights the comfort LED for the reading, and every 5 seconds it seals
`{"n":48,"s":<seq>,"t":<tenths>,"h":<tenths>}` with the field key and sends it
over LoRa. The gateway authenticates each frame, stores it, and charts the
trusted history in both the terminal and the browser.

<br>

## Build and flash

```bash
cd firmware
cmake -S . -B build -G Ninja -DPICO_BOARD=pico2 -DPICO_PLATFORM=rp2350-arm-s
cmake --build build
openocd -f interface/cmsis-dap.cfg -f target/rp2350.cfg \
  -c "program build/picokit_48_gateway_dashboard.elf verify reset exit"
```

<br>

## Watch the node

Open the console at 115200 and reset:

```text
BOOT
I2C scan:
  no devices
=== PICOKIT-48 GATEWAY DASHBOARD // COMFORT LEDS + AUTHENTICATED HEARTBEAT ===
DHT t=230 h=610 code=3
RX from 0x0001, N bytes
```

<br>

## The gateway

```bash
cd gateway
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 listen.py --port /dev/cu.usbserial-A50285BI --hub 0001 --network 18 --db gateway.db
```

The terminal dashboard `python3 tui.py --db gateway.db` shows live nodes, the
event log, and a temperature and humidity sparkline. The web dashboard
`python3 web/app.py --db gateway.db` shows the climate chart, a signal chart,
and the per-node trend summary.

<br>

## Verify

```bash
python3 .opencode/skill/embedded-c-standard/audit_c_standard.py
python3 .opencode/skill/embedded-python-standard/audit_python_standard.py
python3 .opencode/skill/iot-readme-standard/validate_readme.py
python3 .opencode/skill/iot-banner-standard/validate_banner.py
python3 scripts/run_tests.py
python3 scripts/check_coverage.py
```

<br>

# Next
[picokit-49-fleet](https://github.com/mytechnotalent/picokit-49-fleet)

<br>

# License
[MIT License](https://github.com/mytechnotalent/picokit-48-gateway-dashboard/blob/main/LICENSE)
