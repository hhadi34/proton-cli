import os
from pathlib import Path
from .constants import Colors, SEARCH_PATHS, RUNTIME_SEARCH_PATHS
from .config import save_config

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

def check_proton():
    proton_path = find_existing_protons()
    runtime_path = None
    
    if not proton_path:
        print(f"\n{Colors.WARNING}⚠ Proton not found in standard directories.{Colors.ENDC}")
        print("If you have Proton installed in a custom location, please enter the full path.")
        custom_path_str = input(f"{Colors.OKGREEN}Custom Proton Path (Press Enter to skip): {Colors.ENDC}").strip()
        
        if custom_path_str:
            input_path = Path(custom_path_str).expanduser().resolve()
            
           
            if input_path.is_file() and input_path.name == "proton":
                custom_path = input_path.parent
            else:
                custom_path = input_path

            proton_exec = custom_path / "proton"
            if custom_path.is_dir() and proton_exec.exists() and os.access(proton_exec, os.X_OK):
                print(f"{Colors.OKGREEN}✔ Valid Proton version found.{Colors.ENDC}")
                proton_path = custom_path
            else:
                print(f"{Colors.FAIL}✖ Invalid path or 'proton' executable not found.{Colors.ENDC}")

    if proton_path:
        runtime_path = find_steam_runtime()

    save_config(proton_path, runtime_path)
    if proton_path:
        print(f"Path to use: {proton_path}")