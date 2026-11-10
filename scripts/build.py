#!/usr/bin/env python3
"""Build script for inVENTer e16 Lovelace Cards.

Bundles standalone cards into dist/inventer-e16-cards.js and copies
standalone card modules to dist/.
"""

import pathlib
import sys

ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"
DIST_DIR = ROOT_DIR / "dist"

HEADER = """// SPDX-License-Identifier: MIT
// inVENTer Easy Connect e16 - Lovelace Cards Bundle
// Contains:
//   1. inventer-e16-schedule-card (Time Program & Schedule Management)
//   2. inventer-e16-devices-card (Wireless Devices & Zone Management)

"""


def build():
    print(f"Building inVENTer e16 cards from {SRC_DIR}...")
    DIST_DIR.mkdir(parents=True, exist_ok=True)

    schedule_file = SRC_DIR / "inventer-e16-schedule-card.js"
    devices_file = SRC_DIR / "inventer-e16-devices-card.js"

    if not schedule_file.exists() or not devices_file.exists():
        print("Error: Source files missing in src/ directory!", file=sys.stderr)
        sys.exit(1)

    schedule_src = schedule_file.read_text(encoding="utf-8")
    devices_src = devices_file.read_text(encoding="utf-8")

    # Generate bundle
    bundle_content = (
        f"{HEADER}"
        f"(() => {{\n{schedule_src}\n}})();\n\n"
        f"(() => {{\n{devices_src}\n}})();\n"
    )

    # Write to dist
    bundle_dest = DIST_DIR / "inventer-e16-cards.js"
    bundle_dest.write_text(bundle_content, encoding="utf-8")
    print(f"  ✓ Created {bundle_dest} ({len(bundle_content)} chars)")

    schedule_dest = DIST_DIR / "inventer-e16-schedule-card.js"
    schedule_dest.write_text(schedule_src, encoding="utf-8")
    print(f"  ✓ Created {schedule_dest} ({len(schedule_src)} chars)")

    devices_dest = DIST_DIR / "inventer-e16-devices-card.js"
    devices_dest.write_text(devices_src, encoding="utf-8")
    print(f"  ✓ Created {devices_dest} ({len(devices_src)} chars)")

    # Also keep src/inventer-e16-cards.js in sync
    src_bundle = SRC_DIR / "inventer-e16-cards.js"
    src_bundle.write_text(bundle_content, encoding="utf-8")

    print("Build completed successfully!")


if __name__ == "__main__":
    build()
