import subprocess
from .constants import Colors, PREFIXES_DIR
from .config import load_config
from .core import get_proton_env, create_proton_command, debug_log

def run_winecfg():
    conf = load_config()
    proton_path = conf.get("proton_path")
    runtime_path = conf.get("runtime_path")
    if not proton_path or not proton_path.exists():
        print(f"{Colors.FAIL}✖ Proton not found. Please use 'check' command first.{Colors.ENDC}")
        return

    if not PREFIXES_DIR.exists():
        print(f"{Colors.WARNING}⚠ No prefixes found.{Colors.ENDC}")
        return

    prefixes = [p for p in PREFIXES_DIR.iterdir() if p.is_dir()]
    if not prefixes:
        print(f"{Colors.WARNING}⚠ No prefixes found.{Colors.ENDC}")
        return

    prefixes.sort(key=lambda x: x.name)
    print(f"\n{Colors.HEADER}Select Prefix to Configure:{Colors.ENDC}")
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

    cmd = create_proton_command(proton_path, runtime_path, ["run", "winecfg"])
    env = get_proton_env(selected_prefix, runtime_path, proton_path)
    print(f"{Colors.OKBLUE}➜ Starting Wine configuration...{Colors.ENDC}")
    subprocess.run(cmd, env=env)