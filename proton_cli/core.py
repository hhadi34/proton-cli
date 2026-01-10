import os
import sys
from .constants import BASE_DIR, Colors

def get_proton_env(prefix_path, runtime_path=None):
    """Returns the environment variables required for Proton."""
    env = os.environ.copy()
    env["STEAM_COMPAT_DATA_PATH"] = str(prefix_path)
    
    if runtime_path and runtime_path.exists():
        env["STEAM_COMPAT_CLIENT_INSTALL_PATH"] = str(runtime_path.parent.parent.parent)
    else:
        env["STEAM_COMPAT_CLIENT_INSTALL_PATH"] = str(BASE_DIR)
    return env

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