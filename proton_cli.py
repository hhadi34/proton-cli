#!/usr/bin/env python3
import os
import sys
import argparse
import json
import re
import subprocess
import urllib.request
import tarfile
import shutil
from pathlib import Path

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

VERSION = "1.2"

UPDATE_URL = "https://raw.githubusercontent.com/hhadi34/proton-cli/main/proton_cli.py"

BASE_DIR = Path.home() / ".proton-cli"
CONFIG_FILE = BASE_DIR / "config.json"
VERSIONS_DIR = BASE_DIR / "versions"
PREFIXES_DIR = BASE_DIR / "prefixes"

SEARCH_PATHS = [
    Path.home() / ".steam/steam/steamapps/common",
    Path.home() / ".local/share/Steam/steamapps/common",
    Path.home() / ".steam/root/compatibilitytools.d",
    Path.home() / ".local/share/Steam/compatibilitytools.d",
    Path.home() / ".var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common",
    Path.home() / ".var/app/com.valvesoftware.Steam/.local/share/Steam/compatibilitytools.d",
    Path.home() / ".config/heroic/tools/proton",
    Path.home() / ".config/heroic/tools/wine",
    Path.home() / ".local/share/lutris/runners/wine",
    VERSIONS_DIR,
]

def find_existing_protons():
    """Searches for Proton installations in common system directories."""
    print(f"{Colors.HEADER}--- Scanning for Proton Versions ---{Colors.ENDC}")
    
    found_protons = []

    for path in SEARCH_PATHS:
        if not path.exists():
            continue
            
        try:
            for item in path.iterdir():
                if item.is_dir():
                    proton_exec = item / "proton"
                    
                    if proton_exec.exists() and os.access(proton_exec, os.X_OK):
                        found_protons.append(item)
                        print(f"{Colors.OKGREEN}[FOUND]{Colors.ENDC} {item.name} -> {path}")
        except PermissionError:
            print(f"{Colors.WARNING}[WARNING] Could not access directory {path}.{Colors.ENDC}")
            continue

    if found_protons:
        found_protons.sort(key=lambda x: x.name, reverse=False)
        
        print(f"\n{Colors.OKBLUE}Found Proton Versions:{Colors.ENDC}")
        for i, proton in enumerate(found_protons):
            print(f" [{i+1}] {proton.name} ({proton.parent})")
            
        if len(found_protons) > 1:
            while True:
                try:
                    selection = input(f"\n{Colors.WARNING}Enter the version number you want to use (Default: 1): {Colors.ENDC}")
                    if not selection:
                        selection = 1
                    selection = int(selection)
                    if 1 <= selection <= len(found_protons):
                        best_proton = found_protons[selection - 1]
                        break
                    print(f"{Colors.FAIL}Invalid selection, please try again.{Colors.ENDC}")
                except ValueError:
                    print(f"{Colors.FAIL}Please enter a valid number.{Colors.ENDC}")
        else:
            best_proton = found_protons[0]
            
        print(f"\n{Colors.OKBLUE}Selected Proton:{Colors.ENDC} {best_proton.name}")
        return best_proton
    
    print(f"\n{Colors.FAIL}[ERROR]{Colors.ENDC} No installed Proton version found on the system.")
    return None

def save_config(proton_path):
    try:
        if not BASE_DIR.exists():
            BASE_DIR.mkdir(parents=True, exist_ok=True)
            
        data = {"proton_path": str(proton_path) if proton_path else None}
        
        with open(CONFIG_FILE, 'w') as f:
            json.dump(data, f, indent=4)
            
        print(f"{Colors.OKBLUE}[SAVED]{Colors.ENDC} Configuration saved to: {CONFIG_FILE}")
    except Exception as e:
        print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} Could not save configuration: {e}")

def load_config():
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                path_str = data.get("proton_path")
                return Path(path_str) if path_str else None
        except Exception:
            return None
    return None

