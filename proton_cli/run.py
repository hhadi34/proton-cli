import sys
import os
import subprocess
import shlex
import re
from pathlib import Path
from .constants import Colors, PREFIXES_DIR, BASE_DIR
from .config import load_config
from .prefix_make import create_prefix
from .core import get_proton_env, create_proton_command, debug_log

def _create_desktop_shortcut(exe_path, prefix_name, user_options, args):
    """Handles the creation or update of a .desktop shortcut."""
    applications_dir = Path.home() / ".local/share/applications"
    shortcut_name = exe_path.stem
    
    safe_filename = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in shortcut_name).strip().lower()
    desktop_file_name = f"proton-cli-{safe_filename}.desktop"
    desktop_file_path = applications_dir / desktop_file_name
    
    # Check for existing shortcut
    existing_path = None

    if applications_dir.exists():
        for item in applications_dir.iterdir():
            if item.is_file() and item.name.startswith("proton-cli-") and item.name.endswith(".desktop"):
                try:
                    with open(item, 'r', errors='ignore') as f:
                        content = f.read()
                    match = re.search(r'^Exec=["\']?([^"\']+)["\']?', content, re.MULTILINE)
                    if match:
                        wrapper_path = Path(match.group(1))
                        if wrapper_path.exists() and wrapper_path.is_file():
                            with open(wrapper_path, 'r', errors='ignore') as wf:
                                if str(exe_path) in wf.read():
                                    existing_path = item
                                    break
                except Exception:
                    continue

    if not existing_path and desktop_file_path.exists():
        existing_path = desktop_file_path

    # User Interaction
    if existing_path:
        print(f"\n{Colors.OKBLUE}ℹ A shortcut already exists: {existing_path.name}{Colors.ENDC}")
        choice = input(f"{Colors.WARNING}Do you want to update it with current options? (y/N): {Colors.ENDC}")
        if choice.lower() not in ["y", "yes"]:
            return
        desktop_file_path = existing_path
    else:
        choice = input(f"\n{Colors.OKGREEN}Create a desktop shortcut? (Y/n): {Colors.ENDC}")
        if choice.lower() not in ["", "y", "yes"]:
            return
        
        name_input = input(f"{Colors.OKGREEN}Enter shortcut name [Default: {shortcut_name}]: {Colors.ENDC}").strip()
        if name_input:
            shortcut_name = name_input
            safe_filename = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in shortcut_name).strip().lower()
            desktop_file_path = applications_dir / f"proton-cli-{safe_filename}.desktop"

   
    shortcuts_dir = BASE_DIR / "shortcuts"
    shortcuts_dir.mkdir(parents=True, exist_ok=True)
    safe_script_name = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in shortcut_name).strip().lower()
    wrapper_script_path = shortcuts_dir / f"launch_{safe_script_name}.sh"

    cmd_parts = [sys.executable, "-m", "proton_cli", "run"]
    if prefix_name:
        cmd_parts.extend(["-p", prefix_name])
    if user_options:
        cmd_parts.extend(["-o", user_options])
    
    cmd_parts.append(str(exe_path))
    
    if args:
        cmd_parts.extend(args)

    # Write the shell script
    script_content = "#!/bin/bash\n"
    script_content += " ".join(shlex.quote(str(part)) for part in cmd_parts)
    
    try:
        with open(wrapper_script_path, "w") as f:
            f.write(script_content)
        os.chmod(wrapper_script_path, 0o755)
    except Exception as e:
        print(f"{Colors.FAIL}✖ Failed to create wrapper script: {e}{Colors.ENDC}")
        return

    exec_line = f'"{wrapper_script_path}"'

    content = f"""[Desktop Entry]
Name={shortcut_name}
Comment=Launched via Proton-CLI
Exec={exec_line}
Path={exe_path.parent}
Icon=utilities-terminal
Terminal=false
Type=Application
Categories=Utility;Game;
"""
    try:
        applications_dir.mkdir(parents=True, exist_ok=True)
        with open(desktop_file_path, "w") as f:
            f.write(content)
        os.chmod(desktop_file_path, 0o755)
        
        # Update database if tool exists
        subprocess.run(["update-desktop-database", str(applications_dir)], 
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        print(f"{Colors.OKGREEN}✔ Shortcut saved to: {desktop_file_path}{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}✖ Failed to create shortcut: {e}{Colors.ENDC}")

def run_executable(exe_path, args, prefix_name=None, user_options=None):
    conf = load_config()
    proton_path = conf.get("proton_path")
    runtime_path = conf.get("runtime_path")
    
    if not proton_path or not proton_path.exists():
        print(f"{Colors.FAIL}✖ Proton not found. Please use 'check' command first.{Colors.ENDC}")
        return

    exe_file = Path(exe_path).resolve()
    if not exe_file.exists():
        print(f"{Colors.FAIL}✖ File not found: {exe_path}{Colors.ENDC}")
        return

    # Prefix Selection
    if not PREFIXES_DIR.exists():
        PREFIXES_DIR.mkdir(parents=True, exist_ok=True)

    prefixes = [p for p in PREFIXES_DIR.iterdir() if p.is_dir()]
    selected_prefix = None

    if prefix_name:
        selected_prefix = PREFIXES_DIR / prefix_name
        if not selected_prefix.exists():
            print(f"{Colors.FAIL}✖ Prefix '{prefix_name}' not found.{Colors.ENDC}")
            # Fallback to creation or selection could happen here, but strict fail is safer for scripts
            return
    elif not prefixes:
        print(f"{Colors.WARNING}⚠ No prefixes found. Creating 'default'...{Colors.ENDC}")
        create_prefix("default")
        selected_prefix = PREFIXES_DIR / "default"
    else:
        prefixes.sort(key=lambda x: x.name)
        print(f"\n{Colors.HEADER}Select Prefix:{Colors.ENDC}")
        for i, p in enumerate(prefixes):
            print(f" {Colors.OKBLUE}[{i+1}]{Colors.ENDC} {p.name}")
        
        while not selected_prefix:
            try:
                sel = input(f"\n{Colors.OKGREEN}Prefix Number (Default: 1): {Colors.ENDC}")
                if not sel: sel = "1"
                idx = int(sel) - 1
                if 0 <= idx < len(prefixes):
                    selected_prefix = prefixes[idx]
                else:
                    print(f"{Colors.FAIL}✖ Invalid selection.{Colors.ENDC}")
            except ValueError:
                print(f"{Colors.FAIL}✖ Please enter a number.{Colors.ENDC}")

    # User Options
    if user_options is None and sys.stdin.isatty():
        print(f"\n{Colors.HEADER}Launch Options:{Colors.ENDC}")
        print(f"{Colors.GRAY}Enter env vars (e.g. HUD=1) or wrappers (e.g. gamemoderun).{Colors.ENDC}")
        user_options = input(f"{Colors.OKGREEN}Options [Enter for none]: {Colors.ENDC}").strip()

    # Shortcut
    if sys.stdin.isatty():
        _create_desktop_shortcut(exe_file, selected_prefix.name, user_options, args)

    # Execution
    print(f"\n{Colors.HEADER}➜ Launching: {Colors.OKBLUE}{exe_file.name}{Colors.ENDC}")
    
    env = get_proton_env(selected_prefix, runtime_path, proton_path)
    
    parsed_options = shlex.split(user_options) if user_options else []
    real_wrappers = []
    
    for opt in parsed_options:
        if '=' in opt and not opt.startswith('-'):
            key, val = opt.split('=', 1)
            env[key] = val
        else:
            real_wrappers.append(opt)

    cmd = create_proton_command(proton_path, runtime_path, ["run", str(exe_file)] + args, real_wrappers)

    try:
        subprocess.run(cmd, env=env, cwd=exe_file.parent)
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}⚠ Application stopped.{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}✖ Execution error: {e}{Colors.ENDC}")