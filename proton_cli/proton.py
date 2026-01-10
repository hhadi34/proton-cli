import os
import sys
import json
import urllib.request
import tarfile
import shutil
from pathlib import Path
from .constants import Colors, SEARCH_PATHS, VERSIONS_DIR, RUNTIME_SEARCH_PATHS
from .config import save_config, load_config
from .core import download_progress_hook, print_progress_bar

def find_existing_protons():
    """Searches for Proton installations in common system directories."""
    print(f"{Colors.HEADER}➜ Scanning for Proton Versions...{Colors.ENDC}")
    
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
                        print(f" {Colors.OKGREEN}✔{Colors.ENDC} {item.name} {Colors.GRAY}→ {path}{Colors.ENDC}")
        except PermissionError:
            print(f"{Colors.WARNING}⚠ Could not access directory {path}.{Colors.ENDC}")
            continue

    if found_protons:
        found_protons.sort(key=lambda x: x.name, reverse=False)
        
        print(f"\n{Colors.HEADER}Found Proton Versions:{Colors.ENDC}")
        for i, proton in enumerate(found_protons):
            print(f" {Colors.OKBLUE}[{i+1}]{Colors.ENDC} {proton.name} {Colors.GRAY}({proton.parent}){Colors.ENDC}")
            
        if len(found_protons) > 1:
            while True:
                try:
                    selection = input(f"\n{Colors.OKGREEN}Select version (Default: 1): {Colors.ENDC}")
                    if not selection:
                        selection = 1
                    selection = int(selection)
                    if 1 <= selection <= len(found_protons):
                        best_proton = found_protons[selection - 1]
                        break
                    print(f"{Colors.FAIL}✖ Invalid selection.{Colors.ENDC}")
                except ValueError:
                    print(f"{Colors.FAIL}✖ Please enter a valid number.{Colors.ENDC}")
        else:
            best_proton = found_protons[0]
            
        print(f"\n{Colors.OKGREEN}➜ Selected Proton:{Colors.ENDC} {best_proton.name}")
        return best_proton
    
    print(f"\n{Colors.FAIL}✖ No installed Proton version found on the system.{Colors.ENDC}")
    return None

def find_steam_runtime():
    """Searches for Steam Runtime installations."""
    print(f"{Colors.HEADER}➜ Scanning for Steam Runtime...{Colors.ENDC}")
    
    runtime_names = ["SteamLinuxRuntime_sniper", "SteamLinuxRuntime_soldier", "SteamLinuxRuntime"]
    found_runtimes = []

    for path in RUNTIME_SEARCH_PATHS:
        if not path.exists():
            continue
            
        for name in runtime_names:
            runtime_path = path / name
            if runtime_path.exists() and runtime_path.is_dir():
                found_runtimes.append(runtime_path)

    if found_runtimes:
        found_runtimes.sort(key=lambda x: runtime_names.index(x.name) if x.name in runtime_names else 99)
        best_runtime = found_runtimes[0]
        print(f"{Colors.OKGREEN}✔ Found Steam Runtime:{Colors.ENDC} {best_runtime.name}")
        return best_runtime
    
    print(f"{Colors.WARNING}⚠ Steam Runtime not found. Applications will run with system libraries.{Colors.ENDC}")
    return None

