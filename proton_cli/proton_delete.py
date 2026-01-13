import shutil
import os
from pathlib import Path
from .constants import Colors, SEARCH_PATHS
from .config import load_config, save_config

def delete_proton():
    print(f"{Colors.HEADER}➜ Scanning for Proton Versions to Delete...{Colors.ENDC}")
    
    found_protons = []
    seen_paths = set()

    for path in SEARCH_PATHS:
        if not path.exists():
            continue
            
        try:
            for item in path.iterdir():
                if item.is_dir():
                    proton_exec = item / "proton"
                    
                    # Check if it's a valid proton directory and not already added
                    if proton_exec.exists() and item.resolve() not in seen_paths:
                        found_protons.append(item)
                        seen_paths.add(item.resolve())
        except PermissionError:
            continue

    if not found_protons:
        print(f"{Colors.WARNING}⚠ No Proton versions found in search directories.{Colors.ENDC}")
        return

    # Sort by name
    found_protons.sort(key=lambda x: x.name)

    print(f"\n{Colors.HEADER}Select Proton Version to Delete:{Colors.ENDC}")
    for i, p in enumerate(found_protons):
        print(f" {Colors.OKBLUE}[{i+1}]{Colors.ENDC} {p.name} {Colors.GRAY}({p.parent}){Colors.ENDC}")

    while True:
        try:
            sel = input(f"\n{Colors.OKGREEN}Select Version (Number) [Enter to Cancel]: {Colors.ENDC}")
            if not sel:
                print("Operation cancelled.")
                return
            
            idx = int(sel) - 1
            if 0 <= idx < len(found_protons):
                selected = found_protons[idx]
                
                confirm = input(f"{Colors.FAIL}⚠ '{selected.name}' at '{selected.parent}' will be PERMANENTLY deleted.\nAre you sure? (Y/n): {Colors.ENDC}")
                if confirm.lower() in ["y", "yes"]:
                    try:
                        print(f"{Colors.GRAY}Deleting...{Colors.ENDC}")
                        shutil.rmtree(selected)
                        print(f"{Colors.OKGREEN}✔ Version deleted.{Colors.ENDC}")
                        
                        # Check configuration
                        conf = load_config()
                        current_path = conf.get("proton_path")
                        if current_path and Path(current_path).resolve() == selected.resolve():
                            print(f"{Colors.WARNING}⚠ Deleted version was set as default. Clearing configuration...{Colors.ENDC}")
                            save_config(None, conf.get("runtime_path"))
                            
                    except PermissionError:
                        print(f"{Colors.FAIL}✖ Permission denied. Try running with sudo.{Colors.ENDC}")
                    except Exception as e:
                        print(f"{Colors.FAIL}✖ Deletion failed: {e}{Colors.ENDC}")
                else:
                    print("Deletion cancelled.")
                break
            print(f"{Colors.FAIL}✖ Invalid selection.{Colors.ENDC}")
        except ValueError:
            print(f"{Colors.FAIL}✖ Please enter a number.{Colors.ENDC}")