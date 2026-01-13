import subprocess
import shutil
from pathlib import Path
from .constants import Colors, PREFIXES_DIR
from .config import load_config
from .core import get_proton_env, create_proton_command

def run_regsvr32(args):
    conf = load_config()
    proton_path = conf.get("proton_path")
    runtime_path = conf.get("runtime_path")
    if not proton_path or not proton_path.exists():
        return

    if not PREFIXES_DIR.exists():
        print(f"{Colors.WARNING}⚠ No prefixes found.{Colors.ENDC}")
        return

    prefixes = [p for p in PREFIXES_DIR.iterdir() if p.is_dir()]
    if not prefixes:
        print(f"{Colors.WARNING}⚠ No prefixes found.{Colors.ENDC}")
        return

    prefixes.sort(key=lambda x: x.name)
    print(f"\n{Colors.HEADER}Select Prefix to Run regsvr32:{Colors.ENDC}")
    for i, p in enumerate(prefixes):
        print(f" {Colors.OKBLUE}[{i+1}]{Colors.ENDC} {p.name}")

    selected_prefix = None
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

    print(f"{Colors.HEADER}➜ Running regsvr32{Colors.ENDC}")

    final_args = []
    for arg in args:
        path = Path(arg)
        if path.exists() and path.is_file() and path.suffix.lower() == ".dll":
            print(f"{Colors.OKBLUE}ℹ Detected local DLL file: {path.name}{Colors.ENDC}")
            
            system32 = selected_prefix / "pfx" / "drive_c" / "windows" / "system32"
            if not system32.exists():
                system32 = selected_prefix / "drive_c" / "windows" / "system32"
            
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
    env = get_proton_env(selected_prefix, runtime_path, proton_path)
    subprocess.run(cmd, env=env)