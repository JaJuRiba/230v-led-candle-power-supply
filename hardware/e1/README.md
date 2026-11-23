# E1 — five-output isolated-DC bench supply

Open **[e1.kicad_pro](e1.kicad_pro)** in KiCad 10 and edit **[e1.kicad_sch](e1.kicad_sch)**. [KiCad plot (SVG)](preview/e1.svg) · [PNG](preview/e1.png) · [BOM with orderable parts](bom.csv) · [ERC](erc.rpt) · [electrical netlist](e1.xml). The [routed bench PCB, views and layout checks](board/README.md) accompany this schematic. Neither is a mains design. Use an **external isolated current-limited lab supply**. No AC input, reverse-polarity protection, independent output overvoltage cutoff, or automatic voltage identification exists here.

## Operating contract

- Set the source to **6.10 V nominal**; verify **6.05–6.15 V at J1 under load**, including ripple. Keep J1-to-U1 DC and ripple loss below 20 mV. Set **0.40 A** limit for full-load and single-fault tests; check the supply's limit and overshoot first. Use short leads; no hot-plugging. Open-air bench at 15–35 °C only.
- All six two-pin connectors use **1 = positive, 2 = common return**. They are unkeyed; label and meter them. The output returns are not isolated from one another.
- Change **JP1 only with power removed and the rail discharged**. Open/missing shunt → **3.0 V**. Shunt fitted → **4.5 V**. Every branch changes together. Do not mix loads rated for different voltages. Confirm the selected voltage at each empty output before attaching any device.
- Design load, not measured candle current: 20 mA typical and 50 mA continuous per output; five branches give 100/250 mA. Delivered power is 0.30/0.75 W at 3 V and 0.45/1.125 W at 4.5 V. These are **voltage outputs with fault limits**, not precision LED drivers. Never attach bare LEDs without suitable ballast or a driver.

## Regulator and tolerance budget

U1 is specifically **ST LD1117V**, adjustable standard-temperature TO-220, not the C-grade, a fixed 1117, or an LM317. Pin 1 ADJ, 2 OUT, 3 IN; **tab = OUT**, not ground. ST Fig. 2, Tables 1, 2, 8 and §7 specify the pinout, 15 V input maximum, 0–125 °C operating junction range, 800 mA class, and adjustable reference.[1] C1 is 1 µF X7R at IN. C2 is **22 µF ±10%, 16 V solid tantalum**, positive to OUT: 19.8 µF at its initial lower tolerance versus ST's 10 µF minimum. Do not silently substitute a ceramic-only regulator output network. C3–C7 are local switch bypasses, not replacements for C2.[1][3][4] Scope stability with the actual capacitors, wiring and loads.

`VSEL = Vref × (1 + R2/Rtop) + Iadj × R2`. R2 = 167 Ω; Rtop is 120 Ω open, or 120 Ω || 140 Ω = 64.615 Ω closed. Adding the parallel path raises the voltage without ever opening the feedback divider. At 1.25 V and 60 µA the calculated setpoints are **3.000 and 4.491 V**. The divider draws ≥10.18 mA even unloaded (ST minimum-load maximum 5 mA; reference characterized from 10 mA).[1]

|JP1|Calculated steady VSEL window|Minimum VIN−VSEL at U1|
|---|---:|---:|
|Open|2.923–3.077 V (rounded)|>2.95 V|
|Fitted|4.378–4.604 V (rounded)|≥1.426 V|

Corners use ST full-condition Vref 1.225–1.275 V, Iadj 0–120 µA, and independent ±0.20% resistor budgets (±0.10% initial plus ±25 ppm/K over 40 K from 25 °C). Verify resistor bodies stay within that temperature window; these calculations exclude transients, harness drops and contact resistance. Shunt resistance in series with R3 lowers the high setting. Keep feedback wiring short and Kelvin-sense U1 OUT and quiet return. R2 worst dissipation ~67 mW; use the listed 0805 precision parts rated ≥125 mW. R1/R3 are each below 15 mW. Worst high rail still leaves more than ST's **1.4 V reference-test differential** and **1.2 V max dropout at 800 mA**. A generic “6 V ±5%” adapter is *not* equivalent.[1]

