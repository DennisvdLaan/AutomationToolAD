import subprocess
import os
import logging

logger = logging.getLogger("ADLogger")

def run(ad):
    domain = ad.domain
    username = ad.username.split("\\")[-1]
    password = ad.password
    dc_ip = ad.dc_ip

    script_dir = os.path.dirname(os.path.abspath(__file__))
    impacket_path = os.path.join(script_dir, "GetADComputers.py")

    command = [
        "python3",
        impacket_path,
        f"{domain}/{username}:{password}",
        "-dc-ip", dc_ip
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        output = result.stdout
        logger.info("Computer enumeration succesvol uitgevoerd")

        computers_list = []

        for line in output.splitlines():
            if not line.strip() or line.startswith("Name"):
                continue
            parts = line.strip().split()
            if len(parts) < 4:
                continue
            comp_dict = {
                "Type": "Computer",
                "Name": parts[0],
                "OperatingSystem": parts[1],
                "LastLogon": parts[2],
                "Description": parts[3]
            }
            computers_list.append(comp_dict)

        return computers_list

    except subprocess.CalledProcessError as e:
        logger.error(f"Fout bij uitvoeren van GetADComputers.py: {e.stderr.strip()}")
        return []
