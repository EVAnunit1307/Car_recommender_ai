from __future__ import annotations

import argparse
from pathlib import Path
import sys

import kagglehub

from app.data.kaggle_catalog import (
    RAW_DIR,
    CACHE_FILE,
    DATASET_SLUG,
    build_kaggle_catalog,
    write_catalog,
)


def _find_csv(data_path: Path) -> Path:
    csv_files = list(data_path.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {data_path}")
    return csv_files[0]


def _resolve_dataset_path(force_download: bool) -> Path:
    if not force_download and RAW_DIR.exists():
        csv_files = list(RAW_DIR.glob("*.csv"))
        if csv_files:
            return RAW_DIR
    dataset_path = Path(kagglehub.dataset_download(DATASET_SLUG))
    return dataset_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Download and build Kaggle vehicle catalog.")
    parser.add_argument(
        "--force-download",
        action="store_true",
        help="Force re-download of the Kaggle dataset even if local files exist.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional row limit for quick testing.",
    )
    args = parser.parse_args()

    try:
        dataset_path = _resolve_dataset_path(args.force_download)
        csv_path = _find_csv(dataset_path)
    except Exception as exc:
        print(f"[ERROR] Unable to locate Kaggle dataset: {exc}")
        print("Make sure Kaggle credentials are configured in ~/.kaggle/kaggle.json.")
        return 1

    print(f"[INFO] Using dataset at: {csv_path}")
    cars = build_kaggle_catalog(csv_path, limit=args.limit)

    if not cars:
        print("[WARN] No records found to write.")
        return 1

    write_catalog(cars, CACHE_FILE)
    print(f"[SUCCESS] Wrote {len(cars)} vehicles to {CACHE_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
