import os
import shutil
import subprocess
import tempfile
import re

def check_tool_exists(tool):
    """Check if a command-line tool exists in PATH."""
    from shutil import which
    return which(tool) is not None

def patch_and_sign_apk(input_apk, final_apk,
                       min_sdk=24, target_sdk=33,
                       keystore=None, keyalias="androiddebugkey",
                       storepass="android", keypass="android"):
    """
    Patch APK's manifest for modern Android, align & sign.
    Args:
        input_apk: path to original APK
        final_apk: path to output signed APK
        min_sdk: minimum SDK version for manifest patch
        target_sdk: target SDK version for manifest patch
        keystore: path to keystore (debug by default)
        keyalias: keystore alias
        storepass: keystore password
        keypass: key password
    Returns:
        True on success, False on error
    """
    required_tools = ["apktool", "apksigner", "zipalign", "zip", "unzip"]
    for tool in required_tools:
        if not check_tool_exists(tool):
            print(f"[ERROR] Required tool '{tool}' not found in PATH.")
            return False

    if not os.path.isfile(input_apk):
        print(f"[ERROR] Input APK not found: {input_apk}")
        return False

    if not keystore:
        keystore = os.path.expanduser("~/.android/debug.keystore")

    work_dir = tempfile.mkdtemp(prefix="apkpatch_")
    decoded = os.path.join(work_dir, "decoded")
    patched_apk = os.path.join(work_dir, "patched.apk")
    aligned_apk = os.path.join(work_dir, "aligned.apk")
    signed_apk = os.path.join(work_dir, "signed.apk")

    try:
        # Decode APK
        print("[*] Decoding APK...")
        subprocess.run(["apktool", "d", input_apk, "-o", decoded, "-f"], check=True, capture_output=True)

        # Patch AndroidManifest.xml
        print("[*] Patching AndroidManifest.xml...")
        manifest = os.path.join(decoded, "AndroidManifest.xml")
        if not os.path.isfile(manifest):
            print("[ERROR] Failed to find AndroidManifest.xml after decoding.")
            return False

        with open(manifest, "r") as f:
            manifest_data = f.read()

        # Patch <uses-sdk>
        uses_sdk_pattern = r"<uses-sdk[^>]*>"
        uses_sdk_repl = f'<uses-sdk android:minSdkVersion="{min_sdk}" android:targetSdkVersion="{target_sdk}"/>'
        if re.search(uses_sdk_pattern, manifest_data):
            manifest_data = re.sub(uses_sdk_pattern, uses_sdk_repl, manifest_data)
        else:
            manifest_data = re.sub(r"(<application[^>]*>)", f"{uses_sdk_repl}\n\\1", manifest_data, count=1)

        # Ensure android:exported="true" for all components (activity/service/receiver) with intent-filter
        def add_exported_to_components(xml):
            # Regex for <activity ...> ... <intent-filter> ... </activity>
            def repl(match):
                tag_open = match.group(1)
                rest = match.group(2)
                # Only add exported if not present
                if 'android:exported' not in tag_open:
                    # Insert before last '>'
                    tag_open = tag_open.rstrip('>') + ' android:exported="true">'
                return tag_open + rest
            # For activities
            activity_pattern = r'(<activity\b[^>]*)(>[\s\S]*?<intent-filter[\s\S]*?</activity>)'
            xml = re.sub(activity_pattern, repl, xml, flags=re.MULTILINE)
            # For services
            service_pattern = r'(<service\b[^>]*)(>[\s\S]*?<intent-filter[\s\S]*?</service>)'
            xml = re.sub(service_pattern, repl, xml, flags=re.MULTILINE)
            # For receivers
            receiver_pattern = r'(<receiver\b[^>]*)(>[\s\S]*?<intent-filter[\s\S]*?</receiver>)'
            xml = re.sub(receiver_pattern, repl, xml, flags=re.MULTILINE)
            return xml

        manifest_data = add_exported_to_components(manifest_data)

        with open(manifest, "w") as f:
            f.write(manifest_data)

        # Rebuild APK
        print("[*] Rebuilding APK...")
        subprocess.run(["apktool", "b", decoded, "-o", patched_apk], check=True, capture_output=True)

        # Uncompress resources.arsc if needed
        print("[*] Checking resources.arsc compression...")
        zip_list = subprocess.run(["unzip", "-lv", patched_apk], capture_output=True, text=True)
        if "resources.arsc" in zip_list.stdout and "Defl" in zip_list.stdout:
            subprocess.run(["unzip", "-o", patched_apk, "resources.arsc", "-d", work_dir], check=True)
            subprocess.run(["zip", "-d", patched_apk, "resources.arsc"], check=True)
            subprocess.run(["zip", "-0", "-X", patched_apk, os.path.join(work_dir, "resources.arsc")], check=True)

        # Align APK
        print("[*] Aligning APK...")
        subprocess.run(["zipalign", "-p", "-f", "4", patched_apk, aligned_apk], check=True, capture_output=True)

        # Sign APK
        print("[*] Signing APK...")
        subprocess.run([
            "apksigner", "sign",
            "--ks", keystore,
            "--ks-key-alias", keyalias,
            "--ks-pass", f"pass:{storepass}",
            "--key-pass", f"pass:{keypass}",
            "--out", signed_apk,
            aligned_apk
        ], check=True, capture_output=True)

        # Copy signed APK to final location
        shutil.copy2(signed_apk, final_apk)
        print(f"[+] Done! Final APK: {final_apk}")
        print(f"[i] Temporary files left in: {work_dir} (for debugging; remove when done)")
        return True

    except subprocess.CalledProcessError as e:
        print("[ERROR] Tool failed:", e)
        if hasattr(e, "stderr") and e.stderr:
            print(e.stderr.decode() if isinstance(e.stderr, bytes) else e.stderr)
        return False
    except Exception as e:
        print("[ERROR]", str(e))
        return False
