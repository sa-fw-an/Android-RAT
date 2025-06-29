import os
import re
import subprocess
import shutil
import tempfile

APKTOOL = "apktool"
ZIPALIGN = "zipalign"
APKSIGNER = "apksigner"

def run(cmd):
    print(f"[+] Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    if result.returncode != 0:
        raise Exception(f"Command failed: {' '.join(cmd)}")

def fix_manifest_resources(manifest):
    # Replace all label or icon resource IDs like @2130837504 with safe values
    manifest = re.sub(r'android:label="@[0-9a-fA-Fx]+"', 'android:label="App"', manifest)
    manifest = re.sub(r'android:icon="@[0-9a-fA-Fx]+"', '', manifest)
    return manifest

def patch_manifest(manifest_path):
    with open(manifest_path, "r") as f:
        manifest = f.read()
    manifest = fix_manifest_resources(manifest)
    # If MainActivity is already present, skip adding it
    if "android:name=\".MainActivity\"" in manifest:
        print("[*] MainActivity already present in manifest.")
    else:
        # Add MainActivity to manifest, right after <application ...>
        replacement = "<application"
        activity = """
    <activity android:name=".MainActivity"
        android:exported="true"
        android:theme="@android:style/Theme.Translucent.NoTitleBar.Fullscreen">
        <intent-filter>
            <action android:name="android.intent.action.MAIN"/>
            <category android:name="android.intent.category.LAUNCHER"/>
        </intent-filter>
    </activity>
    """
        manifest = manifest.replace(replacement, replacement + activity, 1)
        print("[+] Patched MainActivity into AndroidManifest.xml.")
    with open(manifest_path, "w") as f:
        f.write(manifest)

def add_main_activity(smali_dir):
    main_activity_smali = os.path.join(smali_dir, "MainActivity.smali")
    if os.path.exists(main_activity_smali):
        print("[*] MainActivity.smali already exists.")
        return
    content = """
.class public LMainActivity;
.super Landroid/app/Activity;

.method public onCreate(Landroid/os/Bundle;)V
    .locals 1
    invoke-super {p0, p1}, Landroid/app/Activity;->onCreate(Landroid/os/Bundle;)V
    return-void
.end method
"""
    with open(main_activity_smali, "w") as f:
        f.write(content)
    print(f"[+] Added minimal MainActivity.smali to {smali_dir}")

def patch_apk(input_apk, output_apk, keystore=None, alias=None, keypass=None):
    # Check that output_apk is not a directory!
    if os.path.isdir(output_apk):
        print(f"[!] ERROR: Output path '{output_apk}' is a directory. Please provide a filename ending in .apk.")
        return
    with tempfile.TemporaryDirectory() as tmpdir:
        # 1. Decompile
        run([APKTOOL, "d", input_apk, "-o", os.path.join(tmpdir, "dec"), "-f"])
        decdir = os.path.join(tmpdir, "dec")
        # 2. Patch Manifest
        manifest = os.path.join(decdir, "AndroidManifest.xml")
        patch_manifest(manifest)
        # 3. Add MainActivity.smali
        smali_dir = os.path.join(decdir, "smali")
        add_main_activity(smali_dir)
        # 4. Rebuild
        rebuilt_apk = os.path.join(tmpdir, "rebuilt.apk")
        run([APKTOOL, "b", decdir, "-o", rebuilt_apk])
        # 5. Align
        aligned_apk = os.path.join(tmpdir, "aligned.apk")
        run([ZIPALIGN, "-p", "-f", "4", rebuilt_apk, aligned_apk])
        # 6. Sign
        if keystore and alias and keypass:
            run([APKSIGNER, "sign", "--ks", keystore, "--ks-key-alias", alias,
                 "--ks-pass", f"pass:{keypass}", "--out", output_apk, aligned_apk])
        else:
            # Try to sign with debug.keystore
            debug_keystore = os.path.expanduser("~/.android/debug.keystore")
            if os.path.exists(debug_keystore):
                run([APKSIGNER, "sign", "--ks", debug_keystore, "--ks-key-alias", "androiddebugkey",
                     "--ks-pass", "pass:android", "--key-pass", "pass:android",
                     "--out", output_apk, aligned_apk])
            else:
                shutil.copy(aligned_apk, output_apk)
                print("[!] APK not signed! Please sign manually.")
        print(f"[+] Patched APK ready: {output_apk}")
