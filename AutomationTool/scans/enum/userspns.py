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
    impacket_path = os.path.join(script_dir, "GetUserSPNs.py")

    command = [
        "python3",
        impacket_path,
        f"{domain}/{username}:{password}",
        "-dc-ip", dc_ip
    ]

    try:
        # subprocess run zonder dat output naar terminal gaat
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        output = result.stdout
        logger.info("SPNs enumeratie succesvol uitgevoerd")

        userspns_list = []

        for line in output.splitlines():
            if not line.strip() or line.startswith("Name"):
                continue
            parts = line.strip().split()
            if len(parts) < 4:
                continue
            userspns_dict = {
                "Type": "SPN",
                "ServicePrincipalName": parts[0],
                "Name": parts[1],
                "MemberOf": parts[2],
                "PasswordLastSet": parts[3]
            }
            userspns_list.append(userspns_dict)

        return userspns_list

    except subprocess.CalledProcessError as e:
        logger.error(f"Fout bij uitvoeren van GetUserSPNs.py: {e.stderr.strip()}")
        return []
