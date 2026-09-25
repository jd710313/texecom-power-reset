# Texecom Remote Power Reset

A small ESP32-C3 (Tasmota) board that sits inside a Texecom Premier Elite 64-W
housing and can remotely "hard power reset" the panel by briefly cutting both
its battery and 16VAC feeds.

> **Status:** Design rev A. **KiCad schematic done (ERC clean)**. PCB layout is next.

## Background

The panel occasionally raises an **"AUX 12V output failed"** fault. The only
way to clear it is to remove *all* power (battery and AC) and let the panel
restart. This board lets you do that remotely from Home Assistant.

The root cause (probably an overloaded or tripping AUX output) is being
investigated separately. This board is a remote recovery tool, not a fix.

## Requirements

### Panel

| # | Requirement |
|---|-------------|
| R1 | Panel: **Texecom Premier Elite 64-W** (built-in Ricochet wireless) |
| R2 | Firmware: **V6.05.03LS1** |
| R3 | Panel-side events after a reset (AC/battery fault logs, re-arming, etc.) are **out of scope**. They are handled manually. |
| R4 | AC presence and battery voltage are **already monitored** in Home Assistant through the Texecom integration, so this board doesn't monitor them. |

### Function

| # | Requirement |
|---|-------------|
| F1 | Remotely perform a "hard power reset" of the panel by cutting both the **battery 12V** feed and the **16VAC** feed at the same time. |
| F2 | Off duration: about **3 seconds** (Tasmota `PulseTime 30`). |
| F3 | Controlled from **Home Assistant over WiFi**, and reachable at all times. |
| F4 | The controller must **stay powered** while both panel feeds are cut. |

### Fail-safe

| # | Requirement |
|---|-------------|
| S1 | Panel feeds run through the relays' **NC (normally closed)** contacts. Coils are energised only during a reset, so a dead or unpowered board leaves the panel powered. |
| S2 | **Software timeout:** Tasmota `PulseTime`, so the relays release by themselves even if WiFi drops mid-reset. |
| S3 | **Hardware timeout:** a circuit between each GPIO and relay input limits the maximum on-time (target about 5–10 s). This covers a firmware hang with the GPIO stuck high, and boot-time GPIO glitches. |

### Power

