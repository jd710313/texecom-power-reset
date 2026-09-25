# BOM and Sourcing Tracker: Texecom Remote Power Reset

Through-hole wherever possible; **1206 SMD is acceptable**. Preferred supplier:
**Micro Robotics** ([robotics.org.za](https://www.robotics.org.za)). Anything
they don't carry comes from **Communica** ([communica.co.za](https://www.communica.co.za)).

**Source column:** **On hand** (already have it) · **Micro Robotics** · **Communica**. The **Stock** column shows Micro Robotics or Communica availability at the time of checking.

> Stock was checked on **2026-09-25** on the Micro Robotics product pages
> (Centurion / Stellenbosch) and on Communica's site. Stock changes, so
> re-check before ordering. Communica's "available" flag is from their web
> shop. Their note says stock is held at the Samrand branch only.

## Carrier PCB

| Ref | Qty | Part | Source | Code | Pack / price | Stock (Centurion / Stellenbosch) | Notes |
|-----|-----|------|--------|------|--------------|-------------------|-------|
| U1 | 1 | Pololu S9V11E2F5 5V buck-boost | **Micro Robotics** | [5713](https://www.robotics.org.za/5713) | 1 / R80 | In stock / Limited | |
| U2 | 1 | **74HCT4538E** (TI CD74HCT4538E) dual monostable, DIP-16, runs from **5V** | **Communica** | [74HCT4538E](https://www.communica.co.za/products/74hct4538e) | 1 / R7.38 | Available | **Not carried by Micro Robotics.** Must be **HCT** (TTL inputs accept the ESP's 3.3V). Not 74HC4538, not CD4538. Consider buying 2 (one spare). |
| U2 socket | 1 | IC socket 16-pin | **Micro Robotics** | [IC-SOC-16P](https://www.robotics.org.za/IC-SOC-16P) | 4 / R7 | In stock / In stock | |
| U3 | 1 | ESP32-C3 SuperMini | **On hand** | n/a | n/a | n/a | |
| H1 | 2 | Female header 1×8, 2.54mm (SuperMini socket) | **On hand** | [HFST-08-TH254](https://www.robotics.org.za/HFST-08-TH254) | 10 / R12 | In stock / In stock | On hand. Needs two 1×8 female strips (or longer strips cut down; cutting a female header costs one position). |
| H2 | 1 | Male header, 2.54mm (1×4 for U1, cut from a 40-way strip) | **On hand** | [HMST-40-TH254](https://www.robotics.org.za/HMST-40-TH254) | 10 / R16 | In stock / In stock | On hand. Pololu doesn't include header pins. |
| J1–J6 | 6 | KF301-2P screw terminal, 5.0mm | **On hand** | [KF301-2P](https://www.robotics.org.za/KF301-2P) | 10 / R14 | In stock / In stock | 10-pack on hand |
| J7 | 1 | JST-XH 4-pin PCB header | **Micro Robotics** | [JST-XH-4P-300](https://www.robotics.org.za/JST-XH-4P-300) | 4 kits / R22 | In stock / In stock | The kit includes a 4-pin JST-XH cable (30cm, bare wire end) **plus the mating PCB headers** (straight and right-angle). This one kit covers J7 and the lead. |
| F1 | 1 | PTC resettable fuse 0.5A hold / 1A trip, 24V, **1206 SMD** | **Micro Robotics** | [PTC05A24V](https://www.robotics.org.za/PTC05A24V) | 10 / R10 | In stock / In stock | |
| D1, D3 | 2 | **1N5822** Schottky, 3A 40V, DO-201AD | **Micro Robotics** | [1N5822-TH](https://www.robotics.org.za/1N5822-TH) | 10 / R16 | In stock / In stock | Replaces 1N5819 (not carried). Larger body and 1.3mm leads; the PCB footprint will be DO-201AD. |
| D2 | 1 | **P6KE18A** TVS, unidirectional, 15.3V standoff | **Communica** | [P6KE 18A](https://www.communica.co.za/products/p6ke-18a) | 1 / R4.50 | Available | Micro Robotics only has the P6KE50A (wrong voltage). Optional part: the board works without it. **Don't** use the bidirectional "CA" versions or anything under 15V standoff. |
| C1 | 1 | Electrolytic **100µF 25V** radial | **On hand** | [CAP-100UF-25V](https://www.robotics.org.za/CAP-100UF-25V) | 10 / R8 | In stock / In stock | On hand, from the [CAPKIT](https://www.robotics.org.za/CAPKIT) (100µF **35V**, 6 × 7mm). 35V is fine. |
| C2, C4, C7, C8 | 4 | Ceramic **100nF**, radial 5.08mm | **On hand** | [100NF-P508](https://www.robotics.org.za/100NF-P508) | 25 / R6 | In stock / In stock | On hand, from the CAPKIT (100nF 50V, 5.08mm pitch). The kit has 5 and 4 are needed. |
| C3 | 1 | Electrolytic 10µF 35V radial | **On hand** | [CAP-10UF-35V](https://www.robotics.org.za/CAP-10UF-35V) | 10 / R10 | In stock / In stock | On hand, from the CAPKIT (10µF **50V** electrolytic, 4 × 7mm). |
| C5, C6 | 2 | **Ceramic 10µF 25V X5R, 1206 SMD** (CEXT, sees 5V). **The CAPKIT's 10µF electrolytic is not suitable here.** | **Micro Robotics** | [CL31A106KAHNNNE](https://www.robotics.org.za/CL31A106KAHNNNE) | 100 / R18 | In stock / In stock | Samsung CL31A = X5R. Low leakage, so it's suitable for the timer. |
| R1, R2 | 2 | Resistor 100k ¼W | **Micro Robotics** | [RES-100K-50](https://www.robotics.org.za/RES-100K-50) | 50 / R16 | In stock / In stock | 5% carbon film |
| R3, R4 | 2 | Resistor **1M** ¼W (REXT) | **Micro Robotics** | [RES-1M-50](https://www.robotics.org.za/RES-1M-50) | 50 / R16 | In stock / **No stock** | Order from Centurion. 5% carbon film is fine; the timeout only needs to stay roughly between 4 and 30 s. |
| R5, R6 | 2 | Resistor 10k ¼W | **Micro Robotics** | [RES-10K-025](https://www.robotics.org.za/RES-10K-025) | 50 / R16 | In stock / In stock | |
| R7, R8 | 2 | Resistor **220Ω**, **1206 SMD** (output series, limits CH1 current) | **Micro Robotics** | [RES-220-1206](https://www.robotics.org.za/RES-220-1206) | 50 | In stock / In stock | The through-hole 220Ω ([RES-220E-025W](https://www.robotics.org.za/RES-220E-025W)) is out of stock |
| R9, R10 | 2 | Resistor **1k**, **1206 SMD** (GPIO series protection) | **Micro Robotics** | [RES-1K-1206](https://www.robotics.org.za/RES-1K-1206) | 100 | In stock / In stock | The through-hole 1k ([RES-1K-025W](https://www.robotics.org.za/RES-1K-025W)) is out of stock. [RES-560E-025W](https://www.robotics.org.za/RES-560E-025W) (560Ω through-hole, in stock) also works. |
| R11, R12 | 2 | Resistor **100Ω**, **1206 SMD** (in series with CEXT, power-down protection) | **Micro Robotics** | [RES-100-1206](https://www.robotics.org.za/RES-100-1206) | 50 | In stock / In stock | The through-hole 100Ω ([RES-100E-025W](https://www.robotics.org.za/RES-100E-025W)) is out of stock |
| JP1, JP2 (JP3, JP4 DNP) | 2 | **0Ω link** ¼W. Fit JP1/JP2 (Q). JP3/JP4 (Q̅) stay empty (high-level trigger relays). | **Micro Robotics** | [RES-0E-50](https://www.robotics.org.za/RES-0E-50) | 50 / R16 | In stock / In stock | Replaces the header and jumper shunt ([CCC01505C-20](https://www.robotics.org.za/CCC01505C-20) is out of stock) |
| PCB | 1 | Double-sided copper-clad board, **CNC-milled** by the user (isolation routing) | **On hand** | n/a | n/a | n/a | No plating, solder mask or silkscreen. See the README section on CNC-milling rules. |

## Relay module and wiring

| Item | Qty | Source | Code | Pack / price | Stock (C / S) | Notes |
|------|-----|--------|------|--------------|---------------|-------|
| REL-2CHAN-335V relay module | 1 | **On hand** | [REL-2CHAN-335V](https://www.robotics.org.za/REL-2CHAN-335V) | n/a | (No stock / No stock) | On hand |
| Control lead: JST end | 1 | **Micro Robotics** | [JST-XH-4P-300](https://www.robotics.org.za/JST-XH-4P-300) | (same kit as J7) | In stock / In stock | Use one cable from the kit |
| Control lead: relay end, 5-way DuPont shell | 1 | **Micro Robotics** | [DPSHELL-5P](https://www.robotics.org.za/DPSHELL-5P) | 50 / R16 | In stock / In stock | RGND position left empty |
| Control lead: DuPont female terminals | 4 | **Micro Robotics** | [DUP-PIN-FEM-100](https://www.robotics.org.za/DUP-PIN-FEM-100) **or** [DUP-4P-254-L200](https://www.robotics.org.za/DUP-4P-254-L200) | 100 / R28 · 4 / R16 | In stock / In stock (both) | **Option A:** crimp pins onto the JST cable's bare ends (needs a DuPont crimper; [IWS-2820M](https://www.robotics.org.za/IWS-2820M) is out of stock). **Option B (no crimper):** take a pre-made 4-way DuPont cable, lift the terminals out of one housing into the 5-way shell, then cut the other end and solder it to the JST cable. |
| Heat shrink 3mm | 1 | **On hand** | [HEAT-3MM-BLK](https://www.robotics.org.za/HEAT-3MM-BLK) | 10 × 200mm / R8 | In stock / In stock | On hand. Used for the option B solder joints on the control lead. |
| Hook-up wire 18 AWG, red and black | 1 | **Micro Robotics** | [AWG18-UL1007-RB-5M](https://www.robotics.org.za/AWG18-UL1007-RB-5M) | 5m each / R36 | In stock / In stock | Battery, AC and relay COM/NC runs. Label the relay wires. |
| Bootlace ferrules | 1 kit | **On hand** | [CRIMP-400](https://www.robotics.org.za/CRIMP-400) | 400 / R118 | In stock / In stock | On hand. Ferrules need to suit 18 AWG (0.75–1.0mm²) wire, and a ferrule crimper is needed. |
| In-line blade fuse holder | 1 | **Micro Robotics** | [FUSE-INLINE-40A](https://www.robotics.org.za/FUSE-INLINE-40A) | 1 / R28 | In stock / In stock | **Recommended**, on battery + near the battery |
| Blade fuse 3A | 1 | **Micro Robotics** | [BLADE-3A](https://www.robotics.org.za/BLADE-3A) | 10 / R15 | In stock / In stock | |
| M3 nylon spacers, 15mm, with screws and nuts | 4 sets | **Micro Robotics** | [SPACE-M3-L15-KIT](https://www.robotics.org.za/SPACE-M3-L15-KIT) | 20 / R22 | In stock / In stock | The 10mm kit ([SPACE-M3-L10-KIT](https://www.robotics.org.za/SPACE-M3-L10-KIT)) is out of stock |

## Order summary

**Micro Robotics:** 5713, IC-SOC-16P, JST-XH-4P-300, PTC05A24V, 1N5822-TH, CL31A106KAHNNNE, RES-100K-50, RES-1M-50 (Centurion),
RES-10K-025, RES-0E-50, RES-220-1206, RES-1K-1206, RES-100-1206, DPSHELL-5P, DUP-PIN-FEM-100 or DUP-4P-254-L200,
AWG18-UL1007-RB-5M, FUSE-INLINE-40A, BLADE-3A,
SPACE-M3-L15-KIT.

**Communica:** 74HCT4538E (×1, or ×2 as a spare), P6KE 18A (×1).

**PCB:** milled in-house from on-hand copper-clad board.

## Design changes made to fit available stock

| Was | Now | Why it's fine |
|-----|-----|---------------|
| 1N5819 (D1, D3) | 1N5822 | Same job, higher current rating. Only the footprint changes (DO-201AD). |
| C1 47µF 25V | 100µF 25V | More bulk capacitance damps spikes better. The inrush at hook-up is limited by F1 and D1. |
| C2 1µF | 100nF | C1 already provides bulk capacitance. 100nF handles high-frequency decoupling. |
| C7, C8 1nF (10µs trigger delay) | 100nF (1ms delay) | The delay only needs to be longer than the reset release. 1ms of relay delay doesn't matter, and the Schmitt input handles the slow edge. |
| CEXT 10µF radial X7R | 10µF 1206 X5R (Samsung) | No through-hole 10µF ceramic available. 1206 is hand-solderable. |
| JP1/JP2 headers + shunt | 0Ω link, fit Q or Q̅ | Shunts are out of stock, and the setting never changes after the bench test. |
| 74HC4538 at 3.3V | **74HCT4538E at 5V** (Communica) + 220Ω output resistors | Bench test 1b: the relay input draws 4.77mA at 3.3V, too close to a 3.3V 74HC's limit. The HCT at 5V has margin, and its TTL inputs accept the ESP's 3.3V. |
| BAT85 DEXT diodes (D4, D5) | 100Ω in series with CEXT (R11, R12) | TI's recommended power-down protection. It adds no leakage across the 1M timing resistor. |
| n/a | 1k series resistors R9, R10 | Protect the ESP if it drives a GPIO high while the 5V rail is off (USB-only power) |
| P6KE18A (Micro Robotics) | P6KE 18A (Communica) | Micro Robotics doesn't carry it. It's optional anyway. |

## Micro Robotics alternatives considered and rejected

| Part | Why not |
|------|---------|
| [555-DIP](https://www.robotics.org.za/555-DIP) instead of the 74HCT4538 | Would need 2 × 555 plus an edge-detect transistor stage per channel. A bipolar NE555 also draws about 3–6mA each, which would roughly double the idle current. |
| [T10UF-35V](https://www.robotics.org.za/T10UF-35V) tantalum for CEXT | 3.5µA max leakage, comparable to the 3µA timing current. Use the Samsung ceramic instead. |
| [P6KE50A](https://www.robotics.org.za/P6KE50A) TVS | The listing is contradictory (titled "5V", part number means 50V). Either value is wrong for a 12V battery. |
| [MF-NSMF050-2](https://www.robotics.org.za/MF-NSMF050-2) PTC | Rated 13.2V, below the 13.8V battery float voltage. |
| [WDS250-500](https://www.robotics.org.za/WDS250-500) PTC | Through-hole, but only 0.25A hold. Kept as a fallback for F1. |