def download_ge_proton():
    print(f"{Colors.HEADER}--- Starting GE-Proton Download ---{Colors.ENDC}")
    
    api_url = "https://api.github.com/repos/GloriousEggroll/proton-ge-custom/releases/latest"
    
    try:
        req = urllib.request.Request(api_url, headers={'User-Agent': 'proton-cli'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            
        tag_name = data["tag_name"]
        print(f"Latest version detected: {Colors.OKGREEN}{tag_name}{Colors.ENDC}")
        
        if VERSIONS_DIR.exists():
            for item in VERSIONS_DIR.iterdir():
                if item.is_dir() and tag_name in item.name:
                    print(f"{Colors.OKBLUE}Latest GE-Proton version ({tag_name}) is already installed.{Colors.ENDC}")
                    return item
        
        download_url = None
        for asset in data["assets"]:
            if asset["name"].endswith(".tar.gz"):
                download_url = asset["browser_download_url"]
                break
        
        if not download_url:
            print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} Download link not found.")
            return None

        VERSIONS_DIR.mkdir(parents=True, exist_ok=True)
        tar_path = VERSIONS_DIR / f"{tag_name}.tar.gz"
        extract_path = VERSIONS_DIR / tag_name

        def progress_hook(count, block_size, total_size):
            if total_size > 0:
                percent = int(count * block_size * 100 / total_size)
                if percent > 100: percent = 100
                bar_length = 40
                filled_length = int(bar_length * percent // 100)
                bar = '=' * filled_length + '-' * (bar_length - filled_length)
                sys.stdout.write(f'\rDownloading: [{bar}] {percent}%')
                sys.stdout.flush()

        print(f"Downloading: {download_url}...")
        urllib.request.urlretrieve(download_url, tar_path, reporthook=progress_hook)
        print()
        
        print("Extracting archive...")
        with tarfile.open(tar_path, "r:gz") as tar:
            members = tar.getmembers()
            total_files = len(members)
            for i, member in enumerate(members):
                tar.extract(member, path=VERSIONS_DIR)
                percent = int((i + 1) * 100 / total_files)
                bar_length = 40
                filled_length = int(bar_length * percent // 100)
                bar = '=' * filled_length + '-' * (bar_length - filled_length)
                sys.stdout.write(f'\rExtracting:  [{bar}] {percent}%')
                sys.stdout.flush()
        print()
            
        os.remove(tar_path)
        
        for item in VERSIONS_DIR.iterdir():
            if item.is_dir() and tag_name in item.name:
                print(f"{Colors.OKGREEN}[SUCCESS]{Colors.ENDC} Installation complete: {item}")
                return item
                
    except Exception as e:
        print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} Error occurred during download: {e}")
        return None

def create_prefix(name):
    proton_path = load_config()
    
    if not proton_path or not proton_path.exists():
        print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} Selected Proton version not found. Please use 'check' or 'pull' command first.")
        return

    prefix_path = PREFIXES_DIR / name
    
    if prefix_path.exists():
        print(f"{Colors.WARNING}[WARNING]{Colors.ENDC} A prefix named '{name}' already exists: {prefix_path}")
        return

    try:
        prefix_path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} Could not create prefix directory: {e}")
        return

    print(f"{Colors.HEADER}--- Creating Prefix: {name} ---{Colors.ENDC}")
    print(f"Using Proton: {proton_path.name}")
    print(f"Location: {prefix_path}")
    
    print(f"{Colors.OKGREEN}[SUCCESS]{Colors.ENDC} Prefix directory created. It will be initialized on first run.")