def download_ge_proton():
    print(f"{Colors.HEADER}➜ Starting GE-Proton Download...{Colors.ENDC}")
    
    api_url = "https://api.github.com/repos/GloriousEggroll/proton-ge-custom/releases/latest"
    
    try:
        req = urllib.request.Request(api_url, headers={'User-Agent': 'proton-cli'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            
        tag_name = data["tag_name"]
        print(f"Latest version: {Colors.OKGREEN}{tag_name}{Colors.ENDC}")
        
        if VERSIONS_DIR.exists():
            for item in VERSIONS_DIR.iterdir():
                if item.is_dir() and tag_name in item.name:
                    print(f"{Colors.OKBLUE}✔ Latest GE-Proton version ({tag_name}) is already installed.{Colors.ENDC}")
                    return item
        
        download_url = None
        for asset in data["assets"]:
            if asset["name"].endswith(".tar.gz"):
                download_url = asset["browser_download_url"]
                break
        
        if not download_url:
            print(f"{Colors.FAIL}✖ Download link not found.{Colors.ENDC}")
            return None

        VERSIONS_DIR.mkdir(parents=True, exist_ok=True)
        tar_path = VERSIONS_DIR / f"{tag_name}.tar.gz"

        print(f"Downloading from GitHub...")
        urllib.request.urlretrieve(download_url, tar_path, reporthook=download_progress_hook)
        print()
        
        print(f"{Colors.OKBLUE}Extracting archive...{Colors.ENDC}")
        with tarfile.open(tar_path, "r:gz") as tar:
            members = tar.getmembers()
            total_files = len(members)
            for i, member in enumerate(members):
                if member.name.startswith("/") or ".." in member.name:
                    continue
                
                tar.extract(member, path=VERSIONS_DIR)
                percent = int((i + 1) * 100 / total_files)
                print_progress_bar("Extracting", percent)
        print()
            
        os.remove(tar_path)
        
        for item in VERSIONS_DIR.iterdir():
            if item.is_dir() and tag_name in item.name:
                print(f"{Colors.OKGREEN}✔ Installation complete:{Colors.ENDC} {item.name}")
                return item
                
    except Exception as e:
        print(f"{Colors.FAIL}✖ Error occurred during download: {e}{Colors.ENDC}")
        return None

def delete_proton():
    print(f"{Colors.HEADER}➜ Scanning for Proton Versions to Delete...{Colors.ENDC}")
    versions = []
    
    for path in SEARCH_PATHS:
        if not path.exists():
            continue
            
        try:
            for item in path.iterdir():
                if item.is_dir() and (item / "proton").exists():
                    versions.append(item)
        except Exception:
            continue

    if not versions:
        print(f"{Colors.WARNING}⚠ No Proton versions found.{Colors.ENDC}")
        return

    versions.sort(key=lambda x: x.name)
    print(f"\n{Colors.HEADER}Select Proton Version to Delete:{Colors.ENDC}")
    for i, p in enumerate(versions):
        print(f" {Colors.OKBLUE}[{i+1}]{Colors.ENDC} {p.name} {Colors.GRAY}({p.parent}){Colors.ENDC}")

    while True:
        try:
            sel = input(f"\n{Colors.OKGREEN}Select Version (Number) [Enter to Cancel]: {Colors.ENDC}")
            if not sel:
                print("Operation cancelled.")
                return
            idx = int(sel) - 1
            if 0 <= idx < len(versions):
                selected = versions[idx]
                confirm = input(f"{Colors.FAIL}⚠ '{selected.name}' version will be deleted. Are you sure? (Y/n): {Colors.ENDC}")
                if confirm.lower() in ["y", "yes"]:
                    try:
                        shutil.rmtree(selected)
                        print(f"{Colors.OKGREEN}✔ Version deleted.{Colors.ENDC}")
                        
                        conf = load_config()
                        current_path = conf.get("proton_path")
                        if current_path and current_path.resolve() == selected.resolve():
                            print(f"{Colors.WARNING}⚠ Deleted version was set as default. Clearing configuration...{Colors.ENDC}")
                            save_config(None, conf.get("runtime_path"))
                    except Exception as e:
                        print(f"{Colors.FAIL}✖ Deletion failed: {e}{Colors.ENDC}")
                else:
                    print("Deletion cancelled.")
                break
            print(f"{Colors.FAIL}✖ Invalid selection.{Colors.ENDC}")
        except ValueError:
            print(f"{Colors.FAIL}✖ Please enter a number.{Colors.ENDC}")