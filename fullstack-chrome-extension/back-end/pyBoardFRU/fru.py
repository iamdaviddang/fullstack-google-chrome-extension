import argparse
import os
import shutil
import subprocess
import requests
from bs4 import BeautifulSoup
import socket
import logging
import time
import pyperclip


logging.basicConfig(filename='LOGs/LOG-FRU-rewrite.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_data(usn):
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

def rewrite_serial_number(motherboard_sn, model):
    file_path = f'models/{model}/idp.INI'
    with open(file_path, 'r') as file:
        file_content = file.readlines()
        
    new_content = []
    
    for line in file_content:
        if line.strip().startswith("BoardSerialNumber"):
            line = f'    BoardSerialNumber=S,"{motherboard_sn.upper()}"\n'
        new_content.append(line)
        
    with open(file_path, 'w') as file:
        file.writelines(new_content)
    logging.info(" Motherboard SN has been successfully written to idp.INI")
    print("\n✓ Motherboard SN has been successfully written to idp.INI\n")

def delete_current_idp():
    try:
        os.remove('idp.INI')
    except FileNotFoundError:
        pass

def move_file(model):
    src_file = f"models/{model}/idp.INI"
    shutil.copy(src_file, os.path.join(os.getcwd(), "idp.INI"))

def reformat_file():
    subprocess.run("IPMI_FRU64.exe -ini2bin=idp.ini")
    logging.info(" Reformat idp.INI to idp.BIN done")
    print("\n✓ reformat idp.INI to idp.BIN done\n")

def upload_fru_to_unit(ip,usn):
    try:
        try:
            password = "admin"
            fru_send_command = subprocess.run(f"IPMIVIEW64.exe -host={ip} -ini=WRFRU.INI -usr=admin -pwd={password}", shell=True, check=True)
            if fru_send_command.returncode != 0:
                logging.info("Failed to upload FRU with password: admin!")
            logging.info(f"MB FRU for {usn} has been uploaded successfully. iRMC Password={password}")
            print("\n################################################################")
            print(f"Done! MB FRU for {usn} has been uploaded")
            print("################################################################\n")
        except:
            logging.error("Failed to upload FRU with password: admin")
            logging.warning("Trying to upload FRU with password: Password@123")
            password = "Password@123"
            fru_send_command = subprocess.run(f"IPMIVIEW64.exe -host={ip} -ini=WRFRU.INI -usr=admin -pwd={password}", shell=True, check=True)
            if fru_send_command.returncode == 0:
                logging.info(f"MB FRU for {usn} has been uploaded successfully with iRMC Password: {password}")
            print("\n################################################################")
            print(f"Done! MB FRU for {usn} has been uploaded")
            print("################################################################\n")
        
        if fru_send_command.returncode == 0:
            reboot_irmc(ip, password)

    except subprocess.CalledProcessError:
        logging.error(f"Failed to upload MB FRU into the unit {usn} with iRMC IP: {ip}")
        print("\n################################################################")
        print(f"Failed to upload MB FRU into the unit {usn} with iRMC IP: {ip}")
        print("################################################################")

def reboot_irmc(ip, password):
    try:
        socket.gethostbyname(ip)
        url = f"https://{ip}/redfish/v1/Managers/iRMC/Actions/Manager.Reset"
        auth = ('admin', password)
        requests.post(url, auth=auth, verify=False)
        logging.info("iRMC restarts. Wait until it reboots and check the MB SN")
        pyperclip.copy(ip)
        print("\n################################################################")
        print("iRMC restarts. Wait until it reboots and check the MB SN \niRMC IP has been copied automatically to your clipboard so you can check it.. :)")
        print("################################################################")
        logging.info("END")
        
    except socket.error:
        logging.error(f"IP address {ip} is not available")
        print(f"IP address {ip} is not available")


def is_server_available(host):
    try:
        port = 80
        socket.create_connection((host, port))
        return True
    except OSError:
        return False
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add arguments to write FRU")
    parser.add_argument('USN', type=str, help="USN")
    args = parser.parse_args()
    
    logging.info(f"START - USN: {args.USN}")
    if not args.USN.startswith(("EWCC", "EWCE", "EWCD")):
        logging.error("Unsupported model specified.")
        print("\n############################")
        print("This model is not supported.\nSupported models are:\n-RX2540M7 (EWCE...)\n-RX2530M7 (EWCD...)\n-TX2550M7 (EWCC...)")
        print("############################")
        os._exit(0)
        
    sfcs_data = load_data(args.USN)
    
    if sfcs_data["status"] != "ok":
        logging.error(f"Failed to get data for USN: {args.USN} from SFCS.")
        print("\n########################################################################")
        print(f"Failed to get data for USN: {args.USN} from SFCS! Please double check the USN")
        print("########################################################################")
        os._exit(0)
        
    print(f"\n✓ Motherboard SN has been found in SFCS - {sfcs_data["data"]["mobo_sn"]}")
    logging.info(f" Motherboard SN has been found in SFCS - {sfcs_data["data"]["mobo_sn"]}")
    rewrite_serial_number(sfcs_data["data"]["mobo_sn"], sfcs_data["data"]["model"])
    delete_current_idp()
    move_file(sfcs_data["data"]["model"])
    reformat_file()
    
    if is_server_available(find_ip_for_mac(sfcs_data["data"]["irmc_mac"])):
        upload_fru_to_unit(find_ip_for_mac(sfcs_data["data"]["irmc_mac"]), args.USN)
    else:
        numberOfAttempts = 1
        maxAttempts = 15
        while True:
            if numberOfAttempts <= maxAttempts:
                if is_server_available(find_ip_for_mac(sfcs_data["data"]["irmc_mac"])):
                    print("iRMC connection is available. Waiting 30 second more to let iRMC fully boot up")
                    logging.warning("iRMC connection is available. Waiting 30 second more to let iRMC fully boot up")
                    print("BEFORE SLEEP 30s")
                    time.sleep(30)
                    print("AFTER SLEEP 30s")
                    upload_fru_to_unit(find_ip_for_mac(sfcs_data["data"]["irmc_mac"]), args.USN)
                    break
                else:
                    print((f"iRMC IP not available yet, FRU will try to send again in 15 seconds...(Attempt#{numberOfAttempts}/{maxAttempts})"))
                    logging.error((f"iRMC IP not available yet, FRU will try to send again in 15 seconds...(Attempt#{numberOfAttempts}/{maxAttempts})"))
                    time.sleep(15)
                numberOfAttempts += 1
            else:
                print(f"Number of attempts is bigger than {maxAttempts} and iRMC IP is not still available. Please check iRMC again")
                logging.error(f"Number of attempts is bigger than {maxAttempts} and iRMC IP is not still available. Please check iRMC again")
                logging.info("END")
                break
