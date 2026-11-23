# P1 product design contract — not an order release

The assembly target is a low-voltage candle controller with a closed printed enclosure, a polarized wiring harness and a separately purchased, isolated mains adapter. The Shelly controls power upstream. P1 deliberately does not place 230 V on the custom board or in its printed enclosure. This is an alternative to the original single flush-box integration goal, not evidence that the latter has been met. A recessed mixed-voltage installation is outside this design. Retain E1 as a separate open-bench reference; never substitute E1 files for P1 in an order.

## Inputs frozen for design, not measured limits

- One to five single-LED candle loads with cells removed; all branches share one nominal voltage, 3.0 or 4.5 V. No support claim for bare LEDs, moving-flame mechanisms or coin-cell loads relying on cell impedance. Design budget 20 mA nominal and 50 mA continuous per branch. Minimum assumed total output capacity 250 mA; nominal maximum delivered load power 1.125 W.
- Indoor dry location, accessible for commissioning; choose 35 °C still-air ambient as an initial thermal test condition, not a certified operating rating. No moisture ingress rating. No PCB copper or printed wall is a mains isolation barrier.
- Target PCB envelope 38 × 34 × 1.6 mm, subordinate to routing, thermal and mating-clearance checks. The circuit and enclosure must share a coordinate system and the same released outline. Cable bends and connector extraction need an explicit check, not just a collision-free model of an empty board.
- For a first harness design, assume at most 1 m one-way per output, copper conductors at least 0.14 mm². Recheck the connector contact crimp range, temperature, cable resistance and polarity against the actual harness. Output voltage is evaluated at the candle, not just at the regulator.
- Document electrical connector housings, contacts and mating-cable assemblies separately from PCB parts: JLC assembly of headers does not supply a finished harness. Include enclosure fasteners, strain relief, external adapter and any panel labels in the system BOM.

## Evidence required before calling it orderable

1. Electronics: component data-sheet checks; min/max input at load, worst-case output voltages and trip thresholds, aggregate single-fault current and thermal estimates; recorded ERC, saved-board DRC and schematic parity.
2. Mechanics: compare actual PCB and part envelopes against the closed lid, supports, fastening and cable paths. Declare any absent 3D model and tolerances. Distinguish a CAD fit from a measured H2D print and assembled fit.
3. Order package: revision-specific layer stack, Gerber/drill archive, BOM and CPL matched by reference/footprint, exact assembly part IDs or explicit separately sourced parts, orientation review, top/bottom assembly drawings, assembly options, printable enclosure and harness drawing. Document required manual assembly. Do not place or pay for an order.
4. First article vs product: CAD/DRC alone cannot prove JLC stock/approval, fault transient voltage, candle compatibility, connector retention, enclosure temperature or regulatory compliance. First-article orderability and approval for continuous operation/installation are different decisions. No pass values may be entered without evidence.
