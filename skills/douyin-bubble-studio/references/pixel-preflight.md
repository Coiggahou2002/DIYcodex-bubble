# Pixel spacing preflight

`scripts/edge_spacing.py` is a deterministic preflight helper for transparent static PNGs. It samples the alpha channel at 1/3 and 2/3 of each edge, matching the wording in the platform error “顶部，左/右1/3距离，到有像素距离”.

It checks:

- top and bottom clearance at x = 1/3 and 2/3, each against 36 px;
- left and right clearance at y = 1/3 and 2/3, each against 42 px;
- image dimensions against the static 198×162 px upload limit.

For any new bubble, also declare the planned nine-slice rectangle with `--anchor-rect LEFT TOP RIGHT BOTTOM`. The checker then requires non-transparent pixels continuously along all four declared boundaries. This is the hard local guard against a missing top/right/left/bottom line; it prevents an organic character contour or an empty gap from being mislabeled as a stretch edge.

The script regards pixels with alpha greater than 8 as visible by default. Use `--alpha-threshold 0` to model a strict “any nonzero alpha counts” interpretation.

## Commands

```bash
# Human-readable diagnosis
python3 scripts/edge_spacing.py bubble.png

# JSON for a calling tool
python3 scripts/edge_spacing.py bubble.png --json

# A non-destructive, safe 2px-style whole-image nudge
python3 scripts/edge_spacing.py bubble.png --repair --out bubble-nudged.png

# Required for new assets: verify explicit four-sided stretch anchors
python3 scripts/edge_spacing.py bubble.png --anchor-rect 44 34 174 125
```

## Repair boundary

The repair is deliberately narrow. If only top samples are 38 px against a 36 px limit, it moves the complete RGBA image up two pixels, then reruns the measurement. It does not use AI generation, liquify, content synthesis, or lossy compression.

If both top and bottom (or both left and right) require moving outward, translation cannot solve the conflict. The script refuses to crop visible pixels, reports the conflict, and exits nonzero. In that case choose one of these intentional design changes: relocate fixed decoration into a closer corner cap, enlarge a plain bubble body, or revise the nine-slice layout.

This is a local approximation of the upload checker, not a substitute for the platform’s final upload preview. Always re-check the asset after setting its text box and nine-slice lines.
