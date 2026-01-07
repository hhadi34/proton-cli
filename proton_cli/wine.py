import os
import subprocess
import shutil
from pathlib import Path
from .constants import Colors, BASE_DIR, PREFIXES_DIR
from .config import load_config

def _get_proton_path():
    proton_path = load_config()
    if not proton_path or not proton_path.exists():
        print(f"{Colors.FAIL}✖ Proton not found. Please use 'check' command first.{Colors.ENDC}")
        return None
    return proton_path

def _select_prefix(prompt_msg):
    if not PREFIXES_DIR.exists():
        print(f"{Colors.WARNING}⚠ No prefixes found.{Colors.ENDC}")
        return None

    prefixes = [p for p in PREFIXES_DIR.iterdir() if p.is_dir()]
    if not prefixes:
        print(f"{Colors.WARNING}⚠ No prefixes found.{Colors.ENDC}")
        return None

    prefixes.sort(key=lambda x: x.name)
    print(f"\n{Colors.HEADER}{prompt_msg}:{Colors.ENDC}")
    for i, p in enumerate(prefixes):
        print(f" {Colors.OKBLUE}[{i+1}]{Colors.ENDC} {p.name}")

    while True:
        try:
            sel = input(f"\n{Colors.OKGREEN}Select Prefix (Number): {Colors.ENDC}")
            idx = int(sel) - 1
            if 0 <= idx < len(prefixes):
                return prefixes[idx]
            print(f"{Colors.FAIL}✖ Invalid selection.{Colors.ENDC}")
        except ValueError:
            print(f"{Colors.FAIL}✖ Please enter a number.{Colors.ENDC}")

def _run_proton_cmd(proton_path, prefix_path, cmd, description):
    env = os.environ.copy()
    env["STEAM_COMPAT_DATA_PATH"] = str(prefix_path)
    env["STEAM_COMPAT_CLIENT_INSTALL_PATH"] = str(BASE_DIR)
    
    if description:
        print(f"{Colors.OKBLUE}➜ Starting {description}...{Colors.ENDC}")
        
    try:
        subprocess.run(cmd, env=env)
    except Exception as e:
        print(f"{Colors.FAIL}✖ Execution error: {e}{Colors.ENDC}")

def run_winecfg():
    proton_path = _get_proton_path()
    if not proton_path: return

    prefix = _select_prefix("Select Prefix to Configure")
    if not prefix: return

    cmd = [str(proton_path / "proton"), "run", "winecfg"]
    _run_proton_cmd(proton_path, prefix, cmd, "Wine configuration")

def run_regedit(reg_file_path):
    proton_path = _get_proton_path()
    if not proton_path: return

    reg_file = Path(reg_file_path).resolve()
    if not reg_file.exists():
        print(f"{Colors.FAIL}✖ .reg file not found: {reg_file_path}{Colors.ENDC}")
        return

    prefix = _select_prefix("Select Prefix to Apply Registry File")
    if not prefix: return

    print(f"{Colors.HEADER}➜ Applying Registry File{Colors.ENDC}")
    print(f"  File: {reg_file.name}")
    
    cmd = [str(proton_path / "proton"), "run", "regedit", str(reg_file)]
    _run_proton_cmd(proton_path, prefix, cmd, None)

def run_regsvr32(args):
    proton_path = _get_proton_path()
    if not proton_path: return

    prefix = _select_prefix("Select Prefix to Run regsvr32")
    if not prefix: return

    print(f"{Colors.HEADER}➜ Running regsvr32{Colors.ENDC}")

    final_args = []
    for arg in args:
        path = Path(arg)
        if path.exists() and path.is_file() and path.suffix.lower() == ".dll":
            print(f"{Colors.OKBLUE}ℹ Detected local DLL file: {path.name}{Colors.ENDC}")
            
            system32 = prefix / "pfx" / "drive_c" / "windows" / "system32"
            if not system32.exists():
                system32 = prefix / "drive_c" / "windows" / "system32"
            
            dest_path = system32 / path.name
            try:
                print(f"{Colors.GRAY}➜ Copying to System32...{Colors.ENDC}")
                shutil.copy2(path, dest_path)
                final_args.append(path.name)
            except Exception as e:
                print(f"{Colors.FAIL}✖ Failed to copy DLL: {e}{Colors.ENDC}")
                return
        else:
            final_args.append(arg)
    
    cmd = [str(proton_path / "proton"), "run", "regsvr32"] + final_args
    _run_proton_cmd(proton_path, prefix, cmd, None)

def run_taskmgr():
    proton_path = _get_proton_path()
    if not proton_path: return

    prefix = _select_prefix("Select Prefix to Run Task Manager")
    if not prefix: return

    cmd = [str(proton_path / "proton"), "run", "taskmgr"]
    _run_proton_cmd(proton_path, prefix, cmd, "Task Manager")

def run_uninstaller():
    proton_path = _get_proton_path()
    if not proton_path: return

    prefix = _select_prefix("Select Prefix to Run Uninstaller")
    if not prefix: return

    cmd = [str(proton_path / "proton"), "run", "uninstaller"]
    _run_proton_cmd(proton_path, prefix, cmd, "Uninstaller")