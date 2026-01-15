#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check dependency versions against latest available versions and optionally update them."""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

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

try:
    from urllib.request import urlopen
    from urllib.error import URLError
except ImportError:
    print("Error: urllib not available")
    sys.exit(1)


def get_latest_version(package_name: str) -> Optional[str]:
    """Get the latest version of a package from PyPI."""
    try:
        url = f"https://pypi.org/pypi/{package_name}/json"
        with urlopen(url, timeout=5) as response:
            data = json.loads(response.read())
            return data["info"]["version"]
    except (URLError, KeyError, json.JSONDecodeError) as e:
        return None


def parse_poetry_version_constraint(version_spec: str) -> Tuple[str, Optional[str]]:
    """Parse Poetry version constraints (^, ~, etc.).
    
    Args:
        version_spec: Version string like "^0.22.1" or "~2.3.0"
        
    Returns:
        Tuple of (base_version, constraint_type)
    """
    version_spec = version_spec.strip().strip('"').strip("'")
    
    # Caret (^) means compatible version: ^1.2.3 = >=1.2.3,<2.0.0
    if version_spec.startswith("^"):
        base_version = version_spec[1:]
        return base_version, "^"
    
    # Tilde (~) means approximately: ~1.2.3 = >=1.2.3,<1.3.0
    if version_spec.startswith("~"):
        base_version = version_spec[1:]
        return base_version, "~"
    
    # Standard constraints
    if ">=" in version_spec:
        parts = version_spec.split(">=")
        if len(parts) == 2:
            return parts[1].strip(), ">="
    elif "==" in version_spec:
        parts = version_spec.split("==")
        if len(parts) == 2:
            return parts[1].strip(), "=="
    elif "~=" in version_spec:
        parts = version_spec.split("~=")
        if len(parts) == 2:
            return parts[1].strip(), "~="
    elif ">" in version_spec:
        parts = version_spec.split(">")
        if len(parts) == 2:
            return parts[1].strip(), ">"
    elif "<=" in version_spec:
        parts = version_spec.split("<=")
        if len(parts) == 2:
            return parts[1].strip(), "<="
    elif "<" in version_spec:
        parts = version_spec.split("<")
        if len(parts) == 2:
            return parts[1].strip(), "<"
    
    # Try to extract version number
    match = re.search(r'(\d+\.\d+\.\d+)', version_spec)
    if match:
        return match.group(1), None
    
    return version_spec, None


def parse_version_spec(spec: str) -> Tuple[str, Optional[str]]:
    """Parse version specification (e.g., '>=2.3.0' -> ('2.3.0', '>='))."""
    # Remove package name if present (e.g., "discord.py>=2.3.0")
    spec = spec.strip().strip('"').strip("'")
    
    # Handle Poetry constraints
    if spec.startswith("^") or spec.startswith("~"):
        return parse_poetry_version_constraint(spec)
    
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


