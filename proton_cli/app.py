import sys
import os
import subprocess
import shlex
from pathlib import Path
from .constants import Colors, BASE_DIR, PREFIXES_DIR, RUNTIME_DIR
from .config import load_config
from .prefix import create_prefix
from .core import get_proton_env

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

    if not PREFIXES_DIR.exists():
        PREFIXES_DIR.mkdir(parents=True, exist_ok=True)

    prefixes = [p for p in PREFIXES_DIR.iterdir() if p.is_dir()]
    
    if not prefixes:
        print(f"{Colors.WARNING}⚠ No prefixes found.{Colors.ENDC}")
        print(f"{Colors.OKBLUE}➜ Automatically creating a new prefix...{Colors.ENDC}")
        
        prefix_name = input(f"{Colors.OKGREEN}Enter name for new prefix [Default: default]: {Colors.ENDC}").strip()
        if not prefix_name:
            prefix_name = "default"
            
        create_prefix(prefix_name)
        prefixes = [p for p in PREFIXES_DIR.iterdir() if p.is_dir()]
        
        if not prefixes:
            return

    selected_prefix = None

    if prefix_name:
        selected_prefix = PREFIXES_DIR / prefix_name
        if not selected_prefix.exists():
            print(f"{Colors.FAIL}✖ Prefix '{prefix_name}' not found.{Colors.ENDC}")
            return
    else:
        prefixes.sort(key=lambda x: x.name)
        print(f"\n{Colors.HEADER}Available Prefixes:{Colors.ENDC}")
        for i, p in enumerate(prefixes):
            print(f" {Colors.OKBLUE}[{i+1}]{Colors.ENDC} {p.name}")

        if len(prefixes) == 1:
            print(f"{Colors.GRAY}Single prefix found, selecting automatically: {prefixes[0].name}{Colors.ENDC}")
            selected_prefix = prefixes[0]
        else:
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

    print(f"{Colors.HEADER}➜ Starting Application{Colors.ENDC}")
    print(f"  Exe: {Colors.OKBLUE}{exe_file.name}{Colors.ENDC}")
    print(f"  Prefix: {Colors.OKBLUE}{selected_prefix.name}{Colors.ENDC}")

    if runtime_path and runtime_path.exists():
        print(f"  Runtime: {Colors.OKBLUE}{runtime_path.name}{Colors.ENDC}")
    else:
        print(f"  Runtime: {Colors.WARNING}System Libraries{Colors.ENDC}")

    if user_options is not None:
        user_opts = user_options
    elif sys.stdin.isatty():
        print(f"\n{Colors.HEADER}Launch Options:{Colors.ENDC}")
        print(f"{Colors.GRAY}Enter environment variables (e.g. MANGOHUD=1) or wrappers (e.g. gamemoderun).{Colors.ENDC}")
        user_opts = input(f"{Colors.OKGREEN}Options [Enter for none]: {Colors.ENDC}").strip()
    else:
        user_opts = ""

    env = get_proton_env(selected_prefix, runtime_path)
    
    cmd = [str(proton_path / "proton"), "run", str(exe_file)] + args
    wrappers = []
    if user_opts:
        parts = shlex.split(user_opts)
        for part in parts:
            if '=' in part:
                k, v = part.split('=', 1)
                env[k] = v
            else:
                wrappers.append(part)

    cmd = wrappers + [str(proton_path / "proton"), "run", str(exe_file)] + args
    
    try:
        subprocess.run(cmd, env=env, cwd=exe_file.parent)
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}⚠ Application stopped.{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}✖ Execution error: {e}{Colors.ENDC}")

