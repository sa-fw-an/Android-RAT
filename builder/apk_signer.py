import os
import subprocess
import shutil
from glob import glob

KEYSTORE_FILE = os.path.expanduser("~/.android/debug.keystore")
KEY_ALIAS = "androiddebugkey"
KEY_PASS = "android"
KEYSTORE_PASS = "android"

def find_apksigner():
    """Check if apksigner is in PATH, else prompt for location."""
    if shutil.which("apksigner"):
        return "apksigner"
    else:
        print("apksigner not found in $PATH.")
        custom = input("Enter full path to apksigner or leave blank to abort: ").strip()
        if custom and os.path.isfile(custom) and os.access(custom, os.X_OK):
            return custom
        else:
            print("apksigner not found or not executable. Aborting.")
            return None

def ensure_debug_keystore():
    """Generate debug keystore if missing."""
    if os.path.exists(KEYSTORE_FILE):
        return True
    # Ensure the parent directory exists
    parent_dir = os.path.dirname(KEYSTORE_FILE)
    if not os.path.exists(parent_dir):
        try:
            os.makedirs(parent_dir)
        except Exception as e:
            print(f"Failed to create directory {parent_dir}: {e}")
            return False
    print("Debug keystore not found. Generating one...")
    keytool_path = shutil.which("keytool")
    if not keytool_path:
        print("keytool not found. Please install OpenJDK.")
        return False
    cmd = [
        keytool_path, "-genkey", "-v",
        "-keystore", KEYSTORE_FILE,
        "-storepass", KEYSTORE_PASS,
        "-alias", KEY_ALIAS,
        "-keypass", KEY_PASS,
        "-keyalg", "RSA",
        "-keysize", "2048",
        "-validity", "10000",
        "-dname", "CN=Android Debug,O=Android,C=US"
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("Debug keystore generated at", KEYSTORE_FILE)
            return True
        else:
            print("Failed to generate keystore:")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print("Exception running keytool:", str(e))
        return False

def get_latest_apk():
    """Find the most recent unsigned APK in output/."""
    files = sorted(glob(os.path.join("output", "*.apk")), key=os.path.getmtime, reverse=True)
    if files:
        return files[0]
    return None

def prompt_apk_to_sign():
    """Prompt for APK to sign, defaulting to the most recent one in output/."""
    default_apk = get_latest_apk()
    prompt = "Enter path to unsigned APK"
    if default_apk:
        prompt += f" [{default_apk}]"
    prompt += ": "
    apk = input(prompt).strip()
    if not apk and default_apk:
        apk = default_apk
    if not apk or not os.path.isfile(apk):
        print("APK file not found.")
        return None
    return apk

def prompt_overwrite(filepath):
    """Warn if file exists, ask for overwrite."""
    if os.path.exists(filepath):
        ans = input(f"File {filepath} exists. Overwrite? (y/N): ").strip().lower()
        if ans != "y":
            print("Aborted by user.")
            return False
    return True

def sign_apk():
    apksigner_path = find_apksigner()
    if not apksigner_path:
        return

    if not ensure_debug_keystore():
        return

    apk_to_sign = prompt_apk_to_sign()
    if not apk_to_sign:
        return

    # Compose output filename
    base, ext = os.path.splitext(apk_to_sign)
    signed_apk = f"{base}-signed.apk"

    if not prompt_overwrite(signed_apk):
        return

    print("\nSigning APK...\n")
    cmd = [
        apksigner_path, "sign",
        "--ks", KEYSTORE_FILE,
        "--ks-key-alias", KEY_ALIAS,
        "--ks-pass", f"pass:{KEYSTORE_PASS}",
        "--key-pass", f"pass:{KEY_PASS}",
        "--out", signed_apk,
        apk_to_sign
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print("apksigner error:\n", result.stderr)
            print("Signing failed.")
            return
        print(f"APK signed! Saved as {signed_apk}")
        print("You can now install it on your device with:")
        print(f"  adb install {signed_apk}")
    except Exception as e:
        print("Exception running apksigner:", str(e))
