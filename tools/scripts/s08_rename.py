from __future__ import annotations

import os
from pathlib import Path


ROOT = Path(r"D:\知识库")

MAPPINGS = [
    ("00_索引与导航", "10-索引与导航", 1),
    ("07_材料设备价格库", "11-材料设备价格库", 2),
    ("08_项目案例库", "12-项目案例库", 69),
]

EXCLUDED_DIRS = {".git", ".archive"}


def is_excluded(path: Path) -> bool:
    return any(part in EXCLUDED_DIRS for part in path.relative_to(ROOT).parts)


def iter_markdown_files() -> list[Path]:
    files: list[Path] = []
    for current, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [name for name in dirnames if name not in EXCLUDED_DIRS]
        current_path = Path(current)
        if is_excluded(current_path):
            continue
        for filename in filenames:
            if filename.lower().endswith(".md"):
                files.append(current_path / filename)
    return files


def count_files(path: Path) -> int:
    total = 0
    for current, _dirnames, filenames in os.walk(path):
        total += len(filenames)
    return total


def replace_references() -> tuple[int, int, dict[str, int]]:
    changed_files = 0
    total_replacements = 0
    replacement_counts = {old: 0 for old, _new, _expected in MAPPINGS}

    for md_path in iter_markdown_files():
        original_bytes = md_path.read_bytes()
        text = original_bytes.decode("utf-8")
        updated = text

        for old, new, _expected in MAPPINGS:
            count = updated.count(old)
            if count:
                replacement_counts[old] += count
                total_replacements += count
                updated = updated.replace(old, new)

        if updated != text:
            md_path.write_bytes(updated.encode("utf-8"))
            changed_files += 1

    return changed_files, total_replacements, replacement_counts


def validate_preconditions() -> dict[str, int]:
    before_counts: dict[str, int] = {}
    for old, new, _expected in MAPPINGS:
        old_path = ROOT / old
        new_path = ROOT / new
        if not old_path.is_dir():
            raise RuntimeError(f"old directory missing: {old_path}")
        if new_path.exists():
            raise RuntimeError(f"target path already exists: {new_path}")
        before_counts[old] = count_files(old_path)
    return before_counts


def rename_directories() -> None:
    for old, new, _expected in MAPPINGS:
        os.rename(ROOT / old, ROOT / new)


def validate_after(before_counts: dict[str, int]) -> dict[str, object]:
    first_level_old_missing = {}
    new_exists = {}
    after_counts = {}
    expected_ok = {}

    for old, new, expected in MAPPINGS:
        old_path = ROOT / old
        new_path = ROOT / new
        first_level_old_missing[old] = not old_path.exists()
        new_exists[new] = new_path.is_dir()
        after_counts[new] = count_files(new_path) if new_path.is_dir() else None
        expected_ok[new] = after_counts[new] == before_counts[old] == expected

    residuals = []
    for md_path in iter_markdown_files():
        text = md_path.read_bytes().decode("utf-8")
        for old, _new, _expected in MAPPINGS:
            if old in text:
                residuals.append(str(md_path.relative_to(ROOT)))
                break

    return {
        "old_missing": first_level_old_missing,
        "new_exists": new_exists,
        "before_counts": before_counts,
        "after_counts": after_counts,
        "expected_file_counts_ok": expected_ok,
        "residual_old_references": residuals,
    }


def main() -> None:
    before_counts = validate_preconditions()
    changed_files, total_replacements, replacement_counts = replace_references()
    rename_directories()
    validation = validate_after(before_counts)

    print("S08 rename completed")
    print(f"changed_files={changed_files}")
    print(f"total_replacements={total_replacements}")
    for old, new, _expected in MAPPINGS:
        print(f"replacement[{old}->{new}]={replacement_counts[old]}")
    print(f"old_missing={validation['old_missing']}")
    print(f"new_exists={validation['new_exists']}")
    print(f"before_counts={validation['before_counts']}")
    print(f"after_counts={validation['after_counts']}")
    print(f"expected_file_counts_ok={validation['expected_file_counts_ok']}")
    print(f"residual_old_references={validation['residual_old_references']}")

    if validation["residual_old_references"]:
        raise RuntimeError("old directory references remain in markdown files")
    if not all(validation["old_missing"].values()):
        raise RuntimeError("one or more old first-level directories still exist")
    if not all(validation["new_exists"].values()):
        raise RuntimeError("one or more new directories are missing")
    if not all(validation["expected_file_counts_ok"].values()):
        raise RuntimeError("one or more file counts do not match expected values")


if __name__ == "__main__":
    main()
