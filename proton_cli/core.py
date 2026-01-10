import os
import sys
from .constants import BASE_DIR, Colors

def get_proton_env(prefix_path, runtime_path=None, proton_path=None):
    """Returns the environment variables required for Proton."""
    env = os.environ.copy()
    env["STEAM_COMPAT_DATA_PATH"] = str(prefix_path)
    
    if runtime_path and runtime_path.exists():
        env["STEAM_COMPAT_CLIENT_INSTALL_PATH"] = str(runtime_path.parent.parent.parent)
    else:
        env["STEAM_COMPAT_CLIENT_INSTALL_PATH"] = str(BASE_DIR)

    if proton_path:
        tool_dir = proton_path.parent.parent
        env["STEAM_COMPAT_TOOL_PATHS"] = str(tool_dir)

    return env

def create_proton_command(proton_path, runtime_path, proton_args, wrappers=None):
    """
    Constructs the command list to run Proton, handling Steam Runtime wrapping.
    
    :param proton_path: Path to the Proton installation
    :param runtime_path: Path to the Steam Runtime (optional)
    :param proton_args: List of arguments for Proton (e.g. ["run", "game.exe"])
    :param wrappers: List of wrapper commands (e.g. ["gamemoderun"])
    :return: List of command parts ready for subprocess
    """
    proton_bin = str(proton_path / "proton")
    base_cmd = [proton_bin] + proton_args
    
    final_cmd = base_cmd
    
    if runtime_path and runtime_path.exists():
        # Steam Runtime (Sniper/Soldier) entry point
        runtime_run = runtime_path / "run"
        if runtime_run.exists():
            final_cmd = [str(runtime_run), "--"] + base_cmd
            
    if wrappers:
        final_cmd = wrappers + final_cmd
        
    return final_cmd

def debug_log(message):
    if os.environ.get("PROTON_CLI_DEBUG"):
        print(f"{Colors.WARNING}[DEBUG] {message}{Colors.ENDC}")

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