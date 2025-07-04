# main.py

import argparse
import yaml
import os
import sys
from main.logger import setup_logger
from main.ad_connector import ADConnector
from main.task_manager import TaskManager
from main.powershell_executor import run_powershell_script
from scans.enum import users
#from utils.helpers import save_report

# ───────────────────────────────────────────────────────────────────────────────
def load_config():
    try:
        with open("config/settings.yaml", "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print("❌ Configuratiebestand niet gevonden: config/settings.yaml")
        sys.exit(1)

# ───────────────────────────────────────────────────────────────────────────────
def parse_args():
    parser = argparse.ArgumentParser(description="AD Pentest Automation Tool")
    parser.add_argument("--mode", choices=["enum", "vuln", "exploit", "full"], default="full", help="Welke tests wil je uitvoeren?")
    parser.add_argument("--output", default="reports/report.json", help="Pad naar output rapport")
    return parser.parse_args()

# ───────────────────────────────────────────────────────────────────────────────
def main():
    args = parse_args()
    config = load_config()
    logger = setup_logger("ad_pentest.log")
    logger.info("Programma gestart")

    # Initialiseer verbinding met Active Directory
    ad = ADConnector(config)
    if not ad.connect():
        logger.error("Kan geen verbinding maken met Active Directory")
        sys.exit(1)

    task_manager = TaskManager()
    results = {}

    # ─── MODULE SELECTIE ───────────────────────────────────────────────────────
    if args.mode in ["enum", "full"]:
        logger.info("Pentestinstellingen: " + args.mode)
#        results["domain_info"] = domain_info.run(ad)
        results["users"] = users.run(ad)
#        results["groups"] = groups.run(ad)

#    if args.mode in ["vuln", "full"]:
#        logger.info("🛡️ Start Kwetsbaarheidsanalyse")
#        results["kerberoast"] = kerberoast.run(ad)
#        results["asreproast"] = asreproast.run(ad)

#    if args.mode in ["exploit", "full"]:
#        logger.info("💣 Start Exploit-pogingen (alleen PoC)")
#        results["dc_sync"] = dc_sync.run(ad)

    # ─── RAPPORTAGE ───────────────────────────────────────────────────────────
    #logger.info("📝 Rapport wordt gegenereerd")
 #   save_report(results, args.output)

    logger.info("Pentest voltooid.")
    ad.disconnect()

# ───────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
