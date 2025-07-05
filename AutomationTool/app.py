import argparse
import yaml
import os
import sys
from datetime import datetime
from main.logger import setup_logger
from main.ad_connector import ADConnector
from scans.enum import users, computers, userspns
from utils.helpers import save_report, save_dict_list_to_csv
from scans.exploits.exploits import run_nopac_poc, run_printspool_poc
from main.exploit_manager import load_exploits, is_vulnerable

POC_FUNCTIONS = {
    "run_nopac_poc": run_nopac_poc,
    "run_printspool_poc": run_printspool_poc,
}

def run_exploits_if_vulnerable(ad_connector, os_versions, logger):
    exploits = load_exploits()
    for exploit in exploits:
        patterns = exploit.get("vulnerable_os_patterns", [])
        if is_vulnerable(os_versions, patterns):
            logger.info(f"Exploit {exploit['name']} Could be possible")
            poc_func_name = exploit.get("poc_function")
            poc_func = POC_FUNCTIONS.get(poc_func_name)
            if poc_func:
                poc_func(ad_connector)
            else:
                logger.warning(f"No file found for: {poc_func_name}")

def load_config():
    try:
        with open("config/settings.yaml", "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print("Configuration file not found: config/settings.yaml")
        sys.exit(1)

def parse_args():
    parser = argparse.ArgumentParser(description="AD Pentest Automation Tool")
    parser.add_argument("--mode", choices=["enum", "vuln", "exploit", "full"], default="full", help="Which tests do you want to perform?")
    return parser.parse_args()

def main():
    args = parse_args()
    config = load_config()
    logger = setup_logger("ad_pentest.log")
    logger.info("Started Program")

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = os.path.join("reports", f"Result_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)

    ad = ADConnector(config)
    if not ad.connect():
        logger.error("Cannot connect to Active Directory")
        sys.exit(1)

    results = {}

    logger.info(f"Tests chosen: {args.mode}")

    if args.mode in ["enum", "full"]:
        logger.info("Started Enumeration Module")

        users_results = users.run(ad)
        results["users"] = users_results

        computers_results = computers.run(ad)
        results["computers"] = computers_results

        userspns_results = userspns.run(ad)
        results["userspns"] = userspns_results

        save_dict_list_to_csv(users_results, os.path.join(output_dir, "users.csv"))

        if computers_results and isinstance(computers_results, list) and len(computers_results) > 0:
            save_dict_list_to_csv(computers_results, os.path.join(output_dir, "computers.csv"))

        if userspns_results and isinstance(userspns_results, list) and len(userspns_results) > 0:
            save_dict_list_to_csv(userspns_results, os.path.join(output_dir, "userspns.csv"))

    if args.mode in ["vuln", "full"]:
        logger.info("Started Vulnerability Checks")

    if args.mode in ["exploit", "full"]:
        logger.info("Started Exploit Checks")
        os_version_str = ad.get_os_version()
        logger.info(f"Found OS Version: {os_version_str}")
        os_versions = [v.strip() for v in os_version_str.split(",") if v.strip()]
        run_exploits_if_vulnerable(ad, os_versions, logger)

    if results:
        json_report_path = os.path.join(output_dir, "report.json")
        save_report(results, json_report_path)
        logger.info(f"Saved report: {json_report_path}")
    else:
        logger.warning("No results to save")

    logger.info("Test Completed")
    ad.disconnect()

if __name__ == "__main__":
    main()
