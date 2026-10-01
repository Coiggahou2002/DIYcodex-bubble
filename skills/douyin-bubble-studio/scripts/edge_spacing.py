#!/usr/bin/env python3
"""Check and safely nudge Douyin chat-bubble edge spacing in transparent PNGs."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from PIL import Image


TOP_BOTTOM_LIMIT = 36
LEFT_RIGHT_LIMIT = 42
MAX_WIDTH = 198
MAX_HEIGHT = 162


@dataclass
class Check:
    edge: str
    sample: str
    coordinate: int
    distance: int | None
    limit: int
    status: str


def sample_positions(length: int) -> list[tuple[str, int]]:
    return [("1/3", round(length / 3)), ("2/3", round(length * 2 / 3))]


def first_visible(values: Iterable[int], threshold: int) -> int | None:
    for index, value in enumerate(values):
        if value > threshold:
            return index
    return None


def measure(alpha: Image.Image, threshold: int) -> list[Check]:
    width, height = alpha.size
    pixels = alpha.load()
    checks: list[Check] = []

    for label, x in sample_positions(width):
        top_index = first_visible((pixels[x, y] for y in range(height)), threshold)
        bottom_index = first_visible((pixels[x, y] for y in range(height - 1, -1, -1)), threshold)
        checks.append(make_check("top", label, x, top_index, TOP_BOTTOM_LIMIT))
        checks.append(make_check("bottom", label, x, bottom_index, TOP_BOTTOM_LIMIT))

    for label, y in sample_positions(height):
        left_index = first_visible((pixels[x, y] for x in range(width)), threshold)
        right_index = first_visible((pixels[x, y] for x in range(width - 1, -1, -1)), threshold)
        checks.append(make_check("left", label, y, left_index, LEFT_RIGHT_LIMIT))
        checks.append(make_check("right", label, y, right_index, LEFT_RIGHT_LIMIT))

    return checks


def anchor_checks(alpha: Image.Image, rect: tuple[int, int, int, int], threshold: int) -> list[dict[str, object]]:
    """Verify a declared four-sided stretch rectangle has continuous alpha on every edge."""
    left, top, right, bottom = rect
    width, height = alpha.size
    if not (0 <= left < right < width and 0 <= top < bottom < height):
        raise ValueError("anchor rectangle must be inside the canvas and have positive width and height")
    pixels = alpha.load()
    edges = {
        "top": [(x, top) for x in range(left, right + 1)],
        "bottom": [(x, bottom) for x in range(left, right + 1)],
        "left": [(left, y) for y in range(top, bottom + 1)],
        "right": [(right, y) for y in range(top, bottom + 1)],
    }
    results: list[dict[str, object]] = []
    for name, points in edges.items():
        missing = [point for point in points if pixels[point[0], point[1]] <= threshold]
        results.append({"edge": name, "length": len(points), "missing": len(missing), "status": "PASS" if not missing else "FAIL"})
    return results


def make_check(edge: str, sample: str, coordinate: int, distance: int | None, limit: int) -> Check:
    if distance is None:
        status = "NO_VISIBLE_PIXEL"
    elif distance <= limit:
        status = "PASS"
    else:
        status = "FAIL"
    return Check(edge, sample, coordinate, distance, limit, status)


def visible_bbox(alpha: Image.Image, threshold: int) -> tuple[int, int, int, int] | None:
    mask = alpha.point(lambda value: 255 if value > threshold else 0)
    return mask.getbbox()


def needs(checks: list[Check], edge: str) -> int:
    values = [check.distance - check.limit for check in checks if check.edge == edge and check.distance is not None]
    return max(0, *values)


def required_translation(checks: list[Check]) -> tuple[int, int, list[str]]:
    top, bottom = needs(checks, "top"), needs(checks, "bottom")
    left, right = needs(checks, "left"), needs(checks, "right")
    conflicts: list[str] = []
    if top and bottom:
        conflicts.append(f"top needs {top}px up while bottom needs {bottom}px down")
    if left and right:
        conflicts.append(f"left needs {left}px left while right needs {right}px right")
    return right - left, bottom - top, conflicts


def render_report(path: Path, image: Image.Image, checks: list[Check], threshold: int, as_json: bool, anchors: list[dict[str, object]] | None = None) -> None:
    width, height = image.size
    payload = {
        "file": str(path),
        "canvas": {"width": width, "height": height, "within_static_limit": width <= MAX_WIDTH and height <= MAX_HEIGHT},
        "alpha_threshold": threshold,
        "checks": [asdict(check) for check in checks],
        "anchors": anchors,
        "pass": width <= MAX_WIDTH and height <= MAX_HEIGHT and all(check.status == "PASS" for check in checks) and (anchors is None or all(item["status"] == "PASS" for item in anchors)),
    }
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    print(f"Canvas: {width}×{height}px ({'PASS' if payload['canvas']['within_static_limit'] else 'FAIL: exceeds 198×162'})")
    print(f"Visible-alpha threshold: > {threshold}")
    for check in checks:
        distance = "no visible pixel" if check.distance is None else f"{check.distance}px"
        suffix = "" if check.status == "PASS" else f" (limit {check.limit}px)"
        print(f"{check.status:16} {check.edge:6} {check.sample:3} @ {check.coordinate:3}: {distance}{suffix}")
    if anchors is not None:
        for item in anchors:
            print(f"ANCHOR {item['status']:11} {item['edge']:6}: {item['length']}px, missing {item['missing']}px")
        print("ANCHORS:", "PASS" if all(item["status"] == "PASS" for item in anchors) else "FAIL")
    print("OVERALL:", "PASS" if payload["pass"] else "FAIL")


def repair(image: Image.Image, alpha: Image.Image, checks: list[Check], threshold: int) -> tuple[Image.Image, int, int]:
    dx, dy, conflicts = required_translation(checks)
    if conflicts:
        raise ValueError("translation conflict: " + "; ".join(conflicts))
    bbox = visible_bbox(alpha, threshold)
    if bbox is None:
        raise ValueError("image has no visible pixels at the selected alpha threshold")
    left, top, right, bottom = bbox
    width, height = image.size
    if left + dx < 0 or top + dy < 0 or right + dx > width or bottom + dy > height:
        raise ValueError("safe translation would crop visible pixels; no output written")
    if dx == 0 and dy == 0:
        return image.copy(), dx, dy
    output = Image.new("RGBA", image.size, (0, 0, 0, 0))
    output.alpha_composite(image, (dx, dy))
    return output, dx, dy


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="input PNG or other image with alpha")
    parser.add_argument("--alpha-threshold", type=int, default=8, choices=range(0, 256))
    parser.add_argument("--json", action="store_true", help="emit a JSON report")
    parser.add_argument("--repair", action="store_true", help="apply a safe whole-image translation")
    parser.add_argument("--out", type=Path, help="new PNG path required with --repair")
    parser.add_argument("--anchor-rect", type=int, nargs=4, metavar=("LEFT", "TOP", "RIGHT", "BOTTOM"), help="required straight-anchor rectangle to verify")
    args = parser.parse_args()

    if args.repair and args.out is None:
        parser.error("--repair requires --out so the source is never overwritten")

    with Image.open(args.input) as source:
        image = source.convert("RGBA")
    alpha = image.getchannel("A")
    checks = measure(alpha, args.alpha_threshold)
    try:
        anchors = anchor_checks(alpha, tuple(args.anchor_rect), args.alpha_threshold) if args.anchor_rect else None
    except ValueError as error:
        parser.error(str(error))
    render_report(args.input, image, checks, args.alpha_threshold, args.json, anchors)

    if not args.repair:
        return 0 if all(check.status == "PASS" for check in checks) and image.width <= MAX_WIDTH and image.height <= MAX_HEIGHT and (anchors is None or all(item["status"] == "PASS" for item in anchors)) else 2

    try:
        output, dx, dy = repair(image, alpha, checks, args.alpha_threshold)
    except ValueError as error:
        print(f"REPAIR REFUSED: {error}", file=sys.stderr)
        return 3

    args.out.parent.mkdir(parents=True, exist_ok=True)
    output.save(args.out, "PNG")
    repaired_checks = measure(output.getchannel("A"), args.alpha_threshold)
    repaired_anchors = anchor_checks(output.getchannel("A"), tuple(args.anchor_rect), args.alpha_threshold) if args.anchor_rect else None
    print(f"REPAIR: translated {dx:+d}px horizontally, {dy:+d}px vertically -> {args.out}")
    render_report(args.out, output, repaired_checks, args.alpha_threshold, args.json, repaired_anchors)
    return 0 if all(check.status == "PASS" for check in repaired_checks) and output.width <= MAX_WIDTH and output.height <= MAX_HEIGHT and (repaired_anchors is None or all(item["status"] == "PASS" for item in repaired_anchors)) else 2


if __name__ == "__main__":
    raise SystemExit(main())