| # | Requirement |
|---|-------------|
| P1 | Powered from the **12V lead-acid battery only**, about 7.2Ah, tapped *before* the battery relay so it is never switched off. |
| P2 | The whole system is backed by **solar**, so no low-battery cutoff is needed. |
| P3 | Regulator: **Pololu S9V11E2F5** (5V buck-boost, 2–16V in, under 0.2mA quiescent). It supplies 5V to the ESP32-C3 SuperMini (5V pin) and the relay module VCC. |
| P4 | Regulator input is **16V absolute max**. The battery floats at about 13.7V. The carrier must add **reverse-polarity protection**, a **bulk input capacitor** (≥33µF; 100µF used) and **transient protection**. |
| P5 | The battery tap on the carrier gets its **own small fuse** (about 0.5–1A, sized for the board's load). |
| P6 | Low power: Tasmota dynamic `Sleep` (WiFi stays connected). Target about 10–15mA average from the battery. |

### Hardware

| # | Requirement |
|---|-------------|
| H1 | MCU: **ESP32-C3 SuperMini**, socketed on female headers. |
| H2 | Relays: **REL-2CHAN-335V** 2-channel opto relay module ([Micro Robotics](https://www.robotics.org.za/REL-2CHAN-335V)). Songle SRD-05VDC-SL-C, 5V coil (about 70mA each), contacts 10A at 30VDC / 250VAC. Control header: CH1, CH2, GND, VCC, RGND (GND and RGND are joined on the module). |
| H3 | The relay module is **mounted separately**, next to the carrier PCB, and connected to it **only by wires**: the control lead, plus the COM/NC wires for both relays. |
| H4 | **All field wiring lands on the carrier PCB:** battery in, battery out to the panel, 16VAC in, and 16VAC out to the panel. Nothing from the field connects directly to the relay module. |
| H5 | **Relay control lead:** a 4-pin **JST-XH** on the carrier, going to a single **1×5 DuPont housing** on the module header (RGND position unused). The pinout is printed on the carrier silkscreen. |
| H6 | **Relay contact wiring:** carrier screw terminals (K1 COM/NC, K2 COM/NC) wired to the relay module's COM/NC screw terminals. |
| H7 | Screw terminals: **KF301-2P** (already on hand). 5.0mm pitch, 16A, 250V, 22–14 AWG, side entry, interlocking. |
| H8 | **Custom carrier PCB** (KiCad) holding the SuperMini socket, the S9V11E2F5, the hardware timeout circuits, the battery input protection and fuse, all field screw terminals, the relay contact terminals, and the JST-XH control connector. |
| H9 | Everything must fit **inside the panel housing**. Keep the carrier as small as practical. |
| H10 | The PCB is **CNC-milled in-house**, **double-sided** (FlatCAM with alignment pins, 30° V-bit with 0.1mm tip, 0.7mm tracks proven), from on-hand copper-clad board. There are **no plated through-holes, no solder mask and no silkscreen**. |

## Parts on hand

| Part | Source | Status in this design |
|------|--------|-----------------------|
| ESP32-C3 SuperMini | n/a | U3 |
| REL-2CHAN-335V relay module (**on hand**) | [Micro Robotics](https://www.robotics.org.za/REL-2CHAN-335V) | Off-board relay module |
| KF301-2P screw terminals, 5mm (10-pack) | [Micro Robotics](https://www.robotics.org.za/KF301-2P) | J1–J6. **Suitable:** rated 16A / 250V, against about 1.6A max on the battery path and a 16VAC supply. Uses 6 of the 10. |

## Wiring concept

```
                       ┌──────────────── Carrier PCB ────────────────┐
Battery +  ──► J1 BAT IN + ──┬────────────────► J5 K1 COM ═══wire═══► Relay 1 COM
                             │                                        Relay 1 NC ═══wire═══╗
                             └─ F1 → power supply (5V)                                     ║
Panel BATT + ◄── J2 BAT OUT + ◄──────────────── J5 K1 NC  ◄════════════════════════════════╝
Battery −  ──► J1 BAT IN − ───── GND ─────────► J2 BAT OUT − ──► Panel BATT −

16VAC ~A   ──► J3 AC IN A ────────────────────► J6 K2 COM ═══wire═══► Relay 2 COM
                                                                      Relay 2 NC ═══wire═══╗
Panel AC A ◄── J4 AC OUT A ◄─────────────────── J6 K2 NC  ◄════════════════════════════════╝
16VAC ~B   ──► J3 AC IN B ────────────────────► J4 AC OUT B ──► Panel AC B   (unswitched)

J7 JST-XH (CH1, CH2, GND, 5V) ═══lead═══► Relay module header
                       └─────────────────────────────────────────────┘
```

## Panel facts (Texecom INS176-15 installation manual)

From the *Premier Elite 12-W, 24-W & 48/64-W* sections:

| Item | Value |
|------|-------|
| Battery fuse | **F6, 1.6A electronic PTC** |
| AUX 12V, Digicom, Network 1, Bell/Strobe fuses | 0.9A electronic PTC each |
| Panel current consumption | 150mA |
| Maximum current available | 1.0A, plus 0.3A battery charge (7Ah setting) |
| **Battery kick-start** | "The panel will only become live when the AC Mains is connected or the Battery Kick-start button is pressed." |
| Power-up order | Connect the battery first, then AC. |
| Troubleshooting | "Remove ALL power (AC Mains and Battery) and then reapply", which is the same procedure this board automates. |

**Relay rating check:** each relay path carries at most about 1.6A (the battery PTC
limit) or the panel's AC input current. The SRD-05VDC-SL-C contacts are rated
10A. **OK.**

**Kick-start consequence:** the panel only restarts after a reset if **AC is
present**. A reset during a real AC outage would leave the panel **off** until
someone presses the kick-start button. The Home Assistant script therefore
checks that AC is present before it resets (see below).

---

## Design: rev A

### Block diagram

```
                         ┌──────────────────── Carrier PCB ───────────────────────┐
 Battery + ──J1+──┬── F1 ── D1 ──┬── C1/C2/D2 ── U1 S9V11E2F5 ──► +5V ──┬──────────────┼──► J7-4 VCC ─┐
                  │   PTC  rev.  │   bulk/TVS    (buck-boost)          │              │             │
                  │              │                                     └─ D3 ─► SuperMini 5V         │
                  └──────────────┼──► J5 K1 COM   (heavy traces, see §6)                │             │
 Battery − ──J1−─────────────────┴── GND ─────────────────────────────────────────────┼──► J7-3 GND ─┤
                                                                                      │             │
             +5V ──► U2 74HCT4538 VCC                                                 │             │
             GPIO3 ─ 1k ─┬──► U2 R1 (reset)      1Q ─► JP1 ─ 220Ω ───────────────────────┼──► J7-1 CH1 ─┤ REL-2CHAN-335V
                         └─ R/C delay ─► U2 A1 (↑) 1Q̅ ┘                                 │             │ (separate)
             GPIO4 ─ 1k ─┬──► U2 R2 (reset)      2Q ─► JP2 ─ 220Ω ───────────────────────┼──► J7-2 CH2 ─┘
                         └─ R/C delay ─► U2 A2 (↑) 2Q̅ ┘                                 │
                         └──────────────────────────────────────────────────────────────┘

 Switched paths (see the wiring concept above):
   J1 BAT+ ── J5 K1 COM ═► Relay 1 COM/NC ═► J5 K1 NC ── J2 BAT OUT+
   J3 AC A ── J6 K2 COM ═► Relay 2 COM/NC ═► J6 K2 NC ── J4 AC OUT A
   J1 BAT− ── J2 BAT OUT−, J3 AC B ── J4 AC OUT B     (straight through on the PCB)
```

### 1. Power input and protection

| Ref | Part | Purpose |
|-----|------|---------|
| J1 | KF301-2P screw terminal | BAT IN (+/−). The power supply taps J1+ on the PCB, **before** the relay path, so it is never switched. |
| F1 | **Resettable PTC fuse**, 1206 SMD, 0.5A hold / 1A trip, 24V (selected: Micro Robotics PTC05A24V) | Protects the new battery branch (not the panel's battery path). The board draws about 0.23A peak at 12V. After a short, it trips, then resets by itself once the fault is removed. |
| D1 | 1N5822 Schottky (DO-201AD, 3A 40V), in series | Reverse-polarity protection (about 0.3V drop, negligible at about 15mA). Micro Robotics stocks the 1N5822 rather than the 1N5819. |
| C1 | 100µF 25V radial electrolytic | Damps LC spikes from the battery leads, as Pololu recommends for the S9V11 (at least 33µF). |
| C2 | 100nF ceramic (radial, 5.08mm) | High-frequency decoupling. |
| D2 | P6KE18A TVS (DO-15) | Clamps larger transients. Its 15.3V standoff sits above the 13.8V float voltage, so no leakage. It is a last line of protection; C1 is the main LC-spike damper. |
| U1 | **Pololu S9V11E2F5** on a 1×4 header | 5V buck-boost, under 0.2mA quiescent. EN is left open (internal pull-up means always on). |
| C3 | 10µF 16V radial electrolytic | Output decoupling at the relay connector. |
| D3 | 1N5822 Schottky between +5V and SuperMini 5V | **Blocks USB backfeed.** The SuperMini's USB VBUS is tied straight to its 5V pin, so plugging in USB would otherwise push 5V from USB onto the relays and the Pololu output. The SuperMini still gets about 4.7V, which is fine for its 3.3V LDO. |

**Current budget (estimated):**

| State | 5V rail | From battery (at 13.6V, about 88% efficiency) |
|-------|---------|------------------------------------------|
| Idle, WiFi connected, Tasmota `Sleep` | about 25–35mA | **about 11–15mA** (0.3Ah/day, solar-backed) |
| Reset (both relays on for 3 s) | about 170mA + ESP | about 90mA for 3 s |
| Worst-case peak (WiFi TX + relays) | about 0.5A | about 0.23A |

### 2. Controller: ESP32-C3 SuperMini

- Plugs into **two 1×8 female headers**, so it can be removed for flashing or
  replacement.
- Relay control pins: **GPIO3 → CH1 (battery)** and **GPIO4 → CH2 (AC)**.
  - Neither is a strapping pin (unlike GPIO2, 8 and 9), nor a USB pin (18, 19)
    or the UART0 pin that prints the boot log (GPIO21).
  - They sit next to each other and to the 3V3 pin, which makes routing easy.
- R1 and R2: **100k pull-downs** on the 74HCT4538 side of R9/R10. They hold the
  resets low (relays off) while the ESP is booting, unpowered or removed.
- R9 and R10: **1k series resistors** between each GPIO and the 74HCT4538.
  They protect the ESP when the 5V rail is off. See the note in §3.
- Onboard blue LED (GPIO8, active low) is used as the Tasmota WiFi status LED.
- Keep the antenna end of the SuperMini at the board edge, with no copper under
  it, and away from the relay module and the panel's Ricochet receiver.

### 3. Hardware timeout: 74HCT4538 dual monostable (at 5V)

One chip (**TI CD74HCT4538E**, DIP-16) covers both channels. Each channel behaves as:

> **relay on = GPIO high AND less than T seconds since the GPIO went high**

| GPIO behaviour | Relay |
|----------------|-------|
| Normal 3 s `PulseTime` pulse | On for 3 s (T is longer, so it never cuts a normal pulse short) |
| GPIO stuck **high** (firmware hang mid-reset) | Released after **T about 5–9 s (7 s nominal)**. It cannot re-trigger without a new low-to-high edge. |
| GPIO low or floating (crash, reboot, ESP removed) | Released immediately, because the reset input R is low |
| Short boot glitch high | Only as long as the glitch (µs), so the relay doesn't respond |
| 5V lost | 74HCT4538 and relay coils both unpowered, relay released |

**Why a 74HCT at 5V (not a 74HC at 3.3V):** on the bench, the relay input
drew **4.77mA at 3.3V** (test 1b). That's at the limit of what a 74HC can
supply at 3.3V, and its output would sag. At 5V, the HCT output drives CH1
through a 220Ω resistor at about **5mA with CH1 at about 3.6V**, which gives
comfortable margin. HCT inputs use TTL thresholds (**high = 2.0V or above**,
low = 0.8V or below), so the ESP's 3.3V GPIO drives them reliably.

**Wiring for each channel.** TI pin names are used here; Nexperia's datasheet
swaps the letters A and B, but the **pin numbers and functions are identical**.

| CD74HCT4538 pin (ch1 / ch2) | Connection |
|-----------------------|-----------|
| R 3 / 13 (active-low reset) | Node N: GPIO through **R9/R10 1k**, with **R1/R2 100k** pull-down to GND at the chip side |
| A 4 / 12 (leading-edge / rising trigger) | Node N through **R5/R6 10k**, with **C7/C8 100nF** to GND. The 1ms delay makes sure reset is released **before** the trigger edge arrives. The Schmitt input handles the slow edge. |
| B 5 / 11 (trailing-edge trigger) | Tied to **VCC** (TI: "an unused B should be tied to VCC") |
| CX 1 / 15 | GND |
| RXCX 2 / 14 | REXT **R3/R4 1M** to +5V. CEXT **C5/C6 10µF X5R 1206** to GND through **R11/R12 100Ω** in series (TI's rapid power-down protection, Fig. 13). |
| Q 6 / 10 | Link **JP1 / JP2** (Q, fitted), then **R7/R8 220Ω**, then J7 CH1/CH2 |
| Q̅ 7 / 9 | Link **JP3 / JP4** (Q̅), **not fitted (DNP)** |
| VCC 16 | +5V, with **C4 100nF** decoupling |
| GND 8 | GND |

**Timing:** T = 0.7 × REXT × CEXT = 0.7 × 1M × 10µF ≈ **7 s nominal** (TI
datasheet: τ = 0.7·RX·CX, RX min 5k; noise susceptibility "may occur for
RX > 1M", so 1M is the upper limit). It needs to stay above 3.5 s (the longest
`PulseTime`) and, ideally, below 30 s. **Bench test 3** confirms the real value.
Tune it by lowering REXT or changing CEXT. Keep the RXCX traces short.

- **CEXT must be low-leakage.** With REXT at 1M the timing current is only about
  5µA, so an aluminium electrolytic (leakage in the µA range) would upset the
  timing badly. Use an **X7R/X5R ceramic**. Avoid **Y5V** ceramics, which can
  lose 50–80% of their capacitance.
- **Power-down protection:** TI requires protection when CX is 0.5µF or more.
  The 100Ω in series with CX limits the discharge current into pins 2/14 if 5V
  collapses quickly. It replaces the BAT85 diode used in the earlier design,
  because the TI part calls for a 1A diode, and any diode across a 1M resistor
  needs very low leakage.
- **Use 74HCT4538** (TI CD74HCT4538E from Communica). A 74HC4538 won't reliably
  read 3.3V inputs at 5V, and a CD4538 has too little output drive.

**ESP protection (does 5V reach the ESP?):** no. The ESP pins only drive the
74HCT4538's **inputs**, which are high-impedance CMOS gates. No 5V output
connects to any ESP pin, so the ESP never sees more than its own 3.3V.

The one corner case is the **5V rail being off while the ESP is powered**, for
example on USB for flashing (D3 blocks USB from the 5V rail). If the ESP then
drives a GPIO high, current could flow through the chip's input clamp diode into
the unpowered 5V rail. **R9/R10 (1k)** limit that to under 3mA, which is harmless
for both parts. They cost nothing in normal operation, because the HCT inputs
draw no current.

**JP1–JP4, trigger polarity:** each channel has two 0Ω link positions: JP1/JP2 = Q and JP3/JP4 = Q̅. **Fit only one per channel.** The relay module is **high-level
trigger (confirmed on the bench on 2026-09-25)**, so fit **JP1/JP2 (Q)** and leave **JP3/JP4 (Q̅)** empty.
A link is used instead of a header and jumper shunt because Micro Robotics has
no shunts in stock, and the setting never changes.

### 4. Connectors

**Screw terminals:** all **KF301-2P** (5.0mm pitch, 16A / 250V, 22–14 AWG).

| Ref | Label (silkscreen) | Pin 1 | Pin 2 | Wires to |
|-----|-------------------|-------|-------|----------|
| J1 | BAT IN | + | − | Battery |
| J2 | BAT OUT | + | − | Panel BATT terminals |
| J3 | AC IN | ~A | ~B | 16VAC supply |
| J4 | AC OUT | ~A | ~B | Panel AC terminals |
| J5 | K1 BAT | COM | NC | Relay 1 COM / NC |
| J6 | K2 AC | COM | NC | Relay 2 COM / NC |

**Control connector J7: JST-XH 4-pin (B4B-XH-A)**, silkscreened with the pinout:

| J7 pin | Signal | Relay module header |
|--------|--------|---------------------|
| 1 | CH1 (battery relay) | CH1 |
| 2 | CH2 (AC relay) | CH2 |
| 3 | GND | GND |
| 4 | +5V | VCC |
| n/a | n/a | RGND: empty position in the 1×5 DuPont housing |

The relay coils draw 5V from U1 through J7-4, not from the SuperMini.

### 5. Field wiring

| From | To |
|------|-----|
| Battery + / − | J1 BAT IN + / − |
| J2 BAT OUT + / − | Panel BATT + / − (the panel's original battery leads) |
| 16VAC supply ~A / ~B | J3 AC IN ~A / ~B |
| J4 AC OUT ~A / ~B | Panel AC terminals |
| J5 COM / NC | Relay 1 COM / NC |
| J6 COM / NC | Relay 2 COM / NC |
| J7 | Relay module control header (JST-XH to DuPont lead) |
| Relay **NO** terminals | Unused |

**Wire:** 0.5–0.75mm² (20–18 AWG) for the battery and AC runs, including
the four relay COM/NC wires. Keep the relay wires short, and use ferrules in the
screw terminals.

**Recommended:** an in-line fuse (about 3A) on the battery + lead, close to
the battery. The battery current now runs through the carrier PCB and two extra
wires, and a 7Ah SLA battery can deliver very high currents into a short before
the panel's own F6 PTC (which sits downstream) can do anything.

### 6. PCB

- 2-layer, **about 60 × 40mm** (estimated). The six 5mm terminals take up
  about 60mm of board edge, so the board has grown compared with the rev A
  estimate. The housing dimensions are still open.
- **Terminal layout:** the field terminals (J1–J4) sit along one long edge, and
  the relay terminals (J5, J6) and J7 along the opposite edge, facing the relay
  module. That keeps the wiring tidy and the heavy-current paths short.
- **Heavy-current traces** (J1→J5→J2 and J3→J6→J4, plus the BAT− and AC B
  straight-throughs): at least **2mm wide** on 1oz copper (about 3A at
  10°C rise), or copper pours, on both layers with stitching vias.
- **Clearance:** the 16VAC lines swing about ±23V relative to GND (the
  panel's bridge rectifier references them to 0V). Keep at least 1mm from logic
  traces. This is low voltage, so no mains-level creepage is needed.
- **Footprint pitch:** the KF301 is 5.0mm. Use a 5.0mm footprint (not 5.08mm)
  so that interlocked blocks line up.
- **Through-hole wherever possible:** axial resistors and diodes, radial
  capacitors, DIP-16 in a socket, 2.54mm headers. **1206 SMD is acceptable**
  (hand-solderable) and is used for F1.
- GND pour on both layers, except the antenna keep-out.
- 2 × M3 mounting holes.

### 6a. CNC-milling rules (H10)

**Process:** KiCad → Gerbers + Excellon drill → **FlatCAM** (isolation and drill
G-code) → CNC. **Double-sided**, with FlatCAM flip alignment using **alignment
pins**. Tool: **30° V-bit, 0.1mm tip**. The machine has milled 0.7mm tracks
reliably (see the example board), and all common drill sizes are available.

Milled boards have **no plated through-holes, no solder mask and no
silkscreen**, so the layout follows these rules:

| Rule | Why |
|------|-----|
| **Double-sided, but a top-layer connection is only allowed on pads that can be soldered on top.** Axial resistors and diodes, and radial capacitors mounted slightly raised, can be soldered on top. The IC socket, female headers, male header under the Pololu, JST, and KF301 terminals **cannot**, because their bodies cover the top pads. | There's no plating to carry a top trace to a bottom joint. |
| **Enforced in KiCad:** the footprints of the covered parts get **bottom-copper-only pads**, so neither manual routing nor the autorouter can connect to them on top. | Makes the rule impossible to break by accident, including by the autorouter. |
| **Vias** are drilled and fitted with a **wire link soldered on both sides.** Keep them few (target 10 or fewer), with 0.8mm drill and 2.0mm pads. **0Ω links** (RES-0E-50) can also serve as crossings. | Every via is a manual solder job. |
| **1206 SMD parts go on the bottom side.** | They're soldered on the same side as the through-hole joints. |
| **Traces 0.7mm by default** (proven on this machine; 0.6mm minimum where needed), **clearance at least 0.4mm**. Power paths at least 2mm, and 16VAC traces at least 1mm from logic. | Proven geometry for the 30°/0.1mm V-bit |
| **Oval, oversized pads** (for example 2.0 × 3.0mm for 0.8–1.0mm holes, bigger for terminals and the 1N5822s). | User's standard practice for easy hand soldering |
| **Extra clearance around pads:** a custom KiCad rule of **at least 0.8mm from any pad to other copper** (tracks at 0.4mm to each other), plus **component spacing** that keeps neighbouring pads and bodies well clear. | The user prefers wider isolation around pads for easy hand soldering and no solder bridges. FlatCAM's multi-pass isolation needs room to widen the cut around pads without eating into neighbouring traces. |
| **Drill sizes:** 0.8mm (resistors, small capacitors, vias), 1.0mm (headers, IC socket, JST, 0Ω links), 1.5mm (KF301, 1N5822 at 1.3mm leads, C1), 3.2mm (M3 mounting holes). | Few tool changes |
| **Leave the unused copper as a GND pour** on both layers, cleared around holes. | Faster milling and better grounding. The top GND pour is also a natural place for top-side joints. |
| **SuperMini antenna** overhangs the board edge. | No copper needs pocketing out from under it. |
| **Labels** (J1–J7 names, JST pinout, Q links, polarity) are **engraved into the copper** as V-bit text. | No silkscreen |
| After testing, **coat the board** (conformal coat or clear lacquer). | No solder mask, and the board lives in the panel for years. |

**Routing:** I place the parts and then try routing. If that's poor, use the
user's preferred autorouter, the **KiCad routing tools (Go implementation)**, with
the rules above as design rules.

### 6b. KiCad project

| File | Contents |
|------|----------|
| `texecom-power-reset.kicad_pro` / `.kicad_sch` | Project and schematic (A3, single sheet, label-connected nets) |
| `texecom-power-reset-schematic.pdf` | Schematic PDF export |
| `texecom-power-reset.kicad_sym` | Project symbols: ESP32-C3-SuperMini (from the esp32c3-button-led project), Pololu_S9V11E2F5 |
| `texecom-power-reset.pretty/` | Project footprints: ESP32-C3-SuperMini, Pololu_S9V11E2x (pin order VOUT, GND, VIN, EN per the Pololu drawing) |

**Reference designators** match BOM.md: U1 Pololu, U2 74HCT4538 (units A/B = channels 1/2, unit C = power), U3 SuperMini,
J1–J6 KF301 terminals, J7 JST-XH, F1 PTC, D1/D3 1N5822, D2 P6KE18A,
C1–C8, R1–R12, JP1/JP2 (Q links, fitted), JP3/JP4 (Q̅ links, DNP), MH1/MH2 M3 holes.

**Nets:** BAT_IN+ → F1 → BAT_FUSED → D1 → VIN_REG → U1 → +5V → D3 → +5V_MCU.
GPIO3_CH1 → R9 → RST1 (R1 pull-down, U2 pin 3) → R5 → TRIG1 (C7, U2 pin 4).
RXCX1 (R3 to +5V, C5 + R11 to GND). Q1 → JP1 → OUT1 → R7 → CH1 (J7-1). Channel 2 is identical with GPIO4, pins 9–14, R2/R4/R6/R8/R10/R12, C6/C8, JP2/JP4, and J7-2.

### 7. Tasmota configuration

Build: `tasmota32c3.bin` (flash through the SuperMini's USB-C, with the board
unpowered from the battery; D3 isolates USB from the relay rail).

`Configuration → Configure Module` (Generic ESP32-C3):

| GPIO | Function |
|------|----------|
| GPIO3 | Relay 1 (battery) |
| GPIO4 | Relay 2 (AC) |
| GPIO8 | LedLink_i (onboard LED, active low) |

Console:

```
Backlog PowerOnState 0; PulseTime1 30; PulseTime2 35; Sleep 100; FriendlyName1 Panel Battery Cut; FriendlyName2 Panel AC Cut
```

| Setting | Why |
|---------|-----|
| `PowerOnState 0` | Relays are **always off** after an ESP reboot or power-up. |
| `PulseTime1 30` | Battery cut for 3.0 s. |
| `PulseTime2 35` | AC cut for 3.5 s. Battery comes back first, then AC, which matches the manual's power-up order. The panel goes live when AC returns. |
| `Sleep 100` | Dynamic sleep for lower average current while WiFi stays connected. |

If the SuperMini has trouble holding a WiFi connection (a known issue with some
SuperMini antenna layouts), try `WifiPower 8.5`.

### 8. Home Assistant script (example)

Entity IDs are placeholders. Adjust them, and the AC-OK condition, to match the
Tasmota and Texecom integrations.

```yaml
script:
  texecom_hard_power_reset:
    alias: "Texecom hard power reset"
    mode: single
    sequence:
      # Never reset without AC: the panel would not restart without the kick-start button.
      - condition: state
        entity_id: binary_sensor.texecom_ac_ok        # placeholder
        state: "on"
      - action: switch.turn_on
        target:
          entity_id:
            - switch.texecom_reset_panel_battery_cut   # placeholder
            - switch.texecom_reset_panel_ac_cut        # placeholder
```

### 9. Bench tests before installing

1. **Relay module trigger polarity:** power the module VCC from 5V and GND.
   - **a. Polarity (5V is fine):** touch CH1 to **5V**, then to **GND**. If it
     clicks on 5V, it's **high-level trigger** (fit the Q links, JP1/JP2). If
     it clicks on GND, it's **low-level trigger** (fit the Q̅ links, JP3/JP4).
   - **b. 3.3V drive and current:** repeat with **3.3V** on CH1, with a
     multimeter (mA range) in series. It should still click, and draw under
     about 4mA. For a 3.3V source, use either:
     - the second rail of the breadboard supply, if it has a 3.3V/5V jumper
       per rail (MB102-type boards do), or
     - the ESP32-C3 SuperMini's **3V3** pin, with the SuperMini powered from
       USB and its **GND joined to the breadboard GND**.
2. **Normal pulse:** turn on `Power1` and check that the relay releases after 3.0 s.
3. **Hardware timeout:** set `PulseTime1 0` (no software timeout) and turn on
   `Power1`, so the GPIO stays high. The relay should release after about
   5–9 s (7 s nominal) and stay off. Afterwards, restore `PulseTime1 30`.
4. **Fail-safe:** unplug the SuperMini. Both relays must stay released (NC closed).
5. **USB isolation:** with the battery disconnected, plug in USB. The relay
   module must **not** power up.
6. **Idle current:** measure the battery current with WiFi connected. The
   target is about 15mA or less.

### Bill of materials

The full through-hole BOM and sourcing tracker (on hand / Micro Robotics /
elsewhere) is in **[BOM.md](BOM.md)**.

## Open items

- [ ] Free space inside the 64-W housing (dimensions still to come)
- [x] ~~Panel fuse ratings~~: the battery fuse is 1.6A PTC, which is well within the 10A relay rating
- [x] ~~Relay module trigger polarity~~: **high-level trigger** (clicks with CH1 at 5V, not at GND), so fit the **Q links (JP1/JP2)**. Tested 2026-09-25.
- [x] ~~Test 1b~~: at 3.3V on CH1 the relay switches and CH1 draws **4.77mA** (module VCC was also 3.3V, and the coil still switched). That's too close to what a 74HC at 3.3V can supply, so the design moved to the **74HCT4538 at 5V with 220Ω series resistors**. Tested 2026-09-25.
- [x] ~~KiCad schematic~~: done, ERC clean (2026-09-25)
- [ ] PCB layout (placement, routing, DRC), then Gerbers and drill files for FlatCAM

## Decisions log

| Decision | Reason |
|----------|--------|
| Pololu S9V11E2F5 instead of the XL7015 | The XL7015 (5–80V, 150kHz, non-synchronous) is inefficient at light load and bulky. The S9V11E2F5 has under 0.2mA quiescent current, a light-load mode, and a 10.9 × 16.5mm footprint. |
| Battery-only supply (no 16VAC diode-OR) | Rectified 16VAC peaks at about 22–25V, above the S9V11E2F5's 16V max. Solar backing makes battery drain a non-issue. |
| No low-battery cutoff | The system is solar-backed. |
| No AC or battery monitoring on the board | Already provided by the Texecom integration in HA. |
| Relay module mounted separately | The module isn't designed to stack on another PCB, and separate parts are easier to arrange in a cramped housing. |
| All field wiring lands on the carrier; the relay module is connected by wires only | One labelled place to connect everything. The battery tap for the power supply becomes a PCB trace, which removes the twin-ferrule or splice at relay COM. |
| KF301-2P terminals (on hand) | Rated 16A / 250V and accepts up to 14 AWG, well above the 1.6A battery path and 16VAC. |
| JST-XH on the carrier, 1×5 DuPont housing at the module | The module only has header pins. JST-XH latches and is polarised. A single 5-way DuPont housing can't be fitted offset by a pin. |
| Hardware timeout in addition to `PulseTime` | `PulseTime` is software and can't release a relay if the firmware hangs with the GPIO high. |
| 4538 monostable for the hardware timeout | One chip covers both channels. Its precise timing (0.7·R·C) beats a MOSFET-threshold RC, and its reset input gives "GPIO AND timer" logic without extra gates. |
| Battery restores 0.5 s before AC (`PulseTime1 30` / `PulseTime2 35`) | Matches the manual's power-up order (battery first, then AC). |
| HA script requires AC present | Without AC the panel won't restart unless the kick-start button is pressed. |
| D3 Schottky diode in the SuperMini 5V feed | The SuperMini's USB VBUS connects straight to its 5V pin. The diode stops USB from backfeeding the relay rail and regulator. |
| JP1/JP2 Q/Q̅ jumpers | The relay module's trigger polarity isn't documented, so the board supports both. |
| Through-hole parts wherever possible; 1206 SMD acceptable | User preference. 1206 is large enough to hand-solder. |
| F1 = PTC05A24V (1206, 0.5A hold) instead of the radial WDS250-500 (0.25A hold) | More margin over the 0.23A peak load, and it's in stock at Micro Robotics. |
| CEXT 10µF X7R with REXT 1M (was 22µF/680k) | 22µF through-hole ceramics are hard to find. 10µF with 1M gives T ≈ 7 s. |
| 1N5822 for D1/D3 | Micro Robotics stocks the 1N5822, not the 1N5819. |
| Sourcing pass (Micro Robotics stock check) | The 4538 and the P6KE18A TVS come from Communica (Micro Robotics doesn't carry them). C1 changed to 100µF, C2 to 100nF, C7/C8 to 100nF (1ms trigger delay), CEXT to 1206 X5R, and the JP headers to 0Ω links. All of these changes were made to use Micro Robotics stock. |
| Parts sourced from Micro Robotics (robotics.org.za) where possible | User preference. Tracked in BOM.md. |
| **74HCT4538E at 5V** instead of 74HC4538 at 3.3V, plus 220Ω output resistors (R7/R8) | Bench test 1b measured 4.77mA per relay input at 3.3V, too close to a 3.3V 74HC's drive limit. At 5V the HCT drives about 5mA with margin, and its TTL input levels still accept 3.3V from the ESP. It's also cheaper (R7.38 vs R13.50). |
| 1k series resistors (R9/R10) between the GPIOs and the 74HCT4538 | They limit the clamp-diode current if the ESP drives a GPIO high while the 5V rail is off (USB-only power). |
| 100Ω in series with CEXT (R11/R12) instead of a BAT85 diode across REXT | TI's recommended rapid power-down protection for CX of 0.5µF or more. It avoids adding diode leakage across the 1M timing resistor. |
| Kept the Pololu S9V11E2F5 over the on-hand XL4015 and MP4560 modules | XL4015: too large (54 × 23 × 18mm), high idle current, trimpot output. MP4560: acceptable (55V input, pulse skipping), but its trimpot output could drift and over-voltage the ESP, 74HCT4538 and relays. The Pololu has a fixed 5V output and under 0.2mA idle current. |
