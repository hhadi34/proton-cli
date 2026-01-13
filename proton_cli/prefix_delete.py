import shutil
from .constants import Colors, PREFIXES_DIR

def delete_prefix():
    if not PREFIXES_DIR.exists():
        print(f"{Colors.WARNING}⚠ No prefixes found.{Colors.ENDC}")
        return

    prefixes = [p for p in PREFIXES_DIR.iterdir() if p.is_dir()]
    if not prefixes:
        print(f"{Colors.WARNING}⚠ No prefixes found.{Colors.ENDC}")
        return

    prefixes.sort(key=lambda x: x.name)
    print(f"\n{Colors.HEADER}Select Prefix to Delete:{Colors.ENDC}")
    for i, p in enumerate(prefixes):
        print(f" {Colors.OKBLUE}[{i+1}]{Colors.ENDC} {p.name}")

    while True:
        try:
            sel = input(f"\n{Colors.OKGREEN}Select Prefix (Number) [Enter to Cancel]: {Colors.ENDC}")
            if not sel:
                print("Operation cancelled.")
                return
            idx = int(sel) - 1
            if 0 <= idx < len(prefixes):
                selected = prefixes[idx]
                confirm = input(f"{Colors.FAIL}⚠ '{selected.name}' prefix will be deleted. Are you sure? (Y/n): {Colors.ENDC}")
                if confirm.lower() in ["y", "yes"]:
                    try:
                        shutil.rmtree(selected)
                        print(f"{Colors.OKGREEN}✔ Prefix deleted.{Colors.ENDC}")
                    except Exception as e:
                        print(f"{Colors.FAIL}✖ Deletion failed: {e}{Colors.ENDC}")
                else:
                    print("Deletion cancelled.")
                break
            print(f"{Colors.FAIL}✖ Invalid selection.{Colors.ENDC}")
        except ValueError:
            print(f"{Colors.FAIL}✖ Please enter a number.{Colors.ENDC}")