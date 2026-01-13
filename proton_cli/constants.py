from pathlib import Path

class Colors:
    HEADER = '\033[1;38;5;46m'
    OKBLUE = '\033[38;5;49m'
    OKGREEN = '\033[38;5;118m'
    WARNING = '\033[38;5;226m'
    FAIL = '\033[38;5;196m'
    GRAY = '\033[38;5;240m'
    ENDC = '\033[0m'

VERSION = "2.1.1"


GE_PROTON_API_URL = "https://api.github.com/repos/GloriousEggroll/proton-ge-custom/releases/latest"
REPO_UPDATE_API_URL = "https://api.github.com/repos/hhadi34/proton-cli/contents/proton_cli"


BASE_DIR = Path.home() / ".proton-cli"
CONFIG_FILE = BASE_DIR / "config.json"
PREFIXES_DIR = BASE_DIR / "prefixes"
VERSIONS_DIR = BASE_DIR / "versions"
RUNTIME_DIR = BASE_DIR / "runtime"


RUNTIME_SEARCH_PATHS = [
    Path.home() / ".steam/steam/steamapps/common",
    Path.home() / ".steam/root/steamapps/common",
    Path.home() / ".local/share/Steam/steamapps/common",
    Path.home() / ".var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common",
    Path.home() / "snap/steam/common/.local/share/Steam/steamapps/common",
]

SEARCH_PATHS = [
    Path.home() / ".steam/steam/steamapps/common",
    Path.home() / ".steam/root/steamapps/common",
    Path.home() / ".local/share/Steam/steamapps/common",
    Path.home() / ".steam/steam/compatibilitytools.d",
    Path.home() / ".steam/root/compatibilitytools.d",
    Path.home() / ".local/share/Steam/compatibilitytools.d",
    Path.home() / ".var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common",
    Path.home() / ".var/app/com.valvesoftware.Steam/.local/share/Steam/compatibilitytools.d",
    Path.home() / "snap/steam/common/.local/share/Steam/steamapps/common",
    Path.home() / "snap/steam/common/.local/share/Steam/compatibilitytools.d",
    Path.home() / ".config/heroic/tools/proton",
    Path.home() / ".config/heroic/tools/wine",
    Path.home() / ".var/app/com.heroicgameslauncher.hgl/config/heroic/tools/proton",
    Path.home() / ".var/app/com.heroicgameslauncher.hgl/config/heroic/tools/wine",
    Path.home() / ".local/share/lutris/runners/wine",
    Path.home() / ".local/share/lutris/runners/proton",
    Path.home() / ".var/app/net.lutris.Lutris/data/lutris/runners/wine",
    Path.home() / ".var/app/net.lutris.Lutris/data/lutris/runners/proton",
    Path.home() / ".local/share/bottles/runners/wine",
    Path.home() / ".local/share/bottles/runners/proton",
    Path.home() / ".var/app/com.usebottles.bottles/data/bottles/runners/wine",
    Path.home() / ".var/app/com.usebottles.bottles/data/bottles/runners/proton",
    Path("/usr/share/steam/compatibilitytools.d"),
    Path("/usr/local/share/steam/compatibilitytools.d"),
    VERSIONS_DIR,
]