def run_executable(exe_path, args):
    proton_path = load_config()
    if not proton_path or not proton_path.exists():
        print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} Proton not found. Please use 'check' command first.")
        return

    exe_file = Path(exe_path).resolve()
    if not exe_file.exists():
        print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} File not found: {exe_path}")
        return

    if not PREFIXES_DIR.exists():
        PREFIXES_DIR.mkdir(parents=True, exist_ok=True)

    prefixes = [p for p in PREFIXES_DIR.iterdir() if p.is_dir()]
    
    if not prefixes:
        print(f"{Colors.WARNING}[WARNING]{Colors.ENDC} No prefixes found.")
        print(f"{Colors.OKBLUE}Automatically creating a new prefix...{Colors.ENDC}")
        
        prefix_name = input(f"{Colors.WARNING}Enter name for new prefix [Default: default]: {Colors.ENDC}").strip()
        if not prefix_name:
            prefix_name = "default"
            
        create_prefix(prefix_name)
        prefixes = [p for p in PREFIXES_DIR.iterdir() if p.is_dir()]
        
        if not prefixes:
            return

    prefixes.sort(key=lambda x: x.name)
    selected_prefix = None

    print(f"\n{Colors.OKBLUE}Available Prefixes:{Colors.ENDC}")
    for i, p in enumerate(prefixes):
        print(f" [{i+1}] {p.name}")

    if len(prefixes) == 1:
        print(f"Single prefix found, selecting automatically: {prefixes[0].name}")
        selected_prefix = prefixes[0]
    else:
        while True:
            try:
                sel = input(f"\n{Colors.WARNING}Select Prefix (Number): {Colors.ENDC}")
                idx = int(sel) - 1
                if 0 <= idx < len(prefixes):
                    selected_prefix = prefixes[idx]
                    break
                print(f"{Colors.FAIL}Invalid selection.{Colors.ENDC}")
            except ValueError:
                print(f"{Colors.FAIL}Please enter a number.{Colors.ENDC}")

    print(f"{Colors.HEADER}--- Starting Application ---{Colors.ENDC}")
    print(f"Exe: {exe_file.name}")
    print(f"Prefix: {selected_prefix.name}")

    print(f"\n{Colors.OKBLUE}Launch Options:{Colors.ENDC}")
    if sys.stdin.isatty():
        print("Enter environment variables (e.g. MANGOHUD=1) or wrappers (e.g. gamemoderun).")
        user_opts = input(f"{Colors.WARNING}Options [Enter for none]: {Colors.ENDC}").strip()
    else:
        user_opts = ""

    env = os.environ.copy()
    env["STEAM_COMPAT_DATA_PATH"] = str(selected_prefix)
    env["STEAM_COMPAT_CLIENT_INSTALL_PATH"] = str(BASE_DIR)
    
    cmd = [str(proton_path / "proton"), "run", str(exe_file)] + args
    wrappers = []
    if user_opts:
        parts = user_opts.split()
        for part in parts:
            if '=' in part:
                k, v = part.split('=', 1)
                env[k] = v
            else:
                wrappers.append(part)

    cmd = wrappers + [str(proton_path / "proton"), "run", str(exe_file)] + args
    
    try:
        subprocess.run(cmd, env=env)
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Application stopped.{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} Execution error: {e}")

