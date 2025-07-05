import argparse
import yaml
import os
import sys
from datetime import datetime
from main.logger import setup_logger
from main.ad_connector import ADConnector
from scans.enum import users, computers, userspns
from utils.helpers import save_report, save_dict_list_to_csv

def load_config():
    try:
        with open("config/settings.yaml", "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print("Configuratiebestand niet gevonden: config/settings.yaml")
        sys.exit(1)

def parse_args():
    parser = argparse.ArgumentParser(description="AD Pentest Automation Tool")
    parser.add_argument("--mode", choices=["enum", "vuln", "exploit", "full"], default="full", help="Welke tests wil je uitvoeren?")
    return parser.parse_args()

def main():
    args = parse_args()
    config = load_config()
    logger = setup_logger("ad_pentest.log")
    logger.info("Programma gestart")

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = os.path.join("reports", f"Result_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)

    ad = ADConnector(config)
    if not ad.connect():
        logger.error("Kan geen verbinding maken met Active Directory")
        sys.exit(1)

    results = {}

    logger.info(f"Gekozen modus: {args.mode}")

    if args.mode in ["enum", "full"]:
        logger.info("Start Enumeration Module")

        users_results = users.run(ad)
        results["users"] = users_results
#        logger.info(f"Users results: {users_results}") # Debug messages

        computers_results = computers.run(ad)
        results["computers"] = computers_results
#        logger.info(f"Computers results: {computers_results}") # Debug messages

        userspns_results = userspns.run(ad)
        results["userspns"] = userspns_results
#        logger.info(f"UserSPNs results: {userspns_results}") # Debug message
        save_dict_list_to_csv(users_results, os.path.join(output_dir, "users.csv"))

        if computers_results and isinstance(computers_results, list) and len(computers_results) > 0:
            save_dict_list_to_csv(computers_results, os.path.join(output_dir, "computers.csv"))

        if userspns_results and isinstance(userspns_results, list) and len(userspns_results) > 0:
            save_dict_list_to_csv(userspns_results, os.path.join(output_dir, "userspns.csv"))

    if args.mode in ["vuln", "full"]:
        logger.info("Start Kwetsbaarheidsanalyse")

    if args.mode in ["exploit", "full"]:
        logger.info("Start Exploit-pogingen")

    if results:
        json_report_path = os.path.join(output_dir, "report.json")
        save_report(results, json_report_path)
        logger.info(f"Rapport opgeslagen: {json_report_path}")
    else:
        logger.warning("Geen resultaten om op te slaan")
    os_version = ad.get_os_version()
    logger.info(f"Gevonden OS-versies: {os_version}")
    logger.info("Pentest voltooid")
    ad.disconnect()

if __name__ == "__main__":
    main()
