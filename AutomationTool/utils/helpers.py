import json
import csv
import logging

logger = logging.getLogger("ADLogger")

def save_report(results, output_path):
    """
    Sla het volledige rapport op als JSON
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4)
        logger.info(f"Report saved: {output_path}")
    except Exception as e:
        logger.error(f"Error saving report: {str(e)}")

def save_csv(headers, rows, output_path):
    """
    Sla resultaten op in CSV formaat
    """
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        logger.info(f"CSV saved successfully: {output_path}")
    except Exception as e:
        logger.error(f"Error saving CSV: {str(e)}")

def save_dict_list_to_csv(dict_list, output_path):
    """
    Sla een lijst van dictionaries op als CSV bestand.
    Headers komen uit de keys van de eerste dict.
    """
    if not dict_list:
        logger.warning("No dictionaries found, No CSV Saved")
        return
    
    headers = list(dict_list[0].keys())
    rows = [[item.get(h, "") for h in headers] for item in dict_list]

    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        logger.info(f"CSV saved successfully: {output_path}")
    except Exception as e:
        logger.error(f"Error saving CSV: {str(e)}")
