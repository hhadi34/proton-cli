from .constants import Colors, VERSION

def print_help():
    print(f"{Colors.HEADER}Proton-CLI{Colors.ENDC} {Colors.GRAY}v{VERSION}{Colors.ENDC}")
    print(f"{Colors.GRAY}Manage Proton and Wine prefixes with ease.{Colors.ENDC}\n")
    
    print(f"{Colors.HEADER}{'Command':<25} {'Description':<50}{Colors.ENDC}")
    print(f"{Colors.GRAY}{'-'*75}{Colors.ENDC}")
    
    commands = [
        ("check", "Scan and configure Proton versions"),
        ("pull-proton", "Download latest GE-Proton"),
        ("pull-runtime", "Download Steam Linux Runtime (Sniper)"),
        ("proton-delete", "Delete Proton versions"),
        ("prefix-make [name]", "Create a new Wine prefix"),
        ("prefix-delete", "Delete an existing prefix"),
        ("open-prefix", "Open prefix drive_c"),
        ("run <exe>", "Run an executable"),
        ("winecfg", "Open Wine configuration"),
        ("regedit <file>", "Apply .reg file"),
        ("regsvr32 <args>", "Register/Unregister DLLs"),
        ("taskmgr", "Open Task Manager"),
        ("uninstaller", "Open Uninstaller"),
        ("update", "Update proton-cli"),
        ("help", "Show this help message")
    ]
    
    for cmd, desc in commands:
        print(f"{Colors.OKGREEN}{cmd:<25}{Colors.ENDC} {desc}")
    print()