# P1 assembly candidate — HOLD, not an order release

All 17 manufacturer/MPN pairs have exact JLC catalog IDs; the current schematic and PCB include both reviewed sourcing substitutions. [BOM](bom.csv) and [CPL](cpl.csv) cover 30 top SMT placements, none on bottom. [Procurement evidence](procurement.csv) links each manufacturer specification, JLC listing, LCSC SKU and read-only JLC inventory response. Quantities are pieces per board. Stock fields are JLC catalog snapshots (2026-11-23 about 12:40 UTC), not LCSC warehouse quantities, reservations or a quote. The numeric field names are JLC's; do not add presale to stock. Older staging data is not an input: R11 is **17.4 kΩ RT0805BRD0717K4L**, not 18.2 kΩ.

## What blocks release

|Reference|Finding|Action before release|
|---|---|---|
|R3|RESI PTFR0805B1K18P9, C47115959, implemented|Recheck live allocation; do not use the old YAGEO BOM.|
|U1|Analog Devices LT1963AEQ#TRPBF, C459702, implemented|Recheck live allocation; E-grade first-article limitations are documented in the sourcing notes.|
|R1, C2, R9|R1 stock 19, presale 0, minPurchaseNum 195; C2 stock 14, R9 stock 35|Confirm allocatable quantity for board count plus assembly loss. Recheck all 17 lines at quote; the working first-article quantity is five boards; confirm allocation in the live quote.|
|Front GND pour|Closed locally: the ZIP comes from the current frozen board; all four copper layers match two disposable refills.|Repeat CAM checks if the PCB changes.|
|CAM and placement|Local coordinate-level CAM inspection complete; no vendor DFM or placement preview.|Verify selected process, pad/drill registration and actual library placement, including pickup offsets; record signoff below.|

## Files and verification

[Fabrication ZIP](fabrication.zip): single 38 × 34 mm PCB, four copper layers F.Cu / In1.Cu / In2.Cu / B.Cu, two masks, front paste and silk, outline and separate PTH/NPTH drills. NPTH file has no hits; no bottom paste/silk. Target FR-4 JLC04161H-7628, 1.6 mm, nominal 1 oz outer / 0.5 oz inner. Confirm available stack, finish and tolerances with fabricator. No final process selection made.

[Inspection results](cam-inspection.json) are from reading the delivered Gerbers and drills, independently of KiCad. The outline is one closed 38 × 34 mm rectangle, no cutouts or mounting holes. All 78 Ø0.30 mm plated via hits register with Ø0.65 mm lands on all four copper layers. The back mask has no openings; the front has 105. The 104 front paste flashes omit all four open-jumper lands and split the U1 tab into four windows. The 2- and 10-way JST signal rows register across copper, mask and paste at Y = −108.7 mm, with four hold-down lands toward the cable edge. These are file checks, not a physical fit or process qualification.

**Refill closed locally.** The stable fill was adopted in the source PCB, and a new ZIP was exported from that saved board. Pad flashes, tracks, aperture macros and region paths agree on all four layers across both disposable refills.

[ERC](erc.rpt), [saved-board DRC/parity](saved-board.rpt), [first](refill.rpt) and [second disposable refill DRC](second-refill.rpt) reported zero violations. The CLI wrapper emitted a missing API-schema resource diagnostic; commands exited successfully. [Export report](review.json) identifies the actual unchanged source and procurement hashes; [checksums](SHA256SUMS) cover the candidate. No supplier upload or order.

## Assembly orientation review

Use [top assembly drawing](top.svg) and [bottom seen from below](bottom-viewed-from-below.svg). [Placement worksheet](placement-review.csv) gives each part's original anchor, rotation, side and expected pad 1. Coordinates are mm, absolute, top view (CPL Y = negative KiCad board Y). All CAD angles 0°; no JLC rotation correction assumed. Compare the widely separated U1 lead-1 and J2 pin-1 pads with CAM and vendor preview first; then check all other rows. U1 tab must land opposite the lead row; C2's band is **positive**. JST mouths face toward the Y=114 mm board edge, opposite the signal-pad row; align both hold-downs as well as pin 1. The CPL anchor is not proof of the pickup center. Leave approved XY/rotation blank until the exact part preview is reviewed, record reviewer and preview revision, and repeat after any correction.

JP1/JP2 are open copper-only links, not missing parts. Default low build: leave both open. No THT parts; housings, contacts, harness, case and external isolated supply are not PCBA lines. Only isolated 6 V DC at J1, never mains. Bench qualification remains separate from fabrication approval.
