# Douyin IM chat-bubble rule summary

Source: [抖音聊天气泡常见问题](https://effect.douyin.com/content/pwik2f7v/pwdsypki#80c5b68b), read 2026-09-30. This page can change; refresh it when a later platform requirement conflicts with this summary.

## Asset and structure

- Static bubble: one PNG, at most 198×162 px, no larger than 2 MB.
- Animated bubble: one WEBP, 1-second loop at 30 FPS. Animated elements must not affect scalable regions; movement should be under 18 px.
- A visual bubble height of 120 px is the suggested base, normally not over 135 px. Suggested corner radius is 24 px and suggested outline width is 3–6 px; adapt these when the concept needs an irregular silhouette.
- The platform’s default text size is 51 px and cannot be adjusted.
- The platform uses nine-slice stretching. Select split lines and test both long single-line and multi-line messages before submitting.

## Local experience rule: straight stretch anchors

The user requires an explicit structural safeguard for point-nine stretching. This is a design constraint layered on top of the platform’s nine-slice requirement.

- **Non-negotiable acceptance gate:** declare an anchor rectangle `left, top, right, bottom` for every asset. Its top and bottom must be continuous, straight horizontal runs; its left and right must be continuous, straight vertical runs. The four runs must meet at four corners and be present for the entire declared span. A flat center with curved/missing exterior edges fails.
- A character silhouette, paw, tail, open transparent area, or curved outline cannot stand in for one of these edges. When a character visually occupies an edge, retain a separate quiet straight panel boundary behind it through the scalable middle.
- Run `scripts/edge_spacing.py asset.png --anchor-rect LEFT TOP RIGHT BOTTOM` before delivery. `ANCHORS: FAIL` is a redesign requirement, not a cosmetic warning. Use a very low-contrast, unoutlined fill boundary where the art direction calls for a frameless appearance.
- Place split lines on those runs, not on a curve, diagonal, taper, irregular edge, or character contour.
- Keep the runs continuous in thickness, color, and edge direction. Fine paper grain may continue across them, but unique marks, ripple cells, highlights, text, and distinct line breaks may not.
- Limit curves and irregular silhouettes to the fixed corner caps. The shape must transition from the corner’s visual personality into a quiet horizontal/vertical anchor before it reaches a stretchable region.
- Reject a shape with only curved or asymmetric outer edges even if its center fill is plain: when stretched, its boundaries will deform into an unnatural long arc or kink.

## Text and reading

- Reading experience is the first priority.
- Text is visually centered.
- Leave more than 24 px on the left/right and more than 18 px above/below the text.
- Text/background contrast must be at least 4.5:1.
- The visual design area excludes the text field; do not let artwork compete with or overlap chat text.

## Decorative density

- Primary colors: no more than three.
- Use the minimum decoration needed for the idea. Lines must be clear and moderately weighted; avoid overly thin, dense, or visually uncomfortable details.
- Normally use no more than one main IP/logo subject, up to 102×102 px.
- Normally use no more than two kinds of secondary decoration, up to 48×48 px each.
- Detached decoration may be no farther than 36 px above/below or 42 px left/right of the bubble.

## Upload and review

- In upload, set the text box and nine-slice split lines; select the text color; then preview light and dark modes.
- Bubble name: no more than five Chinese characters, no punctuation or spaces, not a duplicate, and should express the asset’s core idea.
- The work must be original or fully authorized. Avoid visible watermarks, titles using real people/works/famous characters, close visual similarity to live bubbles, commercial placement, personal information, and prohibited or unsafe content.
- Common quality failures: artwork overlapping text, lines too thin, overly complex composition, poor contrast, bland/low-saturation appearance, stretch deformation, unclear concept, and effects that cause visual discomfort.

## Local experience rule: mirror safety

The user requires every bubble concept to remain understandable when horizontally mirrored for the other conversation side. This is a product-experience constraint inferred from real chat rendering, not a numeric requirement from the linked platform page.

- Preview the flipped asset before approval.
- Reject direction-dependent lettering, words, readable logos, arrows, and one-sided character actions unless the flipped result is still intentional and readable.
- Do not approve an asymmetric typographic bubble merely because its original-side preview looks correct.
