#!/usr/bin/env python3
"""
Testing utilities for comparing scraper outputs
"""
import json
import shutil
from pathlib import Path
from datetime import datetime
import argparse
import sys
from typing import Dict, Any, List, Tuple


def backup_data(source_dir: str = "pogo_scraper/data", backup_dir: str = "test_backups") -> str:
    """Backup current data files to timestamped directory"""
    source = Path(source_dir)
    backup = Path(backup_dir)

    # Create timestamped backup directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup / timestamp
    backup_path.mkdir(parents=True, exist_ok=True)

    # Copy all JSON files
    copied_files = []
    for json_file in source.glob("*.json"):
        dest = backup_path / json_file.name
        shutil.copy2(json_file, dest)
        copied_files.append(json_file.name)

    print(f"[OK] Backed up {len(copied_files)} files to {backup_path}")
    print(f"     Files: {', '.join(copied_files)}")
    return str(backup_path)


def normalize_json(obj: Any) -> Any:
    """Normalize JSON for comparison (sort lists, etc.)"""
    if isinstance(obj, dict):
        return {k: normalize_json(v) for k, v in sorted(obj.items())}
    elif isinstance(obj, list):
        # For lists of dicts, try to sort by 'id' or 'name' if available
        if obj and isinstance(obj[0], dict):
            # Try common keys for sorting
            for key in ['id', 'name', 'title', 'pokemon']:
                if key in obj[0]:
                    try:
                        return [normalize_json(item) for item in sorted(obj, key=lambda x: x.get(key, ''))]
                    except:
                        pass
        return [normalize_json(item) for item in obj]
    else:
        return obj


def compare_files(file1_path: Path, file2_path: Path) -> Tuple[bool, List[str]]:
    """Compare two JSON files, return (is_same, differences)"""
    differences = []

    # Check if both files exist
    if not file1_path.exists():
        differences.append(f"[!] File missing: {file1_path}")
        return False, differences
    if not file2_path.exists():
        differences.append(f"[!] File missing: {file2_path}")
        return False, differences

    # Load and normalize JSON
    try:
        with open(file1_path, 'r', encoding='utf-8') as f:
            data1 = json.load(f)
        with open(file2_path, 'r', encoding='utf-8') as f:
            data2 = json.load(f)
    except Exception as e:
        differences.append(f"[!] Error loading JSON: {e}")
        return False, differences

    # Normalize for comparison
    norm1 = normalize_json(data1)
    norm2 = normalize_json(data2)

    # Compare
    if norm1 == norm2:
        return True, []

    # Find differences
    if isinstance(data1, list) and isinstance(data2, list):
        if len(data1) != len(data2):
            differences.append(f"  Item count: {len(data1)} → {len(data2)} (diff: {len(data2) - len(data1):+d})")

        # Check for data quality differences
        if len(data1) > 0 and len(data2) > 0:
            # Sample first item to check field changes
            keys1 = set(data1[0].keys()) if isinstance(data1[0], dict) else set()
            keys2 = set(data2[0].keys()) if isinstance(data2[0], dict) else set()

            added_keys = keys2 - keys1
            removed_keys = keys1 - keys2

            if added_keys:
                differences.append(f"  Added fields: {', '.join(added_keys)}")
            if removed_keys:
                differences.append(f"  Removed fields: {', '.join(removed_keys)}")

    if not differences:
        differences.append("  Data structure changed")

    return False, differences


