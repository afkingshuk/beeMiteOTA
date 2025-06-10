import subprocess
import sys
import importlib
import os

def check_and_install_requirements(requirements_file):
    print("\n🔍 Checking required packages...")

    if not os.path.isfile(requirements_file):
        print(f"⚠️ requirements.txt not found: {requirements_file}")
        return

    with open(requirements_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            package_name = line.split("==")[0].strip()
            import_name = package_name.replace("-", "_")

            # Known exceptions
            special_imports = {
                "opencv-python-headless": "cv2",
                "Pillow": "PIL",
                "scikit-learn": "sklearn",
                "PyYAML": "yaml",
                "python-dateutil": "dateutil",
            }
            import_name = special_imports.get(package_name, import_name)

            try:
                importlib.import_module(import_name)
                print(f"✅ PACKAGE OK: {package_name}")
            except ImportError:
                print(f"❌ MISSING PACKAGE: {package_name}. Installing...")
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
                    print(f"✅ Installed: {package_name}")
                except subprocess.CalledProcessError:
                    print(f"⚠️ Failed to install {package_name}. Please check manually.")

    print("✅ Package check complete.\n")
