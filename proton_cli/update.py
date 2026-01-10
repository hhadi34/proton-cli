import json
import urllib.request
import re
import sys
from pathlib import Path
from .constants import Colors, VERSION

REPO_API_URL = "https://api.github.com/repos/hhadi34/proton-cli/contents/proton_cli"
RAW_CONSTANTS_URL = "https://raw.githubusercontent.com/hhadi34/proton-cli/main/proton_cli/constants.py"

def get_remote_version():
    try:
        with urllib.request.urlopen(RAW_CONSTANTS_URL) as response:
            content = response.read().decode('utf-8')
            match = re.search(r'VERSION\s*=\s*"([^"]+)"', content)
            if match:
                return match.group(1)
    except Exception:
        return None
    return None

def parse_version(version_str):
    try:
        return tuple(map(int, version_str.split('.')))
    except (ValueError, AttributeError):
        return (0,)

def update_self():
    print(f"{Colors.HEADER}➜ Checking for updates...{Colors.ENDC}")
    
    remote_version = get_remote_version()
    
    if not remote_version:
        print(f"{Colors.FAIL}✖ Could not fetch update information.{Colors.ENDC}")
        return

    print(f"  Current Version: {Colors.OKBLUE}{VERSION}{Colors.ENDC}")
    print(f"  Latest Version:  {Colors.OKGREEN}{remote_version}{Colors.ENDC}")

    if parse_version(remote_version) > parse_version(VERSION):
        print(f"\n{Colors.WARNING}⚠ New version available!{Colors.ENDC}")
        choice = input(f"{Colors.OKGREEN}Do you want to update? (Y/n): {Colors.ENDC}")
        if choice.lower() not in ["", "y", "yes"]:
            return
    else:
        print(f"\n{Colors.OKGREEN}✔ You are using the latest version.{Colors.ENDC}")
        return

    print(f"\n{Colors.HEADER}➜ Updating...{Colors.ENDC}")
    
    try:
        req = urllib.request.Request(REPO_API_URL, headers={'User-Agent': 'proton-cli'})
        with urllib.request.urlopen(req) as response:
            files = json.loads(response.read().decode())
        
        py_files = [f for f in files if f['name'].endswith('.py')]
        
        if not py_files:
            print(f"{Colors.FAIL}✖ No files found to update.{Colors.ENDC}")
            return

        current_dir = Path(__file__).parent
        
        for file_info in py_files:
            file_name = file_info['name']
            download_url = file_info['download_url']
            dest_path = current_dir / file_name
            
            print(f"  Downloading: {Colors.OKBLUE}{file_name}{Colors.ENDC}")
            urllib.request.urlretrieve(download_url, dest_path)
            
        print(f"\n{Colors.OKGREEN}✔ Update complete!.{Colors.ENDC}")
        
    except PermissionError:
        print(f"{Colors.FAIL}✖ Permission denied. Try running with sudo.{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}✖ Update failed: {e}{Colors.ENDC}")