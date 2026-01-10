import shutil
import subprocess
import os
from pathlib import Path
from .constants import Colors, PREFIXES_DIR, BASE_DIR
from .config import load_config
from .core import get_proton_env

def create_prefix(name):
    conf = load_config()
    proton_path = conf.get("proton_path")
    runtime_path = conf.get("runtime_path")
    
    if not proton_path or not proton_path.exists():
        print(f"{Colors.FAIL}✖ Selected Proton version not found. Please use 'check' or 'pull' command first.{Colors.ENDC}")
        return

    prefix_path = PREFIXES_DIR / name
    
    if prefix_path.exists():
        print(f"{Colors.WARNING}⚠ A prefix named '{name}' already exists.{Colors.ENDC}")
        return

    try:
        prefix_path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"{Colors.FAIL}✖ Could not create prefix directory: {e}{Colors.ENDC}")
        return

    print(f"{Colors.HEADER}➜ Creating Prefix: {Colors.OKGREEN}{name}{Colors.ENDC}")
    print(f"  Using Proton: {Colors.OKBLUE}{proton_path.name}{Colors.ENDC}")
    print(f"  Location: {Colors.GRAY}{prefix_path}{Colors.ENDC}")
    
    print(f"{Colors.OKBLUE}➜ Initializing Wine Prefix (this may take a while)...{Colors.ENDC}")

    env = get_proton_env(prefix_path, runtime_path)

    try:
        subprocess.run([str(proton_path / "proton"), "run", "wineboot"], env=env, check=True)
        print(f"{Colors.OKGREEN}✔ Prefix initialized successfully.{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}✖ Failed to initialize prefix: {e}{Colors.ENDC}")

def delete_prefix():
    if not PREFIXES_DIR.exists():
        print(f"{Colors.WARNING}⚠ No prefixes found.{Colors.ENDC}")
        return

    prefixes = [p for p in PREFIXES_DIR.iterdir() if p.is_dir()]
    if not prefixes:
        print(f"{Colors.WARNING}⚠ No prefixes found.{Colors.ENDC}")
        return

    prefixes.sort(key=lambda x: x.name)
    print(f"\n{Colors.HEADER}Select Prefix to Delete:{Colors.ENDC}")
    for i, p in enumerate(prefixes):
        print(f" {Colors.OKBLUE}[{i+1}]{Colors.ENDC} {p.name}")

    while True:
        try:
            sel = input(f"\n{Colors.OKGREEN}Select Prefix (Number) [Enter to Cancel]: {Colors.ENDC}")
            if not sel:
                print("Operation cancelled.")
                return
            idx = int(sel) - 1
            if 0 <= idx < len(prefixes):
                selected = prefixes[idx]
                confirm = input(f"{Colors.FAIL}⚠ '{selected.name}' prefix will be deleted. Are you sure? (Y/n): {Colors.ENDC}")
                if confirm.lower() in ["y", "yes"]:
                    try:
                        shutil.rmtree(selected)
                        print(f"{Colors.OKGREEN}✔ Prefix deleted.{Colors.ENDC}")
                    except Exception as e:
                        print(f"{Colors.FAIL}✖ Deletion failed: {e}{Colors.ENDC}")
                else:
                    print("Deletion cancelled.")
                break
            print(f"{Colors.FAIL}✖ Invalid selection.{Colors.ENDC}")
        except ValueError:
            print(f"{Colors.FAIL}✖ Please enter a number.{Colors.ENDC}")

def open_prefix_drive():
    if not PREFIXES_DIR.exists():
        print(f"{Colors.WARNING}⚠ No prefixes found.{Colors.ENDC}")
        return

    prefixes = [p for p in PREFIXES_DIR.iterdir() if p.is_dir()]
    if not prefixes:
        print(f"{Colors.WARNING}⚠ No prefixes found.{Colors.ENDC}")
        return

    prefixes.sort(key=lambda x: x.name)
    print(f"\n{Colors.HEADER}Select Prefix to Open:{Colors.ENDC}")
    for i, p in enumerate(prefixes):
        print(f" {Colors.OKBLUE}[{i+1}]{Colors.ENDC} {p.name}")

    while True:
        try:
            sel = input(f"\n{Colors.OKGREEN}Select Prefix (Number): {Colors.ENDC}")
            idx = int(sel) - 1
            if 0 <= idx < len(prefixes):
                selected_prefix = prefixes[idx]
                break
            print(f"{Colors.FAIL}✖ Invalid selection.{Colors.ENDC}")
        except ValueError:
            print(f"{Colors.FAIL}✖ Please enter a number.{Colors.ENDC}")

    drive_c = selected_prefix / "pfx" / "drive_c"
    if not drive_c.exists():
        drive_c = selected_prefix / "drive_c"
    
    print(f"{Colors.OKBLUE}➜ Opening: {drive_c}{Colors.ENDC}")
    try:
        subprocess.run(["xdg-open", str(drive_c)])
    except Exception as e:
        print(f"{Colors.FAIL}✖ Failed to open file manager: {e}{Colors.ENDC}")