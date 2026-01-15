#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check dependency versions against latest available versions."""

import json
import re
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple
from urllib.request import urlopen
from urllib.error import URLError

# Fix Windows console encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

try:
    import tomli
except ImportError:
    try:
        import tomllib  # Python 3.11+
    except ImportError:
        print("Error: tomli is required. Install with: pip install tomli")
        sys.exit(1)
    else:
        tomli = None


def get_latest_version(package_name: str) -> Optional[str]:
    """Get the latest version of a package from PyPI."""
    try:
        url = f"https://pypi.org/pypi/{package_name}/json"
        with urlopen(url, timeout=5) as response:
            data = json.loads(response.read())
            return data["info"]["version"]
    except (URLError, KeyError, json.JSONDecodeError) as e:
        return None


def parse_version_spec(spec: str) -> Tuple[str, Optional[str]]:
    """Parse version specification (e.g., '>=2.3.0' -> ('2.3.0', '>='))."""
    # Remove package name if present (e.g., "discord.py>=2.3.0")
    if ">=" in spec:
        parts = spec.split(">=")
        if len(parts) == 2:
            return parts[1].strip(), ">="
    elif "==" in spec:
        parts = spec.split("==")
        if len(parts) == 2:
            return parts[1].strip(), "=="
    elif "~=" in spec:
        parts = spec.split("~=")
        if len(parts) == 2:
            return parts[1].strip(), "~="
    elif ">" in spec:
        parts = spec.split(">")
        if len(parts) == 2:
            return parts[1].strip(), ">"
    elif "<=" in spec:
        parts = spec.split("<=")
        if len(parts) == 2:
            return parts[1].strip(), "<="
    elif "<" in spec:
        parts = spec.split("<")
        if len(parts) == 2:
            return parts[1].strip(), "<"
    
    # Try to extract version number
    match = re.search(r'(\d+\.\d+\.\d+)', spec)
    if match:
        return match.group(1), None
    
    return spec.strip(), None


def compare_versions(current: str, latest: str) -> str:
    """Compare two version strings and return status."""
    if not current or not latest:
        return "unknown"
    
    # Normalize versions
    current_parts = [int(x) for x in current.split('.')]
    latest_parts = [int(x) for x in latest.split('.')]
    
    # Pad to same length
    max_len = max(len(current_parts), len(latest_parts))
    current_parts.extend([0] * (max_len - len(current_parts)))
    latest_parts.extend([0] * (max_len - len(latest_parts)))
    
    if current_parts == latest_parts:
        return "up-to-date"
    elif current_parts < latest_parts:
        return "outdated"
    else:
        return "ahead"  # Current is newer (unlikely but possible)


def format_status(status: str) -> str:
    """Format status with emoji."""
    status_map = {
        "up-to-date": "✅",
        "outdated": "⚠️",
        "ahead": "🔵",
        "unknown": "❓"
    }
    return f"{status_map.get(status, '❓')} {status.upper()}"


def main():
    """Main function."""
    # Find pyproject.toml
    project_root = Path(__file__).parent.parent
    pyproject_path = project_root / "pyproject.toml"
    
    if not pyproject_path.exists():
        print(f"Error: {pyproject_path} not found")
        sys.exit(1)
    
    # Read pyproject.toml
    with open(pyproject_path, "rb") as f:
        if tomli:
            data = tomli.load(f)
        else:
            import tomllib
            data = tomllib.load(f)
    
    # Get dependencies
    dependencies = []
    
    # Main dependencies
    if "project" in data and "dependencies" in data["project"]:
        for dep in data["project"]["dependencies"]:
            dependencies.append(("main", dep))
    
    # Optional dependencies
    if "project" in data and "optional-dependencies" in data["project"]:
        for group_name, group_deps in data["project"]["optional-dependencies"].items():
            for dep in group_deps:
                # Skip self-references (e.g., "wisp-framework[db]")
                if not dep.startswith("wisp-framework"):
                    dependencies.append((group_name, dep))
    
    if not dependencies:
        print("No dependencies found")
        return
    
    print("=" * 80)
    print("DEPENDENCY VERSION CHECK")
    print("=" * 80)
    print()
    
    results = []
    
    for group, dep_spec in dependencies:
        # Extract package name (handle extras and version specs)
        package_name = dep_spec.split("[")[0].split(">=")[0].split("==")[0].split("~=")[0].split(">")[0].split("<")[0].strip()
        
        # Skip if it's a git URL
        if package_name.startswith("git+"):
            continue
        
        current_version, constraint = parse_version_spec(dep_spec)
        latest_version = get_latest_version(package_name)
        
        if latest_version:
            status = compare_versions(current_version, latest_version)
        else:
            status = "unknown"
        
        results.append({
            "group": group,
            "package": package_name,
            "current": current_version,
            "latest": latest_version,
            "constraint": constraint,
            "status": status,
            "spec": dep_spec
        })
    
    # Group by category
    groups = {}
    for result in results:
        group = result["group"]
        if group not in groups:
            groups[group] = []
        groups[group].append(result)
    
    # Print results
    for group_name in sorted(groups.keys()):
        print(f"\n{'=' * 80}")
        print(f"{group_name.upper()} DEPENDENCIES")
        print(f"{'=' * 80}")
        print()
        
        print(f"{'Package':<30} {'Current':<15} {'Latest':<15} {'Status':<20}")
        print("-" * 80)
        
        for result in sorted(groups[group_name], key=lambda x: x["package"]):
            package = result["package"]
            current = result["current"] or "N/A"
            latest = result["latest"] or "N/A"
            status = format_status(result["status"])
            
            print(f"{package:<30} {current:<15} {latest:<15} {status:<20}")
            
            # Show constraint if present
            if result["constraint"]:
                print(f"  └─ Constraint: {result['constraint']}")
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    status_counts = {}
    for result in results:
        status = result["status"]
        status_counts[status] = status_counts.get(status, 0) + 1
    
    total = len(results)
    outdated = status_counts.get("outdated", 0)
    up_to_date = status_counts.get("up-to-date", 0)
    unknown = status_counts.get("unknown", 0)
    
    print(f"Total dependencies: {total}")
    print(f"✅ Up-to-date: {up_to_date}")
    print(f"⚠️  Outdated: {outdated}")
    print(f"❓ Unknown: {unknown}")
    
    if outdated > 0:
        print()
        print("⚠️  Outdated packages:")
        for result in results:
            if result["status"] == "outdated":
                print(f"  - {result['package']}: {result['current']} → {result['latest']}")


if __name__ == "__main__":
    main()
