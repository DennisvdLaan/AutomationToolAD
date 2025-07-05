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
    impacket_path = os.path.join(script_dir, "GetADUsers.py")

    command = [
        "python3",
        impacket_path,
        f"{domain}/{username}:{password}",
        "-dc-ip", dc_ip,
        "-all"
    ]

    try:
        # subprocess run zonder dat output naar terminal gaat
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        output = result.stdout
        logger.info("User Enumeration Completed")

        users_list = []

        for line in output.splitlines():
            if not line.strip() or line.startswith("Name"):
                continue
            parts = line.strip().split()
            if len(parts) < 4:
                continue
            user_dict = {
                "Type": "User",
                "Name": parts[0],
                "Email": parts[1],
                "PasswordLastSet": parts[2],
                "LastLogon": parts[3]
            }
            users_list.append(user_dict)

        return users_list

    except subprocess.CalledProcessError as e:
        logger.error(f"Error executing GetADUsers.py: {e.stderr.strip()}")
        return []
