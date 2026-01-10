import os
import subprocess
import shutil
from pathlib import Path
from .constants import Colors, BASE_DIR, PREFIXES_DIR
from .config import load_config
from .core import get_proton_env, create_proton_command, debug_log

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

def _run_proton_cmd(proton_path, prefix_path, cmd, description, runtime_path=None):
    env = get_proton_env(prefix_path, runtime_path, proton_path)
    
    debug_log(f"Full Command: {cmd}")
    debug_log(f"Env STEAM_COMPAT_DATA_PATH: {env.get('STEAM_COMPAT_DATA_PATH')}")
    
    if description:
        print(f"{Colors.OKBLUE}➜ Starting {description}...{Colors.ENDC}")
        
    try:
        subprocess.run(cmd, env=env)
    except Exception as e:
        print(f"{Colors.FAIL}✖ Execution error: {e}{Colors.ENDC}")

def run_winecfg():
    conf = load_config()
    proton_path = conf.get("proton_path")
    runtime_path = conf.get("runtime_path")
    if not proton_path or not proton_path.exists():
        print(f"{Colors.FAIL}✖ Proton not found. Please use 'check' command first.{Colors.ENDC}")
        return

    prefix = _select_prefix("Select Prefix to Configure")
    if not prefix: return

    cmd = create_proton_command(proton_path, runtime_path, ["run", "winecfg"])
    _run_proton_cmd(proton_path, prefix, cmd, "Wine configuration", runtime_path)

def run_regedit(reg_file_path):
    conf = load_config()
    proton_path = conf.get("proton_path")
    runtime_path = conf.get("runtime_path")
    if not proton_path or not proton_path.exists(): return

    reg_file = Path(reg_file_path).resolve()
    if not reg_file.exists():
        print(f"{Colors.FAIL}✖ .reg file not found: {reg_file_path}{Colors.ENDC}")
        return

    prefix = _select_prefix("Select Prefix to Apply Registry File")
    if not prefix: return

    print(f"{Colors.HEADER}➜ Applying Registry File{Colors.ENDC}")
    print(f"  File: {reg_file.name}")
    
    cmd = create_proton_command(proton_path, runtime_path, ["run", "regedit", str(reg_file)])
    _run_proton_cmd(proton_path, prefix, cmd, None, runtime_path)

def run_regsvr32(args):
    conf = load_config()
    proton_path = conf.get("proton_path")
    runtime_path = conf.get("runtime_path")
    if not proton_path or not proton_path.exists(): return

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
    
    cmd = create_proton_command(proton_path, runtime_path, ["run", "regsvr32"] + final_args)
    _run_proton_cmd(proton_path, prefix, cmd, None, runtime_path)

def run_taskmgr():
    conf = load_config()
    proton_path = conf.get("proton_path")
    runtime_path = conf.get("runtime_path")
    if not proton_path or not proton_path.exists(): return

    prefix = _select_prefix("Select Prefix to Run Task Manager")
    if not prefix: return

    cmd = create_proton_command(proton_path, runtime_path, ["run", "taskmgr"])
    _run_proton_cmd(proton_path, prefix, cmd, "Task Manager", runtime_path)

def run_uninstaller():
    conf = load_config()
    proton_path = conf.get("proton_path")
    runtime_path = conf.get("runtime_path")
    if not proton_path or not proton_path.exists(): return

    prefix = _select_prefix("Select Prefix to Run Uninstaller")
    if not prefix: return

    cmd = create_proton_command(proton_path, runtime_path, ["run", "uninstaller"])
    _run_proton_cmd(proton_path, prefix, cmd, "Uninstaller", runtime_path)