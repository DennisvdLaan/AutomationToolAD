import subprocess
import os

def run(ad):
    domain = ad.domain
    username = ad.username.split("\\")[-1]
    password = ad.password
    dc_ip = ad.dc_ip
    script_dir = os.path.dirname(os.path.abspath(__file__))
    impacket_path = os.path.join(script_dir, "GetADUsers.py")
    command = [
        "python3",
        impacket_path,
        f"{domain}/{username}:{password}",
        "-dc-ip", dc_ip,
        "-all",
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        output = result.stdout
        return {"get_ad_users": output}
    except subprocess.CalledProcessError as e:
        return {"get_ad_users": f"Fout bij uitvoeren van GetADUsers.py: {e.stderr}"}
