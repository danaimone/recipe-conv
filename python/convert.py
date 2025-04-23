#!/usr/bin/env python3
"""Mela → Paprika converter (pure‑Python).

Usage:
    python convert.py <input.melarecipes> <output.paprikarecipes>

Requires: Python 3.10+, `tqdm` for progress bar (optional).
"""
from __future__ import annotations

import json
import sys
import zipfile
import gzip
import uuid
import hashlib
import os
from pathlib import Path
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse

try:
    from tqdm import tqdm
except ImportError:
    # fallback no‑op progress bar
    def tqdm(it, *_, **__):
        return it

EPOCH_OFFSET = 978307200  # seconds since 2001‑01‑01 UTC (Apple epoch)

# ---------- helper functions ----------

def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def mela_date_to_iso(sec: float) -> str:
    """Convert Mela numeric date to ISO datetime string accepted by Paprika."""
    unix_ms = int(sec) * 1000 + EPOCH_OFFSET * 1000
    dt = datetime.fromtimestamp(unix_ms / 1000, tz=timezone.utc)
    return dt.astimezone().strftime("%Y-%m-%d %H:%M:%S")


# ---------- core conversion ----------

def convert_recipe(mela_payload: dict) -> dict:
    img = (mela_payload.get("images") or [None])[0]

    return {
        "uid": str(uuid.uuid4()),
        "difficulty": "",
        "servings": mela_payload.get("yield", ""),
        "description": mela_payload.get("text", ""),
        "hash": sha256_hex(mela_payload["id"].encode()),
        "photo_data": img or "",
        "photo_large": "",
        "notes": mela_payload.get("notes", ""),
        "photo": "",
        "cook_time": mela_payload.get("cookTime", ""),
        "image_url": "",
        "photos": [],
        "name": mela_payload["title"],
        "total_time": mela_payload.get("totalTime", ""),
        "categories": mela_payload.get("categories", []),
        "nutritional_info": mela_payload.get("nutrition", ""),
        "directions": mela_payload.get("instructions", ""),
        "created": mela_date_to_iso(float(mela_payload.get("date", 0))),
        "source_url": mela_payload.get("link", ""),
        "rating": 5 if mela_payload.get("favorite") else 0,
        "source": urlparse(mela_payload.get("link", "")).hostname or "",
        "ingredients": mela_payload.get("ingredients", ""),
        "prep_time": mela_payload.get("prepTime", ""),
        "photo_hash": sha256_hex(hashlib.sha256(img.encode()).digest()) if img else "",
    }


def convert_archive(input_path: Path, output_path: Path):
    recipes = []
    with zipfile.ZipFile(input_path) as zf:
        for entry in tqdm(zf.infolist(), desc="Reading Mela export"):
            with zf.open(entry) as fp:
                recipes.append(json.load(fp))

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for rec in tqdm(recipes, desc="Writing Paprika archive"):
            paprika = convert_recipe(rec)
            name_safe = (
                paprika["name"].replace("/", "_").replace("\\", "_")[:80]
                or "Recipe"
            )
            arc_name = f"{name_safe}.paprikarecipe"
            with zout.open(arc_name, "w") as zentry:
                with gzip.GzipFile(fileobj=zentry, mode="w") as gz:
                    gz.write(json.dumps(paprika, ensure_ascii=False).encode("utf-8"))


# ---------- CLI ----------

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("Usage: convert.py <input.melarecipes> <output.paprikarecipes>")

    inp = Path(sys.argv[1]).expanduser().resolve()
    outp = Path(sys.argv[2]).expanduser().resolve()

    if not inp.exists():
        sys.exit(f"Input file not found: {inp}")

    convert_archive(inp, outp)
    print(f"✔ Wrote {outp}")

