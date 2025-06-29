# AndroidRAT Builder

**AndroidRAT Builder** is an educational tool for generating, patching, and managing Android Meterpreter payloads, with extended compatibility for Android 15. This project allows you to easily create, patch (add a visible UI for modern Android versions), sign, and deploy Android Meterpreter APK payloads, as well as launch a Metasploit handler — all from a simple Python command-line menu.

---

## ⚠️ Disclaimer

**This tool is provided for educational and research purposes only.**
- Do **not** use this tool on devices you do not own or have explicit permission to test.
- The authors take no responsibility for misuse or any consequences thereof.
- Always comply with your local laws and regulations.

---

## What is this?

- **AndroidRAT Builder** simplifies the process of generating Android Meterpreter payloads, patching them for compatibility with the latest Android versions (including Android 15), and signing them for installation.
- It provides an interactive menu to guide you through building, patching, signing, and deploying payloads, as well as starting a Metasploit handler to receive connections.

---

## Features

- **Build Android Meterpreter APKs** via msfvenom.
- **Patch APKs** to add a visible UI (Activity) for compatibility with Android 12, 13, 14, and 15 — enabling webcam, screenshot, and more.
- **Sign APKs** for installation on Android devices.
- **Start a Metasploit multi/handler** with your chosen payload options.
- **Works with Android 15** and tested on modern devices.
- **Simple CLI menu** for all actions.

---

## Requirements

- Python 3
- apktool
- zipalign
- apksigner
- msfvenom
- Metasploit Framework
- Linux recommended (tested on Debian 12)

### Signing Keys

A folder named `.android` **must exist in the root of your project** (or in your home directory as `~/.android`) containing the debug keystore file (`debug.keystore`) so APK signing works out-of-the-box.

If you don't have one, you can generate it using:
```bash
keytool -genkey -v -keystore ~/.android/debug.keystore -storepass android -alias androiddebugkey -keypass android -keyalg RSA -keysize 2048 -validity 10000
```

---

## How to use

1. **Clone this repository**
    ```bash
    git clone https://github.com/sa-fw-an/Android-RAT.git
    cd Android-RAT
    ```

2. **Make sure dependencies are installed and in your PATH.**

3. **Ensure the `.android` directory exists in your project root (or your home directory) with the debug keystore inside.**

4. **Start the tool**
    ```bash
    python3 cli.py
    ```

5. **Follow the on-screen menu:**
    ```
    ==============================
       AndroidRAT Main Menu
    ==============================
    [1] Build Android Payload (APK)
    [2] Start Metasploit Listener
    [3] Sign APK
    [4] Patch APK for Visible UI
    [5] Show Help & Exit
    ```

---

## Menu Options Explained

- **Build Android Payload (APK):**
    - Creates a Meterpreter APK using msfvenom with your provided LHOST and LPORT.
- **Start Metasploit Listener:**
    - Launches a Metasploit multi/handler set to catch your reverse shell connection.
- **Sign APK:**
    - Signs an APK using the debug keystore so it can be installed on Android devices.
- **Patch APK for Visible UI:**
    - Rebuilds a Meterpreter APK to include a visible Activity, required for Android 12/13/14/15 features like webcam and screenshots to work.
    - This is what makes the APK compatible with Android 15.
- **Show Help & Exit:**
    - Displays help and exits the tool.

---

## Android 15 Compatibility

- **AndroidRAT Builder** includes a patcher that adds a visible user interface (Activity) to Meterpreter payloads.
- This is essential for Android 12+ (including Android 15) due to permission and background execution restrictions.
- After patching, install the APK on the device, open it, grant all requested permissions (Camera, Microphone, Storage, etc.), and keep it in the foreground to use advanced Meterpreter features (webcam, screenshot, etc).

---

## Educational Purpose Only

This tool is intended **solely for educational and authorized testing**. Unauthorized use against devices without permission is illegal.

---

## Authors

- [Safwan Sayeed](https://safwansayeed.live/)
- Based on community research and open-source tools.

---

## License

[MIT](./LICENSE)
