import os
import sys
import shutil
import urllib.request
import tarfile
from .constants import Colors, RUNTIMES_DIR

RUNTIME_URL = "https://repo.steampowered.com/steamrt-images-sniper/snapshots/latest-public-stable/SteamLinuxRuntime_sniper.tar.xz"
META_FILE = RUNTIMES_DIR / "sniper_version.txt"
RUNTIME_PATH = RUNTIMES_DIR / "SteamLinuxRuntime_sniper"

def print_progress_bar(action, percent):
    if percent > 100: percent = 100
    bar_length = 40
    filled_length = int(bar_length * percent // 100)
    bar = '=' * filled_length + '-' * (bar_length - filled_length)
    sys.stdout.write(f'\r{Colors.OKBLUE}{action}:{Colors.ENDC} [{Colors.OKGREEN}{bar}{Colors.ENDC}] {percent}%')
    sys.stdout.flush()

def download_progress_hook(count, block_size, total_size):
    if total_size > 0:
        percent = int(count * block_size * 100 / total_size)
        print_progress_bar("Downloading", percent)

def pull_runtime():
    print(f"{Colors.HEADER}➜ Checking Steam Linux Runtime (Sniper)...{Colors.ENDC}")
    
    try:
        req = urllib.request.Request(RUNTIME_URL, method='HEAD', headers={'User-Agent': 'proton-cli'})
        with urllib.request.urlopen(req) as response:
            remote_last_modified = response.headers.get('Last-Modified')
            
        if RUNTIME_PATH.exists():
            local_last_modified = None
            if META_FILE.exists():
                with open(META_FILE, 'r') as f:
                    local_last_modified = f.read().strip()
            
            if local_last_modified and remote_last_modified and local_last_modified == remote_last_modified:
                print(f"{Colors.OKGREEN}✔ You already have the latest runtime.{Colors.ENDC}")
                return
            
            print(f"{Colors.WARNING}⚠ Runtime found but might be outdated.{Colors.ENDC}")
            choice = input(f"{Colors.OKGREEN}Do you want to update/re-download? (Y/n): {Colors.ENDC}")
            if choice.lower() not in ["y", "yes", ""]:
                return
            
            print(f"{Colors.GRAY}Removing old runtime...{Colors.ENDC}")
            shutil.rmtree(RUNTIME_PATH)

        RUNTIMES_DIR.mkdir(parents=True, exist_ok=True)
        tar_path = RUNTIMES_DIR / "runtime.tar.xz"
        
        print(f"Downloading from Steam Repo...")
        urllib.request.urlretrieve(RUNTIME_URL, tar_path, reporthook=download_progress_hook)
        print()
        
        print(f"{Colors.OKBLUE}Extracting archive...{Colors.ENDC}")
        with tarfile.open(tar_path, "r:xz") as tar:
            members = tar.getmembers()
            total_files = len(members)
            for i, member in enumerate(members):
                if member.name.startswith("/") or ".." in member.name:
                    continue
                tar.extract(member, path=RUNTIMES_DIR)
                percent = int((i + 1) * 100 / total_files)
                print_progress_bar("Extracting", percent)
        print()
            
        os.remove(tar_path)
        
        if remote_last_modified:
            with open(META_FILE, 'w') as f:
                f.write(remote_last_modified)
                
        print(f"{Colors.OKGREEN}✔ Runtime installed successfully.{Colors.ENDC}")
        print(f"{Colors.GRAY}Run 'proton-cli check' to apply changes.{Colors.ENDC}")
                
    except Exception as e:
        print(f"{Colors.FAIL}✖ Error occurred: {e}{Colors.ENDC}")