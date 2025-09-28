#!/usr/bin/env python3
"""
Sletter maskingenererte filer som automatisk kan gjenopprettes.

Dette scriptet sletter alle maskingenererte filer og kataloger som kan 
automatisk gjenopprettes ved bygg, testing eller kjøring av koden:

- Python bytecode (.pyc filer og __pycache__ kataloger)
- Build artifakter (dist/, build/, *.egg-info/)
- Test cache (.pytest_cache/, .coverage)
- IDE/Editor filer (.vscode/, *.swp, *.swo, *~)
- Temporære filer (*.tmp, *.temp, *.log)
- Automatisk genererte visualiseringsfiler (*.png fra demos)
"""

import os
import sys
import shutil
import glob
import argparse
from pathlib import Path
from typing import List, Dict, Tuple

def get_directory_size(path: Path) -> int:
    """Beregn total størrelse av katalog og alt innhold."""
    total = 0
    try:
        for item in path.rglob('*'):
            if item.is_file():
                try:
                    total += item.stat().st_size
                except (OSError, FileNotFoundError):
                    pass
    except (OSError, PermissionError):
        pass
    return total

def format_file_size(size: int) -> str:
    """Formater filstørrelse til human-readable format."""
    if size < 1024:
        return f"{size} B"
    elif size < 1024**2:
        return f"{size/1024:.1f} KB"
    elif size < 1024**3:
        return f"{size/(1024**2):.1f} MB"
    else:
        return f"{size/(1024**3):.1f} GB"

def find_items_to_clean(project_root: Path, patterns: List[str]) -> List[Path]:
    """Finn alle filer og kataloger som matcher de gitte mønstrene."""
    items = []
    
    for pattern in patterns:
        # Håndter både relative og absolute mønstre
        if pattern.startswith('**/'):
            # Rekursivt søk
            try:
                matches = project_root.rglob(pattern[3:])  # Fjern '**/'
                items.extend(matches)
            except ValueError:
                pass
        else:
            # Vanlig glob i project root
            try:
                matches = project_root.glob(pattern)
                items.extend(matches)
            except ValueError:
                pass
    
    return list(set(items))  # Fjern duplikater

def safe_remove(path: Path, dry_run: bool = False, verbose: bool = False) -> Tuple[bool, int]:
    """Trygt slett fil eller katalog. Returnerer (success, size_freed)."""
    if not path.exists():
        return False, 0
    
    # Beregn størrelse før sletting
    if path.is_dir():
        size = get_directory_size(path)
    else:
        try:
            size = path.stat().st_size
        except OSError:
            size = 0
    
    if dry_run:
        if verbose:
            print(f"   [DRY RUN] Ville slettet: {path} ({format_file_size(size)})")
        return True, size
    
    try:
        if verbose:
            print(f"   Sletter: {path} ({format_file_size(size)})")
        
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
        else:
            path.unlink()
        
        return True, size
    except (OSError, PermissionError) as e:
        if verbose:
            print(f"   ⚠️  Kunne ikke slette {path}: {e}")
        return False, 0

def main():
    parser = argparse.ArgumentParser(
        description="Slett maskingenererte filer som automatisk kan gjenopprettes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Eksempler:
  %(prog)s                 # Slett alle maskingenererte filer
  %(prog)s --dry-run       # Vis hva som ville blitt slettet
  %(prog)s --verbose       # Detaljert output
        """)
    
    parser.add_argument('--dry-run', action='store_true',
                       help='Vis hva som ville blitt slettet uten å faktisk slette')
    parser.add_argument('--verbose', action='store_true',
                       help='Vis detaljert output under slettingen')
    
    args = parser.parse_args()
    
    # Finn prosjektrot (katalogen der dette scriptet ligger)
    project_root = Path(__file__).parent.absolute()
    os.chdir(project_root)
    
    print(f"🧹 Renser maskingenererte filer i: {project_root}")
    print()
    
    # Definer maskingenererte filer og kataloger som kan slettes
    items_to_clean: Dict[str, List[str]] = {
        "Python bytecode": [
            "**/__pycache__",
            "**/*.pyc", 
            "**/*.pyo",
            "**/*.pyd"
        ],
        "Build artifakter": [
            "dist",
            "build", 
            "*.egg-info",
            "**/*.egg-info"
        ],
        "Test og coverage cache": [
            ".pytest_cache",
            ".coverage",
            ".coverage.*",
            "htmlcov",
            ".tox"
        ],
        "IDE og editor filer": [
            ".vscode/settings.json",
            "**/*.swp",
            "**/*.swo", 
            "**/*~",
            ".DS_Store",
            "**/Thumbs.db"
        ],
        "Temporære filer": [
            "*.tmp",
            "*.temp",
            "*.log",
            "**/*.tmp",
            "**/*.temp"
        ],
        "Demo visualiseringsfiler": [
            "*_hx_demo.png",
            "*_hx_demo.html",
            "my_hx.*",
            "static_hx.png",
            "interactive_hx.html"
        ]
    }
    
    total_items_found = 0
    total_items_deleted = 0
    total_size_freed = 0
    
    # Gå gjennom hver kategori
    for category, patterns in items_to_clean.items():
        print(f"📂 {category}")
        
        category_items_found = 0
        category_items_deleted = 0
        category_size_freed = 0
        
        # Finn alle matchende filer/kataloger
        items = find_items_to_clean(project_root, patterns)
        
        for item in items:
            category_items_found += 1
            total_items_found += 1
            
            success, size = safe_remove(item, args.dry_run, args.verbose)
            
            if success:
                if not args.dry_run:
                    category_items_deleted += 1
                    total_items_deleted += 1
                
                category_size_freed += size
                total_size_freed += size
        
        # Vis resultat for kategori
        if category_items_found == 0:
            print("   ✅ Ingen filer funnet")
        else:
            if args.dry_run:
                print(f"   📊 Fant {category_items_found} element(er) ({format_file_size(category_size_freed)})")
            else:
                print(f"   ✅ Slettet {category_items_deleted} av {category_items_found} element(er) ({format_file_size(category_size_freed)})")
        
        print()
    
    # Sammendrag
    print("📊 SAMMENDRAG")
    print("─" * 40)
    
    if args.dry_run:
        print("🔍 DRY RUN - Ingen filer ble slettet")
        print(f"📁 Fant totalt: {total_items_found} element(er)")
        print(f"💾 Ville frigjort: {format_file_size(total_size_freed)}")
    else:
        print(f"✅ Slettet totalt: {total_items_deleted} av {total_items_found} element(er)")
        print(f"💾 Frigjort diskplass: {format_file_size(total_size_freed)}")
    
    print()
    print("🔄 For å gjenopprette filene:")
    print("   • Python bytecode: Kjør python-koden på nytt")
    print("   • Build artifakter: Kjør 'python -m build' eller 'pip install -e .'")
    print("   • Test cache: Kjør 'pytest' på nytt")
    print("   • Demo filer: Kjør visualiseringsdemoene på nytt")
    
    if args.dry_run:
        print()
        print("💡 Kjør uten --dry-run parameteren for å faktisk slette filene.")

if __name__ == "__main__":
    main()