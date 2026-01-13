import subprocess
from pathlib import Path
from .constants import Colors, PREFIXES_DIR
from .config import load_config
from .core import get_proton_env, create_proton_command

def run_regedit(reg_file_path):
    conf = load_config()
    proton_path = conf.get("proton_path")
    runtime_path = conf.get("runtime_path")
    if not proton_path or not proton_path.exists():
        return

    reg_file = Path(reg_file_path).resolve()
    if not reg_file.exists():
        print(f"{Colors.FAIL}✖ .reg file not found: {reg_file_path}{Colors.ENDC}")
        return

    if not PREFIXES_DIR.exists():
        print(f"{Colors.WARNING}⚠ No prefixes found.{Colors.ENDC}")
        return

    prefixes = [p for p in PREFIXES_DIR.iterdir() if p.is_dir()]
    if not prefixes:
        print(f"{Colors.WARNING}⚠ No prefixes found.{Colors.ENDC}")
        return

    prefixes.sort(key=lambda x: x.name)
    print(f"\n{Colors.HEADER}Select Prefix to Apply Registry File:{Colors.ENDC}")
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

    print(f"{Colors.HEADER}➜ Applying Registry File{Colors.ENDC}")
    cmd = create_proton_command(proton_path, runtime_path, ["run", "regedit", str(reg_file)])
    env = get_proton_env(selected_prefix, runtime_path, proton_path)
    subprocess.run(cmd, env=env)