import argparse
import requests
import os

# https://172.25.163.70/redfish/v1/Managers/iRMC/LogServices/SystemEventLog/Actions/LogService.ClearLog

def check_power_status(ip):
    
    pws = {
        "M2": "Password@123",
        "M5": "admin",
        "M7": "Password@123",
        "RX2530M6": "admin",
        "RX2540M6": "admin",
        "RX4770M6": "admin",
        "TX1310M6": "Password@123",
        "TX1320M6": "Password@123",
        "TX1330M6": "Password@123",
        "RX1310M6": "Password@123",
        "RX1320M6": "Password@123",
        "RX1330M6": "Password@123"
    }
    
    def get_password(model):
        return pws.get(model, "defaultni_heslo")
    
    url = f"https://{ip}/redfish/v1"
    auth = ('', '')
    response = requests.get(url, auth=auth, verify=False)
    data = response.json()["Oem"]["ts_fujitsu"]["AutoDiscoveryDescription"]["ServerNodeInformation"]["Model"]
    rada_serveru = data.split()[2]
    model = data.split()[1]+rada_serveru
    
    password = ""
    if rada_serveru == "M7" or rada_serveru == "M2":
        password = "Password@123"
    elif rada_serveru == "M5":
        password = "admin"
    else:
        password = get_password(model)
        
    # print(f"Model: {model}")
    # print(f"Rada: {rada_serveru}")
    # print(f"Heslo pro tento model: {password}")
    return password

def clearSEL(ip):
    url = f'http://{ip}/api/v2/irmc/clear-sel'
    auth = ('admin', check_power_status(ip))
    response = requests.post(url, auth=auth, verify=False)
    if response.status_code == 200:
        print("\n### SEL is cleared ###\n")
    else:
        print("\n### Clear SEL failed! ###\n")
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="iRMCIP")
    parser.add_argument('iRMCIP', type=str, help="iRMCIP")
    args = parser.parse_args()
    
    if args.iRMCIP.startswith("172.25."):
        clearSEL(args.iRMCIP)
    else:
        print("\n### Unknown input ###\n")
        os._exit(0)
