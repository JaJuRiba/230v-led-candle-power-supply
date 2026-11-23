# E1 bench board — routed, not built

[Editable PCB](../e1.kicad_pcb) · [Front copper and silkscreen](front.svg) · [Rear copper, viewed through the board from above](back.svg) · [KiCad DRC and parity report](drc.rpt)

The 44 × 66 mm, two-layer board has five switched outputs and a shared rear ground plane. J1 is the input; J2–J6 are outputs 1–5. The square pad marked `+` is pin 1 on each of these six headers; pin 2 is common return. J1 requires an isolated, current-limited 6.10 V nominal DC bench source. **Never connect mains.** The U1 tab is electrically connected to VSEL, not ground.

Remove power and let the rail discharge before changing JP1. Open selects 3.0 V on every output; fitted selects 4.5 V on every output. **E1 has no output overvoltage protection.** Check the voltage on every empty output before attaching a load. Follow the [operating limits and dummy-load procedure](../README.md) before testing any candle.

## Verification

KiCad CLI 10.0.8 refilled the ground plane and saved the board. A second DRC run on the saved file found zero violations, zero unconnected pads and zero schematic parity findings. The five FAULT pins are deliberately separate no-connects. Board footprints come from the six project-local library definitions and are linked to the schematic component UUIDs. The independent net-intent check passed for the schematic and `e1.xml`.

Recheck from `hardware/e1` without rewriting the board:

```sh
kicad-cli pcb drc --schematic-parity --severity-all --exit-code-violations -o board/drc.rpt e1.kicad_pcb
python3 check_nets.py e1.xml
```

These are layout checks, not measurements. Package fit, polarity on assembled hardware, regulator stability, voltage drop, thermal behavior and branch fault response remain untested. Open-bench review only; no fabrication release.