def update_pyproject_toml(
    pyproject_path: Path,
    updates: List[Dict[str, str]],
    dry_run: bool = True,
) -> bool:
    """Update pyproject.toml with new dependency versions.
    
    Args:
        pyproject_path: Path to pyproject.toml
        updates: List of update dictionaries with 'group', 'package', 'old_spec', 'new_spec'
        dry_run: If True, don't actually write changes
        
    Returns:
        True if updates were made, False otherwise
    """
    if not updates:
        return False
    
    # Read current file
    with open(pyproject_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    original_content = content
    
    # Apply updates using regex with proper escaping
    for update in updates:
        old_spec = update["old_spec"]
        new_spec = update["new_spec"]
        
        # Escape special regex characters but preserve the pattern
        # Replace the exact old_spec with new_spec
        # Use word boundary-like matching for version specs
        escaped_old = re.escape(old_spec)
        
        # Replace first occurrence (should be unique per dependency)
        content = content.replace(old_spec, new_spec, 1)
    
    if dry_run:
        # Show summary
        print("\n" + "=" * 80)
        print("PROPOSED CHANGES (DRY RUN)")
        print("=" * 80)
        print()
        
        # Show line-by-line diff for changed lines
        original_lines = original_content.splitlines()
        new_lines = content.splitlines()
        
        changes_found = False
        for i, (old_line, new_line) in enumerate(zip(original_lines, new_lines), 1):
            if old_line != new_line:
                changes_found = True
                print(f"Line {i}:")
                print(f"  - {old_line}")
                print(f"  + {new_line}")
                print()
        
        if not changes_found:
            # Fallback: show summary table
            print("Summary of changes:")
            for update in updates:
                print(f"  {update['package']:<30} {update['old_spec']:<30} → {update['new_spec']}")
            print()
        
        print("Run with --update to apply these changes")
        return False
    else:
        # Write updated content
        with open(pyproject_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True


def build_update_spec(package_name: str, current_spec: str, latest_version: str) -> str:
    """Build new dependency spec preserving constraint operator.
    
    Args:
        package_name: Package name
        current_spec: Current dependency specification
        latest_version: Latest available version
        
    Returns:
        New dependency specification string
    """
    # Extract constraint operator
    constraint = None
    if ">=" in current_spec:
        constraint = ">="
    elif "==" in current_spec:
        constraint = "=="
    elif "~=" in current_spec:
        constraint = "~="
    elif ">" in current_spec:
        constraint = ">"
    
    # Default to >= if no constraint found
    if constraint is None:
        constraint = ">="
    
    # Handle extras (e.g., "package[extra]>=1.0.0")
    if "[" in current_spec:
        extras_part = current_spec.split("[")[1].split("]")[0]
        return f"{package_name}[{extras_part}]{constraint}{latest_version}"
    else:
        return f"{package_name}{constraint}{latest_version}"


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Check and optionally update dependency versions in pyproject.toml"
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Update pyproject.toml with latest versions (default: dry-run mode)",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip confirmation prompt when updating",
    )
    parser.add_argument(
        "--only-outdated",
        action="store_true",
        help="Only update outdated packages",
    )
    args = parser.parse_args()
    
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
    
    # Check for Poetry format
    is_poetry = "tool" in data and "poetry" in data["tool"]
    
    # Get dependencies
    dependencies = []
    git_dependencies = []
    
    if is_poetry:
        # Poetry format: [tool.poetry.dependencies]
        if "poetry" in data["tool"] and "dependencies" in data["tool"]["poetry"]:
            for package_name, version_spec in data["tool"]["poetry"]["dependencies"].items():
                # Skip python dependency
                if package_name.lower() == "python":
                    continue
                
                # Check for git dependencies
                if isinstance(version_spec, dict):
                    if "git" in version_spec:
                        git_url = version_spec.get("git", "")
                        branch = version_spec.get("branch")
                        tag = version_spec.get("tag")
                        rev = version_spec.get("rev")
                        git_info = f"git+{git_url}"
                        if branch:
                            git_info += f"@{branch}"
                        elif tag:
                            git_info += f"@{tag}"
                        elif rev:
                            git_info += f"@{rev}"
                        git_dependencies.append({
                            "group": "main",
                            "package": package_name.strip('"').strip("'"),
                            "source": git_info
                        })
                        continue
                    elif "version" in version_spec:
                        version_str = version_spec["version"]
                        dep_spec = f"{package_name}{version_str}"
                        dependencies.append(("main", dep_spec, package_name))
                elif isinstance(version_spec, str):
                    # Check if it's a git URL string
                    if version_spec.startswith("git+") or version_spec.startswith("git://"):
                        git_dependencies.append({
                            "group": "main",
                            "package": package_name.strip('"').strip("'"),
                            "source": version_spec
                        })
                        continue
                    else:
                        dep_spec = f"{package_name}{version_spec}"
                        dependencies.append(("main", dep_spec, package_name))
        
        # Poetry dev dependencies: [tool.poetry.group.dev.dependencies]
        if "poetry" in data["tool"] and "group" in data["tool"]["poetry"]:
            for group_name, group_data in data["tool"]["poetry"]["group"].items():
                if "dependencies" in group_data:
                    for package_name, version_spec in group_data["dependencies"].items():
                        if package_name.lower() == "python":
                            continue
                        
                        if isinstance(version_spec, dict):
                            if "git" in version_spec:
                                git_url = version_spec.get("git", "")
                                branch = version_spec.get("branch")
                                tag = version_spec.get("tag")
                                rev = version_spec.get("rev")
                                git_info = f"git+{git_url}"
                                if branch:
                                    git_info += f"@{branch}"
                                elif tag:
                                    git_info += f"@{tag}"
                                elif rev:
                                    git_info += f"@{rev}"
                                git_dependencies.append({
                                    "group": group_name,
                                    "package": package_name.strip('"').strip("'"),
                                    "source": git_info
                                })
                                continue
                            elif "version" in version_spec:
                                version_str = version_spec["version"]
                                dep_spec = f"{package_name}{version_str}"
                                dependencies.append((group_name, dep_spec, package_name))
                        elif isinstance(version_spec, str):
                            if version_spec.startswith("git+") or version_spec.startswith("git://"):
                                git_dependencies.append({
                                    "group": group_name,
                                    "package": package_name.strip('"').strip("'"),
                                    "source": version_spec
                                })
                                continue
                            else:
                                dep_spec = f"{package_name}{version_spec}"
                                dependencies.append((group_name, dep_spec, package_name))
    else:
        # PEP 621 format: [project] dependencies
        # Main dependencies
        if "project" in data and "dependencies" in data["project"]:
            for dep in data["project"]["dependencies"]:
                # Check for git dependencies
                if isinstance(dep, str) and (dep.startswith("git+") or dep.startswith("git://")):
                    # Extract package name from git URL if possible
                    package_match = re.search(r'#egg=([^&]+)', dep)
                    package_name = package_match.group(1) if package_match else dep.split("/")[-1].replace(".git", "")
                    git_dependencies.append({
                        "group": "main",
                        "package": package_name,
                        "source": dep
                    })
                else:
                    dependencies.append(("main", dep, None))
        
        # Optional dependencies
        if "project" in data and "optional-dependencies" in data["project"]:
            for group_name, group_deps in data["project"]["optional-dependencies"].items():
                for dep in group_deps:
                    # Skip self-references (e.g., "wisp-framework[db]")
                    if isinstance(dep, str) and dep.startswith("wisp-framework"):
                        continue
                    
                    # Check for git dependencies
                    if isinstance(dep, str) and (dep.startswith("git+") or dep.startswith("git://")):
                        package_match = re.search(r'#egg=([^&]+)', dep)
                        package_name = package_match.group(1) if package_match else dep.split("/")[-1].replace(".git", "")
                        git_dependencies.append({
                            "group": group_name,
                            "package": package_name,
                            "source": dep
                        })
                    else:
                        dependencies.append((group_name, dep, None))
    
    if not dependencies:
        print("No dependencies found")
        return
    
    print("=" * 80)
    print("DEPENDENCY VERSION CHECK")
    print("=" * 80)
    print()
    
    results = []
    
    for dep_tuple in dependencies:
        if len(dep_tuple) == 3:
            group, dep_spec, package_name_override = dep_tuple
        else:
            # Backward compatibility
            group, dep_spec = dep_tuple
            package_name_override = None
        
        # Extract package name
        if package_name_override:
            # Poetry format: package name is provided directly
            package_name = package_name_override.strip('"').strip("'")
        else:
            # PEP 621 format: extract from spec
            package_name = dep_spec.split("[")[0].split(">=")[0].split("==")[0].split("~=")[0].split("^")[0].split("~")[0].split(">")[0].split("<")[0].strip().strip('"').strip("'")
        
        # Skip python dependency
        if package_name.lower() == "python":
            continue
        
        # Skip if it's a git URL (should already be filtered, but double-check)
        if package_name.startswith("git+") or package_name.startswith("git://"):
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
    
    # Prepare updates
    updates = []
    for result in results:
        # Only update outdated packages (or all if --only-outdated is not set and status is not unknown)
        should_update = False
        if args.only_outdated:
            should_update = result["status"] == "outdated"
        else:
            # Default: only update outdated packages
            should_update = result["status"] == "outdated"
        
        if should_update and result["latest"]:
            new_spec = build_update_spec(
                result["package"],
                result["spec"],
                result["latest"],
                is_poetry=is_poetry
            )
            # Only add if spec actually changes
            if new_spec != result["spec"]:
                updates.append({
                    "group": result["group"],
                    "package": result["package"],
                    "old_spec": result["spec"],
                    "new_spec": new_spec,
                })
    
    if outdated > 0:
        print()
        print("⚠️  Outdated packages:")
        for result in results:
            if result["status"] == "outdated":
                print(f"  - {result['package']}: {result['current']} → {result['latest']}")
    
    if updates:
        if args.update:
            # Show what will be updated
            print()
            print("=" * 80)
            print("UPDATES TO APPLY")
            print("=" * 80)
            print()
            for update in updates:
                print(f"  {update['package']:<30} {update['old_spec']:<30} → {update['new_spec']}")
            print()
            
            if not args.yes:
                response = input("Apply these updates? (yes/no): ").strip().lower()
                if response not in ("yes", "y"):
                    print("Update cancelled.")
                    return
            
            # Apply updates
            if update_pyproject_toml(pyproject_path, updates, dry_run=False, is_poetry=is_poetry):
                print()
                print("✅ pyproject.toml updated successfully!")
                print()
                print("Next steps:")
                print("  1. Review the changes: git diff pyproject.toml")
                print("  2. Test your project: python scripts/test_compatibility.py")
                print("  3. Commit the changes: git add pyproject.toml && git commit -m 'chore: update dependencies'")
        else:
            # Dry run mode - show proposed changes
            print()
            update_pyproject_toml(pyproject_path, updates, dry_run=True, is_poetry=is_poetry)
    elif outdated == 0:
        print()
        print("✅ All dependencies are up-to-date!")


if __name__ == "__main__":
    main()
