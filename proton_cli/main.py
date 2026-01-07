import sys
import argparse
import shutil
import os
from pathlib import Path
from .constants import Colors, VERSION, VERSIONS_DIR
from .config import save_config, load_config
from .proton import find_existing_protons, download_ge_proton, delete_proton

def print_help_table():
    banner = r"""
  ____            _                    ____ _     ___ 
|  _ \ _ __ ___ | |_ ___  _ __       / ___| |   |_ _|
| |_) | '__/ _ \| __/ _ \| '_ \_____| |   | |    | | 
|  __/| | | (_) | || (_) | | | |____| |___| |___ | | 
|_|   |_|  \___/ \__\___/|_| |_|     \____|_____|___|
"""
    print(f"{Colors.HEADER}{banner}{Colors.ENDC}")
    print(f"                                            {Colors.GRAY}v{VERSION}{Colors.ENDC}\n")
    
    print(f"{Colors.HEADER}{'Command':<25} {'Description':<55}{Colors.ENDC}")
    print(f"{Colors.GRAY}" + "-" * 80 + f"{Colors.ENDC}")
    commands = [
        ("check", "Scan and configure Proton versions on the system"),
        ("pull", "Download the latest GE-Proton version"),
        ("proton-delete", "Delete downloaded Proton versions"),
        ("prefix-make <name>", "Create a new Wine prefix"),
        ("winecfg", "Open Wine configuration for a prefix"),
        ("regedit <file>", "Apply a .reg file to a prefix"),
        ("regsvr32 [args]", "Register/Unregister DLLs in a prefix"),
        ("taskmgr", "Open Task Manager for a prefix"),
        ("uninstaller", "Open Add/Remove Programs for a prefix"),
        ("open-prefix", "Open the drive_c folder of a prefix"),
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
            print(f"{Colors.FAIL}✖ {message}{Colors.ENDC}")
            print(f"Use {Colors.OKGREEN}proton-cli -h{Colors.ENDC} to see available commands.")
            sys.exit(2)

    parser = CustomParser(description="Proton-CLI", add_help=False)
    parser.add_argument('-h', '--help', action='store_true', help="Show help menu")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("check", help="Scan and configure Proton versions on the system")
    subparsers.add_parser("pull", help="Download the latest GE-Proton version")
    subparsers.add_parser("proton-delete", help="Delete downloaded Proton versions")

    prefix_parser = subparsers.add_parser("prefix-make", help="Create a new Wine prefix")
    prefix_parser.add_argument("name", nargs='?', help="Name for the prefix")

    subparsers.add_parser("winecfg", help="Open Wine configuration for a prefix")

    regedit_parser = subparsers.add_parser("regedit", help="Apply a .reg file to a prefix")
    regedit_parser.add_argument("reg_file", help="Path to the .reg file")

    regsvr_parser = subparsers.add_parser("regsvr32", help="Register/Unregister DLLs in a prefix")
    regsvr_parser.add_argument("args", nargs=argparse.REMAINDER, help="Arguments for regsvr32")

    subparsers.add_parser("taskmgr", help="Open Task Manager for a prefix")
    subparsers.add_parser("uninstaller", help="Open Add/Remove Programs for a prefix")
    subparsers.add_parser("open-prefix", help="Open the drive_c folder of a prefix")
    subparsers.add_parser("prefix-delete", help="Delete an existing Wine prefix")

    run_parser = subparsers.add_parser("run", help="Run an .exe file")
    run_parser.add_argument("-p", "--prefix", help="Name of the prefix to use")
    run_parser.add_argument("-o", "--options", help="Launch options (env vars and wrappers)")
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
            print(f"\n{Colors.WARNING}⚠ Proton not found in standard directories.{Colors.ENDC}")
            print("If you have Proton installed in a custom location, please enter the full path.")
            custom_path_str = input(f"{Colors.OKGREEN}Custom Proton Path (Press Enter if you don't have it installed): {Colors.ENDC}").strip()
            
            if custom_path_str:
                custom_path = Path(custom_path_str).expanduser().resolve()
                proton_exec = custom_path / "proton"
                if custom_path.is_dir() and proton_exec.exists() and os.access(proton_exec, os.X_OK):
                    print(f"{Colors.OKGREEN}✔ Valid Proton version found.{Colors.ENDC}")
                    proton_path = custom_path
                else:
                    print(f"{Colors.FAIL}✖ Invalid path or 'proton' executable not found.{Colors.ENDC}")

            if not proton_path:
                choice = input(f"\n{Colors.WARNING}⚠ Proton not found. Do you want to download the latest GE-Proton version? (Y/n): {Colors.ENDC}")
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
                print(f"\n{Colors.WARNING}⚠ Found {len(old_versions)} old Proton versions in this directory.{Colors.ENDC}")
                choice = input(f"{Colors.OKGREEN}Do you want to delete old versions and set the new one as default? (Y/n): {Colors.ENDC}")
                
                if choice.lower() in ["", "y", "yes"]:
                    print("Cleaning old versions...")
                    for old in old_versions:
                        try:
                            shutil.rmtree(old)
                            print(f"Deleted: {old.name}")
                        except Exception as e:
                            print(f"{Colors.FAIL}✖ Could not delete {old.name}: {e}{Colors.ENDC}")
                    
                    print("\nUpdating configuration...")
                    proton_path = find_existing_protons()
                    save_config(proton_path)

    elif args.command == "proton-delete":
        delete_proton()

    # Lazy imports for modules not yet created
    elif args.command == "prefix-make":
        from .prefix import create_prefix
        name = args.name
        if not name:
            name = input(f"{Colors.OKGREEN}Enter name for new prefix: {Colors.ENDC}").strip()
        if name: create_prefix(name)
    elif args.command == "winecfg":
        from .wine import run_winecfg; run_winecfg()
    elif args.command == "regedit":
        from .wine import run_regedit; run_regedit(args.reg_file)
    elif args.command == "regsvr32":
        from .wine import run_regsvr32; run_regsvr32(args.args)
    elif args.command == "taskmgr":
        from .wine import run_taskmgr; run_taskmgr()
    elif args.command == "uninstaller":
        from .wine import run_uninstaller; run_uninstaller()
    elif args.command == "open-prefix":
        from .prefix import open_prefix_drive; open_prefix_drive()
    elif args.command == "prefix-delete":
        from .prefix import delete_prefix; delete_prefix()
    elif args.command == "run":
        from .app import run_executable; run_executable(args.exe, args.args, prefix_name=args.prefix, user_options=args.options)
    elif args.command == "run-app":
        from .app import run_installed_app; run_installed_app(args.args)
    elif args.command == "update":
        from .update import update_self; update_self()

if __name__ == "__main__":
    main()
