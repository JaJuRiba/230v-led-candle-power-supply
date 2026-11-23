# P1 five-board first article: sourcing override, not a release

Use [procurement.csv](procurement.csv) with the **revised hardware/p1**, not the older candidate or staging BOM. It is a complete input mapping for `manufacturing/p1-tools/review.sh`; the other 12 lines retain the prior candidate evidence. Recheck all 17 at quote. No stock has been purchased or allocated.

## Two design changes, no reroute

- **U1:** Replace Analog Devices LT1963AIQ#TRPBF (C665716, stock 0) with **LT1963AEQ#TRPBF (C459702)**. The same-I-grade non-TR LT1963AIQ#PBF (C117221) also reported 0; E-grade non-TR LT1963AEQ#PBF (C20415348) reported 87. Use only the selected TR ordering. [ADI ordering table, Q pinout, electrical tables and Note 3](https://www.analog.com/media/en/technical-documentation/data-sheets/lt1963a.pdf): same adjustable 1.21 V reference, 1.5 A, same five-lead DDPAK, SHDN/IN/GND/OUT/ADJ pins 1–5, grounded tab, lead-free tape/reel. E and I have the same −40 to +125 °C operating junction range and applicable electrical limits, **not the same production test assurance**: E is 100% tested at 25 °C, endpoints assured by design/characterization/correlation; I guaranteed across range. E accepted for the indoor P1 first article, not an industrial-screening equivalence. No change to feedback, headroom or thermal budget. Reject fixed-output suffixes and other packages.
- **R3:** Replace YAGEO RT0805BRD071K18L (C865252, stock 0) with **RESI PTFR0805B1K18P9 (C47115959)**. [YAGEO baseline](https://yageogroup.com/component-documentation/download/specsheet/RT0805BRD071K18L); [RESI C16003 specifications, dimensions and ordering key](https://www.resistor.today/upload/soft/datasheet/PTFR.pdf). Both thin film, 1.18 kΩ, ±0.1%, ±25 ppm/K, 150 V maximum working voltage, −55 to +155 °C, two-terminal 0805. RESI 2.00 × 1.25 mm nominal; B = 0.1%, 1K18 = 1180 Ω, P = 25 ppm/K, 9 = standard. Power at 70 °C is **0.130 W vs 0.125 W**, not a downgrade; retain the original design limit and derating. No change to nominal high-mode divider or its tolerance allowance. The [JLC exact listing](https://jlcpcb.com/partdetail/RESI-PTFR0805B1K18P9/C47115959) agrees; a nearby E96 resistance or looser TCR is not allowed.

## Quantity decision (pieces)

JLC part-detail API snapshot, 2026-11-23 UTC; per-line source URLs in CSV. Each ref fits once per board. Screen with `max(5, leastPatchNumber) + lossNumber`; use the actual assembly quote if it requires more. Public stock and presale are **not additive**. Purchase minima are not placement minima.

|Ref / JLC ID|Public / presale|Purchase min|Placement min / loss|Five-board screen|Action|
|---|---:|---:|---:|---:|---|
|U1 C459702|1664 / 1652|1|0 / 0|5|Select exact TR part; reserve 5 or quote requirement.|
|R3 C47115959|4213 / 4213|1|5 / 2|7|Reserve at least 7.|
|R1 C865262|19 / 0|195|5 / 4|9|Try public assembly allocation of 9; do **not** assume a nine-piece pre-order. If not allocated use the exact-part route below.|
|C2 C600518|14 / 10|1|5 / 0|5|Pre-order 5 now if still offered, or match 5 public pieces at quote. Keep the polarized KEMET T491C226K016AT.|
|R9 C865634|35 / 25|1|5 / 4|9|Pre-order 9 if offered, or match 9 public pieces. Keep YAGEO RT0805BRD0771K5L.|

**R1 fallback:** In Parts Manager → Order Parts → Global Sourcing search exact `RT0805BRD071K47L`. Request 10 cut-tape pieces (or greater supplier/assembly minimum); distributor identifiers **DigiKey YAG1813CT-ND**, **Mouser 603-RT0805BRD071K47L** ([distributor cross-reference](https://thepartsdirect.com/part/rt0805brd071k47l~yageo), not a live quote). If the service cannot quote it, obtain JLC consignment acceptance, feeder/package and quantity instructions *before* buying/shipping the exact cut tape. Use the same exact-MPN global route for C2/R9 if their small public pools disappear. No generic substitutions or hand-edited BOM rows.

[JLC Global Sourcing instructions](https://jlcpcb.com/help/article/how-to-use-jlcpcb-global-sourcing-parts-service) and [matching My Parts](https://jlcpcb.com/help/article/how-to-use-my-own-parts-for-pcb-assembly-order): wait for review and warehouse receipt, confirm usable private quantity, then match MPN, ref and JLC/private ID at assembly checkout. Do not count public stock toward a global/consigned shortfall for the same line. A cart, supplier listing or request is not a reservation. Stop if allocation, identity or placement is uncertain.

After owner fill review, rebuild to a **new** directory from repository root: `sh manufacturing/p1-tools/review.sh hardware/p1/p1.kicad_pcb manufacturing/p1-sourcing/procurement.csv <new-review-directory>`. Do not upload the older candidate. Vendor DFM, placement preview (particularly U1 tab and C2 polarity), front-fill approval and bench tests are separate gates.
