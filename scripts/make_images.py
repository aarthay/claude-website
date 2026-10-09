#!/usr/bin/env python3
"""Make web-sized WebP copies of every artwork upload.

For each image in assets/artworks/ this writes, into assets/thumbs/:
  <name>-480.webp   gallery tile (480px wide)
  <name>-960.webp   gallery tile on high-density screens (960px wide)
  <name>-1800.webp  full-screen viewer and artwork page (1800px on the long edge)

Copies are never larger than the original. A manifest of source-file hashes
(assets/thumbs/manifest.json) means unchanged images are skipped, so it is
cheap to re-run, including in CI with a cached assets/thumbs folder. The GitHub
Pages workflow runs this before every build; run it yourself before
`jekyll serve` to preview locally.

Usage: python3 scripts/make_images.py [--force]
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "assets" / "artworks"
OUTPUT = ROOT / "assets" / "thumbs"
EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"}
WIDTHS = (480, 960)
LONG_EDGE = 1800
QUALITY = 82
# Bump when the sizes or encoding settings change, so every copy is rebuilt.
SETTINGS = f"{WIDTHS}-{LONG_EDGE}-{QUALITY}-v1"
MANIFEST = OUTPUT / "manifest.json"


def save(img, path):
    img.save(path, "WEBP", quality=QUALITY, method=6)


def outputs_for(stem):
    return [OUTPUT / f"{stem}-{w}.webp" for w in WIDTHS] + [OUTPUT / f"{stem}-{LONG_EDGE}.webp"]


def fingerprint(src):
    digest = hashlib.sha256(SETTINGS.encode())
    with open(src, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def process(src, force, manifest):
    targets = outputs_for(src.stem)
    digest = fingerprint(src)
    if not force and manifest.get(src.name) == digest and all(t.exists() for t in targets):
        return False

    with Image.open(src) as opened:
        img = ImageOps.exif_transpose(opened)
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGBA" if "A" in img.getbands() else "RGB")

        for width, target in zip(WIDTHS, targets):
            w = min(width, img.width)
            h = round(img.height * w / img.width)
            save(img.resize((w, h), Image.LANCZOS), target)

        large = img.copy()
        large.thumbnail((LONG_EDGE, LONG_EDGE), Image.LANCZOS)
        save(large, targets[-1])
    manifest[src.name] = digest
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--force", action="store_true", help="rebuild every copy, even if up to date")
    args = parser.parse_args()

    if not SOURCE.is_dir():
        print(f"No {SOURCE.relative_to(ROOT)} folder, nothing to do.")
        return 0
    OUTPUT.mkdir(parents=True, exist_ok=True)

    sources = sorted(p for p in SOURCE.iterdir() if p.is_file() and p.suffix.lower() in EXTENSIONS)
    stems = {}
    for src in sources:
        if src.stem in stems:
            print(f"error: {src.name} and {stems[src.stem].name} would share web copies; rename one.", file=sys.stderr)
            return 1
        stems[src.stem] = src

    try:
        manifest = json.loads(MANIFEST.read_text())
    except (OSError, ValueError):
        manifest = {}

    made = 0
    failed = []
    for src in sources:
        try:
            if process(src, args.force, manifest):
                made += 1
                print(f"made copies of {src.name}")
        except Exception as exc:  # one bad upload shouldn't stop the whole site building
            failed.append(src.name)
            print(f"warning: could not process {src.name}: {exc}", file=sys.stderr)

    # Remove copies whose original has been deleted.
    expected = {t.name for stem in stems for t in outputs_for(stem)}
    for old in OUTPUT.glob("*.webp"):
        if old.name not in expected:
            old.unlink()
    manifest = {name: h for name, h in manifest.items() if name in {s.name for s in sources}}
    MANIFEST.write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n")

    print(f"{len(sources)} artwork images, {made} updated, {len(failed)} failed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
