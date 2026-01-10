import json
from pathlib import Path
from .constants import BASE_DIR, CONFIG_FILE, Colors

def save_config(proton_path, runtime_path=None):
    try:
        if not BASE_DIR.exists():
            BASE_DIR.mkdir(parents=True, exist_ok=True)
            
        data = {
            "proton_path": str(proton_path) if proton_path else None,
            "runtime_path": str(runtime_path) if runtime_path else None
        }
        
        with open(CONFIG_FILE, 'w') as f:
            json.dump(data, f, indent=4)
            
        print(f"{Colors.OKGREEN}✔ Configuration saved to: {Colors.GRAY}{CONFIG_FILE}{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}✖ Could not save configuration: {e}{Colors.ENDC}")

def load_config():
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                path_str = data.get("proton_path")
                runtime_str = data.get("runtime_path")
                return {
                    "proton_path": Path(path_str) if path_str else None,
                    "runtime_path": Path(runtime_str) if runtime_str else None
                }
        except Exception:
            return {"proton_path": None, "runtime_path": None}
    return {"proton_path": None, "runtime_path": None}