For full continuous load, upper current budgets are 262 mA low and 272 mA high (load, feedback, switch bias and rounding). Worst U1 losses `(6.15 − VSELmin) × I` are **0.85 W low / 0.49 W high**. Using ST's TO-220 50 °C/W junction-to-ambient figure gives ~78/60 °C at 35 °C ambient; this is a board-dependent estimate, not a measured temperature.[1] A collapsed rail changes the calculation: even a 0.40 A source could deliver ~2.46 W into the regulator at near-zero output. Interrupt faults; do not rely on steady thermal shutdown. The live output tab must not touch grounded hardware.

## What each output protects against

U2–U6 are **TI TPS2553DBVR**, SOT-23-6 DBV, active-high, **non-latching** version. See pin-functions, recommended operating conditions, electrical/thermal tables and current-limit programming in the TI datasheet.[2] IN=1 and EN=3 connect to VSEL; GND=2, open-drain active-low FAULT=4 (intentionally NC), ILIM=5 via its own 210 kΩ to GND, OUT=6 to that branch alone. Do **not** substitute the different WSON pinout, active-low TPS2552, or latch-off `-1`. The 2.5–6.5 V operating range contains both rail windows; EN tied to IN clears the 1.1 V high threshold. Each IC has a dedicated 1 µF / 25 V ceramic across pins 1/2; put it directly at the pins (TI calls for ≥0.1 µF effective).[2][4] Keep ILIM traces short. No bulk branch output capacitor is fitted; start with short resistive-load leads and qualify the actual load capacitance and hot-plug behavior separately.

TI tabulates **110 / 130 / 150 mA min/typ/max at exactly 210 kΩ**. The 75 mA typical mode is ILIM shorted to IN, *not* what is fitted (its 50 mA minimum has no margin at our 50 mA rating). TI's equations, with kΩ as input and mA as output, give `25230/R^1.016` minimum and `22980/R^0.94` maximum. Allowing ±1.5% for the 1% programming resistors plus temperature drift gives **about 109–153 mA**; use **154 mA** for supply budgeting. This is a DC limit, not a guarantee on instantaneous short current; switch response is ~2 µs typical. DBV on-resistance max 135 mΩ implies ≤6.75 mV drop at 50 mA before connectors and leads.[2]

Four healthy 50 mA loads + one limited short + ~21 mA divider + ~0.65 mA switch bias = **~376 mA**, below 400 mA on paper. This does **not** guarantee selective protection; source foldback, wiring and startup may still dip the common rail. Multiple faults may collapse every output. A short at the high setting can dissipate ~0.71 W in a single DBV; at TI's 182.6 °C/W benchmark that implies ~130 °C rise. Expect thermal cycling, not indefinite uninterrupted current delivery.[2] Switch limits do not protect a 3 V candle against selecting 4.5 V, an LDO failure, or a destructive sub-threshold load. No branch FAULT monitoring is implemented.

## Exact net intent

`ref.pin` notation. With **b = 1…5**, let `u = b+1`, `c = b+2`, `r = b+3`. Repeated entries below apply for every b. No other connections are intended.

|Net|Member pins|
|---|---|
|VIN|J1.1, C1.1, U1.3|
|VSEL|U1.2, C2.1, R1.1, R3.1; Uu.1, Uu.3, Cc.1|
|ADJ|U1.1, R1.2, R2.1, JP1.2|
|SEL_LINK|R3.2, JP1.1|
|GND|J1.2, C1.2, C2.2, R2.2; Uu.2, Cc.2, Rr.2, Ju.2|
|OUTb (five separate nets)|Uu.6, Ju.1|
|LIMb (five separate nets)|Uu.5, Rr.1|
|Explicit no-connects|U2.4, U3.4, U4.4, U5.4, U6.4, each separate|

