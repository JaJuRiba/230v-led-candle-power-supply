# P1 harness — separate from the assembled PCB

Cable drawing for the standalone SELV controller. **Never route mains into this enclosure.** This is the pin list for harness construction and continuity testing, not evidence of a tested assembly. Use [the populated PCB interface](../hardware/p1/README.md#mechanical-and-harness-interface) as the numbering reference; the wire-side view may appear mirrored.

| Board header | Mating housing | Cavity assignment |
|---|---|---|
| J1 input | JST SHR-02V-S-B | 1 = +6 V from regulated isolated adapter, 2 = return |
| J2 outputs | JST SHR-10V-S-B | 1+/2− CH1; 3+/4− CH2; 5+/6− CH3; 7+/8− CH4; 9+/10− CH5 |

Per controller: 1 of each housing, 12 fitted SSH-003T-P0.2-H contacts (plus spares), two input conductors and five individually labelled output pairs. Select correctly terminated JST SH AWG28 leads or have a harness supplier crimp them; soldering wires directly to the PCB is not the intended assembly process. Use the [JST drawing](https://www.jst-mfg.com/product/pdf/eng/eSH.pdf) and check contact compatibility with insulation diameter. Transition from pigtails to the specified branch cable outside the case if needed; insulate and strain-relieve each splice. Never fit the larger branch wire in a crimp meant for AWG28. Order the correct low-voltage adapter mating jack/pigtail for the *exact* adapter selected; check actual polarity with a meter, not the colour or an assumed barrel convention. Candle-side mechanical battery adapters are model-specific, not supplied by JLCPCB and not qualified here.

**Assembly and incoming inspection (unpowered).** Label both ends `IN` or `CH1`–`CH5` and mark positive. Before inserting either plug into the controller, check each wire end against its numbered housing cavity and check insulation from every other conductor. In particular no channel positive may connect to another channel: a shared positive would defeat individual fault protection. Returns become common on the PCB only. Fit the cable retention parts and check that pulling on the external jacket does not move either board header. Do not pull on individual wires to unmate. Reject any open, swapped, bridged or loose termination.

**First energization.** No batteries or candles connected. Follow the P1 commissioning procedure using the external current-limited isolated lab supply and dummy loads. Verify polarity and voltage at the far end of every labelled pair; blank test results are not passes. Keep unused output pairs individually insulated. J1 is an input; never parallel it or any output with another supply. A candle that depends on battery internal impedance is not approved by this harness test.