def run_installed_app(args):
    proton_path = load_config()
    if not proton_path or not proton_path.exists():
        print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} Proton not found. Please use 'check' command first.")
        return

    if not PREFIXES_DIR.exists():
        print(f"{Colors.WARNING}[WARNING]{Colors.ENDC} No prefixes found.")
        return

    prefixes = [p for p in PREFIXES_DIR.iterdir() if p.is_dir()]
    if not prefixes:
        print(f"{Colors.WARNING}[WARNING]{Colors.ENDC} No prefixes found.")
        return

    prefixes.sort(key=lambda x: x.name)
    selected_prefix = None

    print(f"\n{Colors.OKBLUE}Which prefix do you want to run the application from?{Colors.ENDC}")
    for i, p in enumerate(prefixes):
        print(f" [{i+1}] {p.name}")

    while True:
        try:
            sel = input(f"\n{Colors.WARNING}Select Prefix (Number): {Colors.ENDC}")
            idx = int(sel) - 1
            if 0 <= idx < len(prefixes):
                selected_prefix = prefixes[idx]
                break
            print(f"{Colors.FAIL}Invalid selection.{Colors.ENDC}")
        except ValueError:
            print(f"{Colors.FAIL}Please enter a number.{Colors.ENDC}")

    print(f"{Colors.HEADER}--- Scanning Applications... ---{Colors.ENDC}")
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
        print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} No installed application (.exe) found in this prefix.")
        return

    found_exes.sort(key=lambda x: (len(x.parts), x.name))

    print(f"\n{Colors.OKBLUE}Found Applications:{Colors.ENDC}")
    print(f"(If you see multiple exes and don't know which one to choose, try starting from 1)")
    for i, exe in enumerate(found_exes):
        display_name = f"{exe.parent.name}/{exe.name}"
        print(f" [{i+1}] {display_name}")

    selected_exe = None
    while True:
        try:
            sel = input(f"\n{Colors.WARNING}Select Application (Number) [Default: 1]: {Colors.ENDC}")
            if not sel:
                sel = "1"
            idx = int(sel) - 1
            if 0 <= idx < len(found_exes):
                selected_exe = found_exes[idx]
                break
            print(f"{Colors.FAIL}Invalid selection.{Colors.ENDC}")
        except ValueError:
            print(f"{Colors.FAIL}Please enter a number.{Colors.ENDC}")

    print(f"\n{Colors.OKBLUE}Launch Options:{Colors.ENDC}")
    print("Enter environment variables (e.g. MANGOHUD=1) or wrappers (e.g. gamemoderun).")
    user_opts = input(f"{Colors.WARNING}Options [Enter for none]: {Colors.ENDC}").strip()

    applications_dir = Path.home() / ".local/share/applications"
    shortcut_exists = False
    
    if applications_dir.exists():
        for item in applications_dir.iterdir():
            if item.is_file() and item.name.endswith(".desktop"):
                try:
                    with open(item, 'r', errors='ignore') as f:
                        content = f.read()
                        if str(selected_exe) in content and "proton-cli" in content:
                            shortcut_exists = True
                            break
                except Exception:
                    continue

    if shortcut_exists:
        print(f"\n{Colors.OKBLUE}A desktop shortcut already exists for this application.{Colors.ENDC}")
    else:
        create_shortcut = input(f"\n{Colors.WARNING}Create a desktop shortcut (.desktop) for this application? (Y/n): {Colors.ENDC}")
        if create_shortcut.lower() in ["", "y", "yes"]:
            default_name = selected_exe.stem
            shortcut_name = input(f"{Colors.WARNING}Enter shortcut name [Default: {default_name}]: {Colors.ENDC}")
            if not shortcut_name:
                shortcut_name = default_name
            
            safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in shortcut_name).strip().replace(' ', '-')
            desktop_file_name = f"proton-cli-{safe_name.lower()}.desktop"
            applications_dir.mkdir(parents=True, exist_ok=True)
            desktop_file_path = applications_dir / desktop_file_name
        
            script_path = Path(__file__).resolve()
            
            
            base_cmd = f"{sys.executable} \"{script_path}\" run \"{selected_exe}\""
            
            shortcut_wrappers = []
            shortcut_envs = []
            if user_opts:
                for part in user_opts.split():
                    if '=' in part:
                        shortcut_envs.append(part)
                    else:
                        shortcut_wrappers.append(part)
            
            exec_cmd = f"{' '.join(shortcut_wrappers)} env {' '.join(shortcut_envs)} {base_cmd}".strip().replace("  ", " ")
        
            content = f"""[Desktop Entry]
Name={shortcut_name}
Comment=Launched via Proton-CLI
Exec={exec_cmd}
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
                
                print(f"{Colors.OKGREEN}[SUCCESS]{Colors.ENDC} Shortcut created: {desktop_file_path}")
            except Exception as e:
                print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} Could not create shortcut: {e}")

    print(f"{Colors.HEADER}--- Starting Application ---{Colors.ENDC}")
    print(f"Exe: {selected_exe}")

    env = os.environ.copy()
    env["STEAM_COMPAT_DATA_PATH"] = str(selected_prefix)
    env["STEAM_COMPAT_CLIENT_INSTALL_PATH"] = str(BASE_DIR)
    
    cmd = [str(proton_path / "proton"), "run", str(selected_exe)] + args
    wrappers = []
    if user_opts:
        parts = user_opts.split()
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
        print(f"\n{Colors.WARNING}Application stopped.{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} Execution error: {e}")

def run_winecfg():
    proton_path = load_config()
    if not proton_path or not proton_path.exists():
        print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} Proton not found. Please use 'check' command first.")
        return

    if not PREFIXES_DIR.exists():
        print(f"{Colors.WARNING}[WARNING]{Colors.ENDC} No prefixes found.")
        return

    prefixes = [p for p in PREFIXES_DIR.iterdir() if p.is_dir()]
    if not prefixes:
        print(f"{Colors.WARNING}[WARNING]{Colors.ENDC} No prefixes found.")
        return

    prefixes.sort(key=lambda x: x.name)
    print(f"\n{Colors.OKBLUE}Select Prefix to Configure:{Colors.ENDC}")
    for i, p in enumerate(prefixes):
        print(f" [{i+1}] {p.name}")

    while True:
        try:
            sel = input(f"\n{Colors.WARNING}Select Prefix (Number): {Colors.ENDC}")
            idx = int(sel) - 1
            if 0 <= idx < len(prefixes):
                selected_prefix = prefixes[idx]
                break
            print(f"{Colors.FAIL}Invalid selection.{Colors.ENDC}")
        except ValueError:
            print(f"{Colors.FAIL}Please enter a number.{Colors.ENDC}")

    env = os.environ.copy()
    env["STEAM_COMPAT_DATA_PATH"] = str(selected_prefix)
    env["STEAM_COMPAT_CLIENT_INSTALL_PATH"] = str(BASE_DIR)
    
    cmd = [str(proton_path / "proton"), "run", "winecfg"]
    
    try:
        print(f"{Colors.OKBLUE}Starting Wine configuration...{Colors.ENDC}")
        subprocess.run(cmd, env=env)
    except Exception as e:
        print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} Execution error: {e}")

def run_regedit(reg_file_path):
    proton_path = load_config()
    if not proton_path or not proton_path.exists():
        print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} Proton not found. Please use 'check' command first.")
        return

    reg_file = Path(reg_file_path).resolve()
    if not reg_file.exists():
        print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} .reg file not found: {reg_file_path}")
        return

    if not PREFIXES_DIR.exists():
        print(f"{Colors.WARNING}[WARNING]{Colors.ENDC} No prefixes found.")
        return

    prefixes = [p for p in PREFIXES_DIR.iterdir() if p.is_dir()]
    if not prefixes:
        print(f"{Colors.WARNING}[WARNING]{Colors.ENDC} No prefixes found.")
        return

    prefixes.sort(key=lambda x: x.name)
    print(f"\n{Colors.OKBLUE}Select Prefix to Apply Registry File:{Colors.ENDC}")
    for i, p in enumerate(prefixes):
        print(f" [{i+1}] {p.name}")

    while True:
        try:
            sel = input(f"\n{Colors.WARNING}Select Prefix (Number): {Colors.ENDC}")
            idx = int(sel) - 1
            if 0 <= idx < len(prefixes):
                selected_prefix = prefixes[idx]
                break
            print(f"{Colors.FAIL}Invalid selection.{Colors.ENDC}")
        except ValueError:
            print(f"{Colors.FAIL}Please enter a number.{Colors.ENDC}")

    env = os.environ.copy()
    env["STEAM_COMPAT_DATA_PATH"] = str(selected_prefix)
    env["STEAM_COMPAT_CLIENT_INSTALL_PATH"] = str(BASE_DIR)
    
    print(f"{Colors.HEADER}--- Applying Registry File ---{Colors.ENDC}")
    print(f"File: {reg_file.name}")
    
    cmd = [str(proton_path / "proton"), "run", "regedit", str(reg_file)]
    
    try:
        subprocess.run(cmd, env=env)
    except Exception as e:
        print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} Execution error: {e}")

def run_taskmgr():
    proton_path = load_config()
    if not proton_path or not proton_path.exists():
        print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} Proton not found. Please use 'check' command first.")
        return

    if not PREFIXES_DIR.exists():
        print(f"{Colors.WARNING}[WARNING]{Colors.ENDC} No prefixes found.")
        return

    prefixes = [p for p in PREFIXES_DIR.iterdir() if p.is_dir()]
    if not prefixes:
        print(f"{Colors.WARNING}[WARNING]{Colors.ENDC} No prefixes found.")
        return

    prefixes.sort(key=lambda x: x.name)
    print(f"\n{Colors.OKBLUE}Select Prefix to Run Task Manager:{Colors.ENDC}")
    for i, p in enumerate(prefixes):
        print(f" [{i+1}] {p.name}")

    while True:
        try:
            sel = input(f"\n{Colors.WARNING}Select Prefix (Number): {Colors.ENDC}")
            idx = int(sel) - 1
            if 0 <= idx < len(prefixes):
                selected_prefix = prefixes[idx]
                break
            print(f"{Colors.FAIL}Invalid selection.{Colors.ENDC}")
        except ValueError:
            print(f"{Colors.FAIL}Please enter a number.{Colors.ENDC}")

    env = os.environ.copy()
    env["STEAM_COMPAT_DATA_PATH"] = str(selected_prefix)
    env["STEAM_COMPAT_CLIENT_INSTALL_PATH"] = str(BASE_DIR)
    
    cmd = [str(proton_path / "proton"), "run", "taskmgr"]
    
    try:
        print(f"{Colors.OKBLUE}Starting Task Manager...{Colors.ENDC}")
        subprocess.run(cmd, env=env)
    except Exception as e:
        print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} Execution error: {e}")

def update_self():
    print(f"{Colors.HEADER}--- Checking for Updates ---{Colors.ENDC}")
    try:
        req = urllib.request.Request(UPDATE_URL, headers={'User-Agent': 'proton-cli'})
        with urllib.request.urlopen(req) as response:
            remote_code = response.read().decode('utf-8')
        
        match = re.search(r'VERSION\s*=\s*[\'"]([^\'"]+)[\'"]', remote_code)
        if not match:
            print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} Could not determine remote version.")
            return

        remote_version = match.group(1)
        
        if remote_version == VERSION:
            print(f"{Colors.OKGREEN}You are already using the latest version ({VERSION}).{Colors.ENDC}")
            return
            
        print(f"{Colors.OKBLUE}New version found: {remote_version} (Current: {VERSION}){Colors.ENDC}")
        
        if not os.access(__file__, os.W_OK):
            print(f"{Colors.FAIL}[PERMISSION DENIED]{Colors.ENDC}")
            print(f"{Colors.WARNING}You need root privileges to update.{Colors.ENDC}")
            print(f"Please run: {Colors.OKGREEN}sudo proton-cli update{Colors.ENDC}")
            return

        choice = input(f"{Colors.WARNING}Do you want to update? (Y/n): {Colors.ENDC}")
        if choice.lower() in ["", "y", "yes"]:
            with open(__file__, 'w') as f:
                f.write(remote_code)
            print(f"{Colors.OKGREEN}[SUCCESS]{Colors.ENDC} Updated to version {remote_version}.")
            print("Please restart the application.")
        else:
            print("Update cancelled.")

    except Exception as e:
        print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} Failed to check for updates: {e}")

def run_uninstaller():
    proton_path = load_config()
    if not proton_path or not proton_path.exists():
        print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} Proton not found. Please use 'check' command first.")
        return

    if not PREFIXES_DIR.exists():
        print(f"{Colors.WARNING}[WARNING]{Colors.ENDC} No prefixes found.")
        return

    prefixes = [p for p in PREFIXES_DIR.iterdir() if p.is_dir()]
    if not prefixes:
        print(f"{Colors.WARNING}[WARNING]{Colors.ENDC} No prefixes found.")
        return

    prefixes.sort(key=lambda x: x.name)
    print(f"\n{Colors.OKBLUE}Select Prefix to Run Uninstaller:{Colors.ENDC}")
    for i, p in enumerate(prefixes):
        print(f" [{i+1}] {p.name}")

    while True:
        try:
            sel = input(f"\n{Colors.WARNING}Select Prefix (Number): {Colors.ENDC}")
            idx = int(sel) - 1
            if 0 <= idx < len(prefixes):
                selected_prefix = prefixes[idx]
                break
            print(f"{Colors.FAIL}Invalid selection.{Colors.ENDC}")
        except ValueError:
            print(f"{Colors.FAIL}Please enter a number.{Colors.ENDC}")

    env = os.environ.copy()
    env["STEAM_COMPAT_DATA_PATH"] = str(selected_prefix)
    env["STEAM_COMPAT_CLIENT_INSTALL_PATH"] = str(BASE_DIR)
    
    cmd = [str(proton_path / "proton"), "run", "uninstaller"]
    
    try:
        print(f"{Colors.OKBLUE}Starting Uninstaller...{Colors.ENDC}")
        subprocess.run(cmd, env=env)
    except Exception as e:
        print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} Execution error: {e}")

def delete_prefix():
    if not PREFIXES_DIR.exists():
        print(f"{Colors.WARNING}[WARNING]{Colors.ENDC} No prefixes found.")
        return

    prefixes = [p for p in PREFIXES_DIR.iterdir() if p.is_dir()]
    if not prefixes:
        print(f"{Colors.WARNING}[WARNING]{Colors.ENDC} No prefixes found.")
        return

    prefixes.sort(key=lambda x: x.name)
    print(f"\n{Colors.OKBLUE}Select Prefix to Delete:{Colors.ENDC}")
    for i, p in enumerate(prefixes):
        print(f" [{i+1}] {p.name}")

    while True:
        try:
            sel = input(f"\n{Colors.WARNING}Select Prefix (Number) [Enter to Cancel]: {Colors.ENDC}")
            if not sel:
                print("Operation cancelled.")
                return
            idx = int(sel) - 1
            if 0 <= idx < len(prefixes):
                selected = prefixes[idx]
                confirm = input(f"{Colors.FAIL}'{selected.name}' prefix will be deleted. Are you sure? (Y/n): {Colors.ENDC}")
                if confirm.lower() in ["y", "yes"]:
                    try:
                        shutil.rmtree(selected)
                        print(f"{Colors.OKGREEN}[SUCCESS]{Colors.ENDC} Prefix deleted.")
                    except Exception as e:
                        print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} Deletion failed: {e}")
                else:
                    print("Deletion cancelled.")
                break
            print(f"{Colors.FAIL}Invalid selection.{Colors.ENDC}")
        except ValueError:
            print(f"{Colors.FAIL}Please enter a number.{Colors.ENDC}")

def delete_proton():
    if not VERSIONS_DIR.exists():
        print(f"{Colors.WARNING}[WARNING]{Colors.ENDC} No downloaded Proton versions found.")
        return

    versions = [p for p in VERSIONS_DIR.iterdir() if p.is_dir()]
    if not versions:
        print(f"{Colors.WARNING}[WARNING]{Colors.ENDC} No downloaded Proton versions found.")
        return

    versions.sort(key=lambda x: x.name)
    print(f"\n{Colors.OKBLUE}Select Proton Version to Delete:{Colors.ENDC}")
    for i, p in enumerate(versions):
        print(f" [{i+1}] {p.name}")

    while True:
        try:
            sel = input(f"\n{Colors.WARNING}Select Version (Number) [Enter to Cancel]: {Colors.ENDC}")
            if not sel:
                print("Operation cancelled.")
                return
            idx = int(sel) - 1
            if 0 <= idx < len(versions):
                selected = versions[idx]
                confirm = input(f"{Colors.FAIL}'{selected.name}' version will be deleted. Are you sure? (Y/n): {Colors.ENDC}")
                if confirm.lower() in ["y", "yes"]:
                    try:
                        shutil.rmtree(selected)
                        print(f"{Colors.OKGREEN}[SUCCESS]{Colors.ENDC} Version deleted.")
                        
                        current_path = load_config()
                        if current_path and current_path.resolve() == selected.resolve():
                            print(f"{Colors.WARNING}Deleted version was set as default. Clearing configuration...{Colors.ENDC}")
                            save_config(None)
                    except Exception as e:
                        print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} Deletion failed: {e}")
                else:
                    print("Deletion cancelled.")
                break
            print(f"{Colors.FAIL}Invalid selection.{Colors.ENDC}")
        except ValueError:
            print(f"{Colors.FAIL}Please enter a number.{Colors.ENDC}")

def print_help_table():
    print(f"\n{Colors.HEADER}=== Proton-CLI Help Menu (v{VERSION}) ==={Colors.ENDC}")
    print(f"{Colors.OKBLUE}{'Command':<25} {'Description':<55}{Colors.ENDC}")
    print("-" * 80)
    commands = [
        ("check", "Scan and configure Proton versions on the system"),
        ("pull", "Download the latest GE-Proton version"),
        ("proton-delete", "Delete downloaded Proton versions"),
        ("prefix-make <name>", "Create a new Wine prefix"),
        ("winecfg", "Open Wine configuration for a prefix"),
        ("regedit <file>", "Apply a .reg file to a prefix"),
        ("taskmgr", "Open Task Manager for a prefix"),
        ("uninstaller", "Open Add/Remove Programs for a prefix"),
        ("prefix-delete", "Delete an existing Wine prefix"),
        ("run <exe> [args]", "Run an .exe file"),
        ("run-app [args]", "Find and run an installed application inside a prefix"),
        ("update", "Update proton-cli to the latest version")
    ]
    for cmd, desc in commands:
        print(f"{Colors.OKGREEN}{cmd:<25}{Colors.ENDC} {desc}")
    print("-" * 80)

def main():
    class CustomParser(argparse.ArgumentParser):
        def error(self, message):
            if "choose from" in message:
                message = message.split('(')[0].strip()
            print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} {message}")
            print(f"Use {Colors.OKGREEN}proton-cli -h{Colors.ENDC} to see available commands.")
            sys.exit(2)

    parser = CustomParser(description="Proton-CLI", add_help=False)
    parser.add_argument('-h', '--help', action='store_true', help="Show help menu")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("check", help="Scan and configure Proton versions on the system")

    subparsers.add_parser("pull", help="Download the latest GE-Proton version")

    subparsers.add_parser("proton-delete", help="Delete downloaded Proton versions")

    prefix_parser = subparsers.add_parser("prefix-make", help="Create a new Wine prefix")
    prefix_parser.add_argument("name", help="Name for the prefix (e.g., office-apps)")

    subparsers.add_parser("winecfg", help="Open Wine configuration for a prefix")

    regedit_parser = subparsers.add_parser("regedit", help="Apply a .reg file to a prefix")
    regedit_parser.add_argument("reg_file", help="Path to the .reg file")

    subparsers.add_parser("taskmgr", help="Open Task Manager for a prefix")

    subparsers.add_parser("uninstaller", help="Open Add/Remove Programs for a prefix")

    subparsers.add_parser("prefix-delete", help="Delete an existing Wine prefix")

    run_parser = subparsers.add_parser("run", help="Run an .exe file")
    run_parser.add_argument("exe", help="Path to the .exe file")
    run_parser.add_argument("args", nargs=argparse.REMAINDER, help="Arguments to pass to the exe")

    run_app_parser = subparsers.add_parser("run-app", help="Find and run an installed application inside a prefix")
    run_app_parser.add_argument("args", nargs=argparse.REMAINDER, help="Arguments to pass to the application")

    subparsers.add_parser("update", help="Update proton-cli to the latest version")

    args = parser.parse_args()

    if args.help or not args.command:
        print_help_table()
        return

    if args.command == "check":
        proton_path = find_existing_protons()
        
        if not proton_path:
            print(f"\n{Colors.WARNING}Proton not found in standard directories.{Colors.ENDC}")
            print("If you have Proton installed in a custom location, please enter the full path.")
            custom_path_str = input(f"{Colors.OKBLUE}Custom Proton Path (Press Enter if you don't have it installed): {Colors.ENDC}").strip()
            
            if custom_path_str:
                custom_path = Path(custom_path_str).expanduser().resolve()
                proton_exec = custom_path / "proton"
                if custom_path.is_dir() and proton_exec.exists() and os.access(proton_exec, os.X_OK):
                    print(f"{Colors.OKGREEN}[SUCCESS]{Colors.ENDC} Valid Proton version found.")
                    proton_path = custom_path
                else:
                    print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} Invalid path or 'proton' executable not found.")

            if not proton_path:
                choice = input(f"\n{Colors.WARNING}Proton not found. Do you want to download the latest GE-Proton version? (Y/n): {Colors.ENDC}")
                if choice.lower() in ["", "y", "yes"]:
                    proton_path = download_ge_proton()
                else:
                    print("Operation cancelled.")

        save_config(proton_path)
        if proton_path:
            print(f"Path to use: {proton_path}")
    elif args.command == "pull":
        new_proton = download_ge_proton()
        
        if new_proton:
            old_versions = [p for p in VERSIONS_DIR.iterdir() if p.is_dir() and p != new_proton]
            
            if old_versions:
                print(f"\n{Colors.WARNING}Found {len(old_versions)} old Proton versions in this directory.{Colors.ENDC}")
                choice = input(f"{Colors.WARNING}Do you want to delete old versions and set the new one as default? (Y/n): {Colors.ENDC}")
                
                if choice.lower() in ["", "y", "yes"]:
                    print("Cleaning old versions...")
                    for old in old_versions:
                        try:
                            shutil.rmtree(old)
                            print(f"Deleted: {old.name}")
                        except Exception as e:
                            print(f"{Colors.FAIL}Could not delete {old.name}: {e}{Colors.ENDC}")
                    
                    print("\nUpdating configuration...")
                    proton_path = find_existing_protons()
                    save_config(proton_path)
    elif args.command == "prefix-make":
        create_prefix(args.name)
    elif args.command == "winecfg":
        run_winecfg()
    elif args.command == "regedit":
        run_regedit(args.reg_file)
    elif args.command == "taskmgr":
        run_taskmgr()
    elif args.command == "uninstaller":
        run_uninstaller()
    elif args.command == "prefix-delete":
        delete_prefix()
    elif args.command == "proton-delete":
        delete_proton()
    elif args.command == "run":
        run_executable(args.exe, args.args)
    elif args.command == "run-app":
        run_installed_app(args.args)
    elif args.command == "update":
        update_self()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()