J1 is drawn as an externally driven supply connector (both pins drive their respective rails for ERC); this does not create an onboard supply. The shunt is a removable BOM accessory, not a short drawn between JP1 pads.

## Bench acceptance — not yet performed

1. Unpowered, inspect C2 polarity, IC orientations and header pin 1. Check for shorts; verify no continuity between distinct branch positives from a solder bridge. Start with JP1 open, no loads and a low source current limit (e.g. 50 mA). Power up, check VIN, VSEL and all five output voltages. Repeat after powering down and fitting JP1.
2. Use one then five **external dummy loads** per mode: 150 Ω / 60 Ω at 3 V, or 225 Ω / 90 Ω at 4.5 V for nominal 20 / 50 mA. Per-resistor nominal dissipation is 0.060 / 0.150 W or 0.090 / 0.225 W, respectively; use ≥0.5 W each, or electronic loads to set exact currents at the actual rail voltage. Set 0.40 A source limit for the five-load tests. Check U1 input differential, individual output drop, current, and steady temperatures at both settings.
3. Scope VIN, VSEL and a healthy output during start, stop and 0→250→0 mA steps. Check for overshoot, oscillation and load resets. Use bounded, momentary current-limited fault tests with dummy loads only. Measure the faulted current and all other rails; remove power if the source folds back, temperatures rise rapidly, or the healthy loads reset. Check recovery without a power cycle; do not leave a short applied.
4. Before testing a real candle, remove all cells; measure its polarity, operating and startup current on its intended source. Confirm permitted voltage and whether it depends on battery internal resistance. The calculated voltage windows are design predictions, not proof that any particular candle tolerates them.

## Verification and portability

KiCad CLI **10.0.8** loaded the schematic, exported the SVG and XML, and reported **0 errors / 0 warnings** with the local project and libraries. The isolated runtime also printed a missing API-schema startup diagnostic; the schematic commands themselves produced their outputs. The SVG was rasterized and inspected: all five stages, divider, connector labels and title block fit the A3 page. `check_nets.py` checked 28 placed parts, 77 pins, 15 named nets and five NCs against the drawn wiring, then independently compared the KiCad XML net memberships to the same intent. For PCB design-rule checks, see the board report linked above. No hardware measurements, safety approval or enclosure qualification are claimed.

From this folder, without regenerating the design:

```sh
kicad-cli sch erc --exit-code-violations -o erc.rpt e1.kicad_sch
kicad-cli sch export netlist --format kicadxml -o e1.xml e1.kicad_sch
python3 -c "import xml.etree.ElementTree as E; p='e1.xml'; t=E.parse(p); t.find('./design/source').text='e1.kicad_sch'; t.write(p,encoding='utf-8',xml_declaration=True)"
python3 check_nets.py e1.xml
kicad-cli sch export svg -o preview e1.kicad_sch
```

`generate.py` is optional source for the initial drawing and BOM; re-running it **overwrites hand edits**. The embedded symbols are also in the editable local `E1.kicad_sym`. The six assigned footprints are unmodified files from the [KiCad 10.0.0 footprint library](https://gitlab.com/kicad/libraries/kicad-footprints/-/tree/10.0.0), with [upstream license](footprints/LICENSE.md). The project footprint table resolves them locally; optional 3D models are not bundled. Pad numbers/library resolution were checked, not land-pattern assembly fit. Verify package drawings, actual components and harness orientation before any PCB work.

## Sources

[1] [ST LD1117 datasheet, DocID2572 Rev 38](https://www.st.com/resource/en/datasheet/ld1117.pdf)

[2] [TI TPS255xx datasheet, SLVS841](https://www.ti.com/lit/ds/symlink/tps2553.pdf)

[3] [KEMET T491C226K016AT specification](https://search.kemet.com/download/specsheet/T491C226K016AT)

[4] [KEMET C0805C105K3RACTU specification](https://search.kemet.com/component-documentation/download/specsheet/C0805C105K3RACTU)
