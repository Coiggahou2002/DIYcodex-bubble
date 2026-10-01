---
name: douyin-bubble-studio
description: "Design and preflight original Douyin chat bubble PNGs, then register them in Bubble Studio for per-asset nine-slice tuning and application to Codex user messages. Use for 抖音气泡设计, 点九图, bubble libraries, and Codex bubble skins."
---

# Douyin Bubble Studio

Create an expressive chat-bubble asset without sacrificing reading comfort or nine-slice behavior. Treat platform requirements in [Douyin rules](references/douyin-rules.md) as the source of truth; distinguish those requirements from the user's visual preferences.

## Start every bubble task

1. Identify whether the deliverable is static or animated, and whether it must work with horizontal stretch, vertical stretch, or both.
2. Choose the intended text-safe field and the fixed versus scalable nine-slice regions before drawing. Place recognisable characters, letters, faces, dense texture, highlights, and asymmetric details only in fixed caps/corners. Make every scalable band calm and visually uniform.
3. Design the bubble around readable text, not around decoration. Keep the user’s requested concept and style, but simplify anything that collides with text or will smear when stretched.

## Non-negotiable preflight

- Static upload: PNG, no larger than 198×162 px, file size at most 2 MB.
- Keep text visually centered. Reserve more than 24 px on the left/right and more than 18 px on the top/bottom of the text field.
- Ensure the chosen text color has contrast of at least 4.5:1 against every part of the text field.
- Keep primary colors to three or fewer. Use clear, moderately weighted lines; avoid dense or excessively thin linework.
- Use at most one main IP/subject (normally no larger than 102×102 px), and at most two types of secondary decoration (normally no larger than 48×48 px each).
- Detached decoration must remain within 36 px above/below or 42 px left/right of the bubble. Prefer integrating decoration into the bubble silhouette when practical.
- Use original work or content for which the user has adequate rights. Do not closely recreate existing online bubble assets or leave visible third-party watermarks.

## Mirror-safety rule

This is a user-required experience rule, not a documented platform measurement: chat bubbles can be shown as a horizontally mirrored counterpart on the other side of a conversation. Before approving any asymmetric bubble, preview its horizontal flip and reject the design if its core expression becomes unreadable, misleading, or visually broken.

- Do not use readable letters, words, logos, arrows, directional marks, or handed character poses as decoration unless their mirrored form is equally meaningful.
- Do not assume the platform supports separate left/right art variants. Design one asset that survives mirroring.
- Favor bilateral symmetry, mirror-neutral symbols, or a central text-safe field with non-directional edge decoration.
- A bubble that depends on a reading order—such as an L/O/V/E composition—fails this preflight even if its pixel spacing and nine-slice behavior pass.

## Nine-slice design rule

The center and the horizontal/vertical slices grow independently. Therefore:

- **Hard delivery gate — explicit anchor rectangle:** every bubble, including an irregular/organic silhouette, must declare one rectangular scalable field before drawing: `left, top, right, bottom`. Its four boundaries are the only permitted stretch anchors. The top and bottom boundaries must each be a continuous horizontal line; the left and right boundaries must each be a continuous vertical line. All four runs must be visibly present, connected, and uninterrupted through the scalable band. A plain center fill does not substitute for a missing straight boundary.
- Never treat a character body, paw, tail, an open transparent gap, or a curved outer contour as a vertical/horizontal anchor. If the concept puts a character on an edge, add a separate calm straight panel edge behind it and keep that edge uninterrupted in the scalable band.
- Before delivery, run `edge_spacing.py asset.png --anchor-rect LEFT TOP RIGHT BOTTOM`. If the reported `ANCHORS` result is not `PASS`, the asset fails even if size, alpha spacing, or visual appeal otherwise pass. Do not waive this check for “frameless,” soft, hand-drawn, or irregular styles: use a low-contrast fill edge rather than removing the required structure.
- Put the nine-slice split lines only through these straight anchors. Do not put a split line on an arc, diagonal, taper, wave, corner transition, character contour, or decoration; stretching those shapes produces kinks, rails, or duplicated-looking forms.
- The central part of each anchor must keep a stable direction, thickness, color, and spacing. Hand-drawn texture is allowed, but it must be fine and directionally neutral enough to extend without a visible seam.
- Keep all dramatic curvature, scallops, asymmetrical protrusions, and texture landmarks inside the fixed corner caps. An organic bubble may look irregular at the corners but must visibly settle into flat horizontal/vertical runs before the scalable center begins.
- Do not let cells, sketches, gradients with landmarks, text, faces, stripes, or irregular outlines cross a scalable slice.
- For a textured-edge design, confine the distinctive texture to fixed corners; make center/top/bottom and middle-side scalable bands flat or extremely fine and nondirectional.
- For character or typography concepts, anchor all expressive parts in fixed edge zones and let a simple body/panel occupy the scalable center.
- Simulate a short message, a long single-line message, and a multi-line message. Revise if any pattern becomes a long horizontal/vertical band, characters warp, or text loses room.

## Before delivery

1. Export a non-destructive versioned file; do not overwrite an earlier approved asset unless asked.
2. Verify pixel dimensions, format, transparency when requested, and file size.
3. State the intended text color and text-safe area. Tell the user that upload still requires setting the text box and nine-slice lines, then previewing both light and dark modes.
4. For animated assets, also check the one-second/30fps loop, keep motion under 18 px, and do not animate scalable regions.

## Pixel-spacing preflight and micro-fix

When the user reports an upload error such as “元素与气泡间距过大”, use `scripts/edge_spacing.py` before regenerating art. It checks the alpha-channel distance from the canvas edge at the platform-style 1/3 and 2/3 sample lines.

```bash
python3 scripts/edge_spacing.py asset.png
python3 scripts/edge_spacing.py asset.png --repair --out asset-nudged.png
```

`--repair` performs only a uniform whole-image translation and writes a new PNG. It is appropriate for a small, single-edge overshoot (for example 38 px where the limit is 36 px). It refuses conflicting opposite-edge failures or any fix that would crop visible pixels; redesign those assets instead of stretching distinctive artwork blindly. Read [pixel preflight details](references/pixel-preflight.md) when interpreting a platform failure or choosing an alternative repair.

For exact platform values, upload steps, and review risks, read [Douyin rules](references/douyin-rules.md).

## Bubble Studio application workflow

Read [Studio integration](references/studio-integration.md) when importing PNGs, tuning an existing library, or applying a skin to Codex. Use an existing user PNG rather than generating a replacement when the user wants to tune their existing art.

- The installed skill handles design and preflight; the companion local app handles collection, previews, saved coordinates, and application. Generating images requires the host image-generation tool and permission to use it; the app does not bundle a hosted image model or API key.
- Choose a user-authorized output folder and preserve original PNGs. Connect that folder through the app. Do not publish personal folders, paths, logs, or PNGs automatically as part of source publication.
- Keep recognizable decoration entirely in fixed nine-slice caps. Tail stretching is a demonstrated failure: inspect the actual source pixels and let the user select the lines with the editor; a passing alpha-anchor test alone does not prove stretch-safe art.
- Separate saved, connected, applied, and visually verified outcomes. Zero matched messages is a waiting state, never proof of success. Verify at least one real long user message, check assistant messages remain unchanged, and confirm the selected asset's slice values in the live style.
- Apply only on the user's Apply action or explicit instruction. Library browsing, preview edits, and saved presets must not change the live chat theme. Restore clears the app's active choice and the runtime style; exit the app and launch normally to close the debugging port.
