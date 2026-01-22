import os
import sys
import json
import urllib.request
import tarfile
from .constants import Colors, VERSIONS_DIR, GE_PROTON_API_URL

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

def pull_proton():
    print(f"{Colors.HEADER}➜ Starting GE-Proton Download...{Colors.ENDC}")
    
    try:
        download_progress_hook.last_percent = -1
        req = urllib.request.Request(GE_PROTON_API_URL, headers={'User-Agent': 'proton-cli'})
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