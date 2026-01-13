import subprocess
from pathlib import Path
from .constants import Colors, PREFIXES_DIR
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

    env = get_proton_env(prefix_path, runtime_path, proton_path)

    try:
        subprocess.run([str(proton_path / "proton"), "run", "wineboot"], env=env, check=True)
        print(f"{Colors.OKGREEN}✔ Prefix initialized successfully.{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}✖ Failed to initialize prefix: {e}{Colors.ENDC}")