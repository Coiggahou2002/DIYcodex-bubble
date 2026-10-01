# Design → library → Codex

The companion project contains `app/server.py`, `app/bridge.mjs`, and `app/static/`. When installed with the companion installer, launch `python3 <skill-dir>/assets/studio/app/server.py`. From the source project, launch `python3 app/server.py`, then open `http://127.0.0.1:19329`.

The app starts without a hardcoded personal library. In the UI, connect a folder containing PNGs, or import selected PNG files. It reads connected folders without changing source art. Imported copies and per-asset presets live in `.local/`, excluded from Git. Set `BUBBLE_STUDIO_DATA` for a different local storage directory.

For each image, the editor stores original-pixel `left, top, right, bottom`, display `scale`, text `color`, and four text paddings (top, right, bottom, left). Presets are keyed by stable resolved file path. Moving an original asset creates a new identity. A `.bubble.json` export contains only filename and settings, no local absolute path.

Open the short, long, and custom message previews, including dark appearance. Lines must avoid characters, tails, paws, and strong texture landmarks. Padding and slice boundaries are separate controls. There is no assumption that PNGs marked size-compliant have passed all Douyin design requirements.

Click Save to store a preset; click Apply to make it active. The server embeds the PNG as a data URL and injects CSS only into local `app://-/` renderer pages over the loopback CDP port. A MutationObserver recognizes new user messages; the local monitor reapplies the chosen skin after page refresh. It replaces only user messages and does not transmit their text. The matched count reflects currently mounted message nodes, which can be hidden or virtualized.

If no debugging port exists, save input and fully quit ChatGPT/Codex before clicking Launch in the studio. macOS is the tested launch platform. The app never force-quits the user's chat. Other platforms may run the library/editor, but must launch a compatible Codex build manually with a localhost debugging port. Do not claim Windows launch support has been tested.

For a real acceptance test: import one original PNG, choose lines, save, reload the editor, verify the preset persists, apply to one visible user message, inspect long-message art, then restore. Do not publish localhost runtime logs or private assets.
