import subprocess
from .constants import Colors, PREFIXES_DIR

def open_prefix_drive():
    if not PREFIXES_DIR.exists():
        print(f"{Colors.WARNING}⚠ No prefixes found.{Colors.ENDC}")
        return

    prefixes = [p for p in PREFIXES_DIR.iterdir() if p.is_dir()]
    if not prefixes:
        print(f"{Colors.WARNING}⚠ No prefixes found.{Colors.ENDC}")
        return

    prefixes.sort(key=lambda x: x.name)
    print(f"\n{Colors.HEADER}Select Prefix to Open:{Colors.ENDC}")
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

    drive_c = selected_prefix / "pfx" / "drive_c"
    if not drive_c.exists():
        drive_c = selected_prefix / "drive_c"
    
    print(f"{Colors.OKBLUE}➜ Opening: {drive_c}{Colors.ENDC}")
    try:
        subprocess.run(["xdg-open", str(drive_c)])
    except Exception as e:
        print(f"{Colors.FAIL}✖ Failed to open file manager: {e}{Colors.ENDC}")