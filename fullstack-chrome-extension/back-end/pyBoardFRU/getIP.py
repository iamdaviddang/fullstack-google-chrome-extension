import argparse
import requests
from bs4 import BeautifulSoup
import pyperclip
import logging
import os

logging.basicConfig(filename='LOGs/LOG-getIP.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_data(usn):
    """
    Get data from SFCS by USN
    """
    base_url = "http://172.25.32.4/dev/api/v2/fru-tool/"
    url = f"{base_url}{usn}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Chyba pri volani API: {e}")
        return None

def find_ip_for_mac(formatted_mac):
    """
    Find iRMC IP in DHCP by MAC
    """
    url = "http://172.25.32.1/catalyst/kea/ipv4leases"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        table = soup.find('table')

        for row in table.find_all('tr')[1:]:
            columns = row.find_all('td')
            
            if len(columns) >= 3:
                mac_address = columns[1].text.strip().upper().replace(":", "")
                ip_address = columns[2].text.strip()
                
                if mac_address == formatted_mac:
                    return ip_address
    return None



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="USN")
    parser.add_argument('USN', type=str, help="USN")
    args = parser.parse_args()
    
    if not args.USN.startswith(("EWCC", "EWCE", "EWCD", "EWCP", "EWCM", "EWCR", "EWCQ", "EWCT", "EWCS")):
        print("\n############################")
        print("This model is not supported.\nSupported models are:\n-RX2540M7 (EWCE...)\n-RX2530M7 (EWCD,EWCP...)\n-TX2550M7 (EWCC...)\n-RX1440M2 (EWCM...)\n-all MM6(EWCR, EWCQ, EWCT, EWCS)")
        print("############################")
        os._exit(0)
    
    sfcs_data = load_data(args.USN)
    
    if sfcs_data["status"] != "ok":
        logging.error(f"Failed to get data for USN: {args.USN} from SFCS.")
        print("\n########################################################################")
        print(f"Failed to get data for USN: {args.USN} from SFCS! Please double check the USN")
        print("########################################################################")
        os._exit(0)
    
    if sfcs_data:
        irmc_ip = find_ip_for_mac(sfcs_data["data"]["irmc_mac"])
        if irmc_ip:
            logging.info(f"iRMC IP for {args.USN} is: {irmc_ip}")
            print(f"iRMC IP for {args.USN} is: {irmc_ip}")
            pyperclip.copy(irmc_ip)
            print("IP has been found and copied to your clipboard")
        else:
            logging.warning(f"No IP found for the given MAC address.")
            print("No IP found for the given MAC address.")
    else:
        logging.error(f"Failed to load data for USN: {args.USN}")
        print(f"Failed to load data for USN: {args.USN}")