def compare_runs(dir1: str, dir2: str = "pogo_scraper/data") -> Dict[str, Any]:
    """Compare two data directories"""
    path1 = Path(dir1)
    path2 = Path(dir2)

    print(f"\n{'='*70}")
    print(f"Comparing data directories:")
    print(f"  Baseline: {path1}")
    print(f"  Current:  {path2}")
    print(f"{'='*70}\n")

    # Get all JSON files (exclude minified versions)
    files1 = {f.name for f in path1.glob("*.json") if not f.name.endswith('.min.json')}
    files2 = {f.name for f in path2.glob("*.json") if not f.name.endswith('.min.json')}

    all_files = sorted(files1 | files2)

    results = {
        'total_files': len(all_files),
        'identical': 0,
        'different': 0,
        'missing': 0,
        'details': {}
    }

    for filename in all_files:
        file1 = path1 / filename
        file2 = path2 / filename

        is_same, diffs = compare_files(file1, file2)

        if is_same:
            results['identical'] += 1
            print(f"[OK] {filename:30s} IDENTICAL")
            results['details'][filename] = 'identical'
        else:
            if file1.exists() and file2.exists():
                results['different'] += 1
                print(f"[!!] {filename:30s} DIFFERENT")
                for diff in diffs:
                    print(f"     {diff}")
                results['details'][filename] = diffs
            else:
                results['missing'] += 1
                print(f"[!]  {filename:30s} MISSING")
                for diff in diffs:
                    print(f"     {diff}")
                results['details'][filename] = 'missing'

    print(f"\n{'='*70}")
    print(f"Summary:")
    print(f"  [OK] Identical: {results['identical']}/{results['total_files']}")
    print(f"  [!!] Different: {results['different']}/{results['total_files']}")
    print(f"  [!]  Missing:   {results['missing']}/{results['total_files']}")
    print(f"{'='*70}\n")

    return results


def benchmark_scraper(runs: int = 3) -> None:
    """Run scraper multiple times and report timing statistics"""
    import subprocess
    import time

    print(f"\n{'='*70}")
    print(f"Running scraper benchmark ({runs} runs)")
    print(f"{'='*70}\n")

    times = []
    for i in range(runs):
        # Clear cache
        data_dir = Path('pogo_scraper/data')
        for f in data_dir.glob('*.json'):
            f.unlink()

        print(f"Run {i+1}/{runs}...", end=' ', flush=True)

        start = time.time()
        result = subprocess.run(
            ['python', 'scraper.py', '--all'],
            cwd='pogo_scraper',
            capture_output=True,
            text=True
        )
        elapsed = time.time() - start
        times.append(elapsed)

        if result.returncode == 0:
            print(f"OK ({elapsed:.2f}s)")
        else:
            print(f"FAILED")
            print(result.stderr)

    print(f"\n{'='*70}")
    print(f"Benchmark Results:")
    print(f"  Average: {sum(times)/len(times):.2f}s")
    print(f"  Min:     {min(times):.2f}s")
    print(f"  Max:     {max(times):.2f}s")
    print(f"{'='*70}\n")


def main():
    parser = argparse.ArgumentParser(description="Scraper testing utilities")
    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Backup current data files')
    backup_parser.add_argument('--source', default='pogo_scraper/data', help='Source directory')
    backup_parser.add_argument('--dest', default='test_backups', help='Backup directory')

    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Compare two data directories')
    compare_parser.add_argument('baseline', help='Baseline directory (or "latest" for most recent backup)')
    compare_parser.add_argument('--current', default='pogo_scraper/data', help='Current directory')

    # Benchmark command
    benchmark_parser = subparsers.add_parser('benchmark', help='Run scraper multiple times for timing')
    benchmark_parser.add_argument('--runs', type=int, default=3, help='Number of runs (default: 3)')

    args = parser.parse_args()

    if args.command == 'backup':
        backup_data(args.source, args.dest)

    elif args.command == 'compare':
        baseline = args.baseline

        # Handle "latest" shorthand
        if baseline == 'latest':
            backup_dir = Path('test_backups')
            if not backup_dir.exists():
                print("[!] No backups found")
                sys.exit(1)

            backups = sorted(backup_dir.iterdir(), key=lambda p: p.name, reverse=True)
            if not backups:
                print("[!] No backups found")
                sys.exit(1)

            baseline = str(backups[0])
            print(f"Using latest backup: {baseline}\n")

        results = compare_runs(baseline, args.current)

        # Exit with error if any differences found
        if results['different'] > 0 or results['missing'] > 0:
            sys.exit(1)

    elif args.command == 'benchmark':
        benchmark_scraper(args.runs)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
