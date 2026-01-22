import sys
import argparse
import os
from .constants import Colors

def main():
    class CustomParser(argparse.ArgumentParser):
        def error(self, message):
            print(f"{Colors.FAIL}✖ Error: {message}{Colors.ENDC}")
            sys.exit(2)

    parser = CustomParser(add_help=False)
    parser.add_argument('-h', '--help', action='store_true')
    parser.add_argument('-d', '--debug', action='store_true')
    
    subparsers = parser.add_subparsers(dest="command")

    # Command Definitions
    subparsers.add_parser("check")
    subparsers.add_parser("pull-proton")
    subparsers.add_parser("pull-runtime")
    subparsers.add_parser("proton-delete")
    
    prefix_make = subparsers.add_parser("prefix-make")
    prefix_make.add_argument("name", nargs='?')
    
    subparsers.add_parser("winecfg")
    
    regedit = subparsers.add_parser("regedit")
    regedit.add_argument("reg_file")
    
    regsvr = subparsers.add_parser("regsvr32")
    regsvr.add_argument("args", nargs=argparse.REMAINDER)
    
    subparsers.add_parser("taskmgr")
    subparsers.add_parser("uninstaller")
    subparsers.add_parser("open-prefix")
    subparsers.add_parser("prefix-delete")
    
    run = subparsers.add_parser("run")
    run.add_argument("-p", "--prefix")
    run.add_argument("-o", "--options")
    run.add_argument("exe")
    run.add_argument("args", nargs=argparse.REMAINDER)
    
    subparsers.add_parser("update")
    subparsers.add_parser("help")

    args = parser.parse_args()

    if args.help or not args.command:
        parser.print_help()
        return

    if args.debug:
        os.environ["PROTON_CLI_DEBUG"] = "1"
        print(f"{Colors.WARNING}⚠ Debug mode enabled.{Colors.ENDC}")

    # Command Dispatcher
    if args.command == "check":
        from .check import check_proton
        check_proton()
    elif args.command == "pull-proton":
        from .pull_proton import pull_proton
        pull_proton()
    elif args.command == "pull-runtime":
        from .pull_runtime import pull_runtime
        pull_runtime()
    elif args.command == "proton-delete":
        from .proton_delete import delete_proton
        delete_proton()
    elif args.command == "prefix-make":
        from .prefix_make import create_prefix
        name = args.name
        if not name:
            name = input(f"{Colors.OKGREEN}Enter name for new prefix: {Colors.ENDC}").strip()
        if name: create_prefix(name)
    elif args.command == "winecfg":
        from .winecfg import run_winecfg
        run_winecfg()
    elif args.command == "regedit":
        from .regedit import run_regedit
        run_regedit(args.reg_file)
    elif args.command == "regsvr32":
        from .regsvr32 import run_regsvr32
        run_regsvr32(args.args)
    elif args.command == "taskmgr":
        from .taskmgr import run_taskmgr
        run_taskmgr()
    elif args.command == "uninstaller":
        from .uninstaller import run_uninstaller
        run_uninstaller()
    elif args.command == "open-prefix":
        from .prefix_open import open_prefix_drive
        open_prefix_drive()
    elif args.command == "prefix-delete":
        from .prefix_delete import delete_prefix
        delete_prefix()
    elif args.command == "run":
        from .run import run_executable
        run_executable(args.exe, args.args, prefix_name=args.prefix, user_options=args.options)
    elif args.command == "update":
        from .update import update_self
        update_self()
    elif args.command == "help":
        from .help import print_help
        print_help()

if __name__ == "__main__":
    main()