def run_installed_app(args):
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
    selected_prefix = None

    print(f"\n{Colors.HEADER}Select Prefix:{Colors.ENDC}")
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

    print(f"{Colors.HEADER}➜ Scanning Applications...{Colors.ENDC}")
    drive_c = selected_prefix / "pfx" / "drive_c"
    if not drive_c.exists():
        drive_c = selected_prefix / "drive_c"

    found_exes = []
    search_dirs = [drive_c / "Program Files", drive_c / "Program Files (x86)"]
    
    ignored_keywords = [
        "uninstall", "unins", "update", "helper", "crash", "report", 
        "config", "redist", "dxsetup", "vcredist", "dotnet", 
        "unitycrashhandler", "webview", "setup",
        "iexplore", "wmplayer", "wordpad",
    ]

    for d in search_dirs:
        if d.exists():
            for root, dirs, files in os.walk(d):
                for file in files:
                    lower_name = file.lower()
                    if lower_name.endswith(".exe") and not any(k in lower_name for k in ignored_keywords):
                        full_path = Path(root) / file
                        found_exes.append(full_path)

    if not found_exes:
        print(f"{Colors.FAIL}✖ No installed application (.exe) found in this prefix.{Colors.ENDC}")
        return

    found_exes.sort(key=lambda x: (len(x.parts), x.name))

    print(f"\n{Colors.HEADER}Found Applications:{Colors.ENDC}")
    print(f"{Colors.GRAY}(If you see multiple exes, try starting from 1){Colors.ENDC}")
    for i, exe in enumerate(found_exes):
        display_name = f"{exe.parent.name}/{exe.name}"
        print(f" {Colors.OKBLUE}[{i+1}]{Colors.ENDC} {display_name}")

    selected_exe = None
    while True:
        try:
            sel = input(f"\n{Colors.OKGREEN}Select Application (Number) [Default: 1]: {Colors.ENDC}")
            if not sel:
                sel = "1"
            idx = int(sel) - 1
            if 0 <= idx < len(found_exes):
                selected_exe = found_exes[idx]
                break
            print(f"{Colors.FAIL}✖ Invalid selection.{Colors.ENDC}")
        except ValueError:
            print(f"{Colors.FAIL}✖ Please enter a number.{Colors.ENDC}")

    print(f"\n{Colors.HEADER}Launch Options:{Colors.ENDC}")
    print(f"{Colors.GRAY}Enter environment variables (e.g. MANGOHUD=1) or wrappers (e.g. gamemoderun).{Colors.ENDC}")
    user_opts = input(f"{Colors.OKGREEN}Options [Enter for none]: {Colors.ENDC}").strip()

    applications_dir = Path.home() / ".local/share/applications"
    shortcut_exists = False
    existing_shortcut_path = None
    
    if applications_dir.exists():
        for item in applications_dir.iterdir():
            if item.is_file() and item.name.endswith(".desktop"):
                try:
                    with open(item, 'r', errors='ignore') as f:
                        content = f.read()
                        if str(selected_exe) in content and "proton-cli" in content:
                            shortcut_exists = True
                            existing_shortcut_path = item
                            break
                except Exception:
                    continue

    should_create_shortcut = False
    use_existing = False

    if shortcut_exists:
        print(f"\n{Colors.OKBLUE}ℹ A desktop shortcut already exists.{Colors.ENDC}")
        update_choice = input(f"{Colors.WARNING}Do you want to update it with new options? (y/N): {Colors.ENDC}")
        if update_choice.lower() in ["y", "yes"]:
            should_create_shortcut = True
            use_existing = True
    else:
        create_shortcut = input(f"\n{Colors.OKGREEN}Create a desktop shortcut (.desktop) for this application? (Y/n): {Colors.ENDC}")
        if create_shortcut.lower() in ["", "y", "yes"]:
            should_create_shortcut = True

    if should_create_shortcut:
        if use_existing and existing_shortcut_path:
            desktop_file_path = existing_shortcut_path
            shortcut_name = selected_exe.stem
            try:
                with open(desktop_file_path, 'r', errors='ignore') as f:
                    for line in f:
                        if line.startswith("Name="):
                            shortcut_name = line.strip().split("=", 1)[1]
                            break
            except:
                pass
            print(f"{Colors.OKBLUE}Updating existing shortcut: {desktop_file_path.name}{Colors.ENDC}")
        else:
            default_name = selected_exe.stem
            shortcut_name = input(f"{Colors.OKGREEN}Enter shortcut name [Default: {default_name}]: {Colors.ENDC}")
            if not shortcut_name:
                shortcut_name = default_name
            
            safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in shortcut_name).strip().replace(' ', '-')
            desktop_file_name = f"proton-cli-{safe_name.lower()}.desktop"
            applications_dir.mkdir(parents=True, exist_ok=True)
            desktop_file_path = applications_dir / desktop_file_name
    
        # Helper to quote arguments for .desktop Exec key
        def desktop_quote(s):
            return '"' + str(s).replace('\\', '\\\\').replace('"', '\\"') + '"'

        # Construct the Exec line
        # We use sys.executable -m proton_cli run -p "Prefix" -o "Options" "Exe"
        base_cmd_parts = [sys.executable, "-m", "proton_cli", "run", str(selected_exe)]
        
        if selected_prefix:
            base_cmd_parts[4:4] = ["-p", selected_prefix.name]
            
        if user_opts:
            base_cmd_parts[4:4] = ["-o", user_opts]
        
        # Join with proper quoting
        exec_cmd = " ".join(desktop_quote(part) for part in base_cmd_parts)
    
        content = f"""[Desktop Entry]
Name={shortcut_name}
Comment=Launched via Proton-CLI
Exec={exec_cmd}
Path={selected_exe.parent}
Icon=utilities-terminal
Terminal=false
Type=Application
Categories=Utility;
"""
        try:
            with open(desktop_file_path, "w") as f:
                f.write(content)
            os.chmod(desktop_file_path, 0o755)
            
            try:
                subprocess.run(["update-desktop-database", str(applications_dir)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass
            
            print(f"{Colors.OKGREEN}✔ Shortcut created/updated: {desktop_file_path}{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.FAIL}✖ Could not create shortcut: {e}{Colors.ENDC}")

    print(f"{Colors.HEADER}➜ Starting Application{Colors.ENDC}")
    print(f"  Exe: {Colors.OKBLUE}{selected_exe}{Colors.ENDC}")
    
    if runtime_path and runtime_path.exists():
        print(f"  Runtime: {Colors.OKBLUE}{runtime_path.name}{Colors.ENDC}")
    else:
        print(f"  Runtime: {Colors.WARNING}System Libraries{Colors.ENDC}")

    env = get_proton_env(selected_prefix, runtime_path)
    
    cmd = [str(proton_path / "proton"), "run", str(selected_exe)] + args
    wrappers = []
    if user_opts:
        parts = shlex.split(user_opts)
        for part in parts:
            if '=' in part:
                k, v = part.split('=', 1)
                env[k] = v
            else:
                wrappers.append(part)

    cmd = wrappers + [str(proton_path / "proton"), "run", str(selected_exe)] + args
    
    try:
        subprocess.run(cmd, env=env)
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}⚠ Application stopped.{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}✖ Execution error: {e}{Colors.ENDC}")