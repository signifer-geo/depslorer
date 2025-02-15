import argparse
import sys
from pathlib import Path
import json
import glob
from typing import List
import subprocess
from deps_explorer import analyze_dependencies

def parse_file_patterns(patterns: List[str], recursive: bool = True) -> List[Path]:
    files = []
    for pattern in patterns:
        if '*' in pattern:
            matched = glob.glob(pattern, recursive=recursive)
            if not matched:
                print(f"Warning: No files match pattern '{pattern}'")
            files.extend(Path(p) for p in matched)
        else:
            path = Path(pattern)
            if path.exists():
                if path.is_dir():
                    glob_pattern = f"{pattern}/**/*.py" if recursive else f"{pattern}/*.py"
                    files.extend(Path(p) for p in glob.glob(glob_pattern, recursive=recursive))
                else:
                    files.append(path)
            else:
                print(f"Warning: Path does not exist: {pattern}")
    
    return sorted(set(files))

def uninstall_packages(packages: List[str], verbose: bool = False) -> None:
    if not packages:
        return
        
    cmd = ["pip", "uninstall", "-y"] + packages
    try:
        if verbose:
            print(f"Uninstalling packages: {', '.join(packages)}")
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error uninstalling packages: {e}")

def setup_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Find and optionally remove unused dependencies"
    )
    parser.add_argument(
        "-f", "--files",
        nargs='+',
        default=["."],
        help="Python files or directories to analyze"
    )
    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        default=True,
        help="Recursively search directories"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed output"
    )
    parser.add_argument(
        "-u", "--uninstall",
        action="store_true",
        help="Uninstall unused packages"
    )
    return parser

def main() -> int:
    parser = setup_parser()
    args = parser.parse_args()
    
    try:
        python_files = parse_file_patterns(args.files, args.recursive)
        if not python_files:
            print("Error: No Python files found")
            return 1
            
        if args.verbose:
            print(f"Found {len(python_files)} Python files")
            
        result = analyze_dependencies(python_files, args.verbose)
        print(result)
        
        if args.uninstall and "Found unused packages:" in result:
            unused = [line.strip("- ") for line in result.splitlines() if line.strip().startswith("-")]
            uninstall_packages(unused, args.verbose)
        
        return 0
        
    except Exception as e:
        print(f"Error: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
