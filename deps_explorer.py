import site
from pathlib import Path
from collections import defaultdict
import ast
import re
import json
import subprocess
from typing import Set, Dict, Union, List, Iterable


DEFAULT_PKGS = {'pip', 'setuptools', 'wheel', 'python', 'python_version', 'poetry', 'poetry-core'}

def get_installed_deps() -> Dict[str, Set[str]]:
    name_imports_mapping = defaultdict(set)
    
    # Include user's site-packages
    site_packages = site.getsitepackages() + [site.getusersitepackages()]
    
    for d in site_packages:
        if not Path(d).exists():
            continue
            
        info_dirs = list(Path(d).glob('*.dist-info')) + list(Path(d).glob('*.egg-info'))
        for info_dir in info_dirs:
            try:
                pkg_name = info_dir.stem.split('-')[0].lower()
                if pkg_name in DEFAULT_PKGS:
                    continue
                    
                top_level = info_dir / 'top_level.txt'
                if top_level.exists():
                    import_names = {name.strip().lower() for name in top_level.read_text().splitlines() if name.strip()}
                    name_imports_mapping[pkg_name].update(import_names)
                else:
                    name_imports_mapping[pkg_name].add(pkg_name)
            except Exception as e:
                print(f"Warning: Error processing {info_dir}: {e}")
                
    return name_imports_mapping

def get_used_imports(filepaths: Union[str, Path, Iterable[Union[str, Path]]]) -> Set[str]:
    if isinstance(filepaths, (str, Path)):
        filepaths = [filepaths]
    
    imports = set()
    for fp in filepaths:
        try:
            with open(fp, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=str(fp))
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.add(alias.name.split('.')[0].lower())
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.add(node.module.split('.')[0].lower())
        except Exception as e:
            print(f"Warning: Error analyzing {fp}: {e}")
            
    return imports

def analyze_dependencies(python_files: List[Path], verbose: bool = False) -> str:
    if verbose:
        print("Analyzing Python files...")
    used_imports = get_used_imports(python_files)
    
    if verbose:
        print("Scanning installed packages...")
    installed_deps = get_installed_deps()
    
    unused = []
    for pkg, imports in installed_deps.items():
        if not any(imp in used_imports for imp in imports):
            unused.append(pkg)
    
    if not unused:
        return "No unused dependencies were found."
    
    return "Found unused packages:\n" + "\n".join(f"  - {pkg}" for pkg in sorted(unused))
