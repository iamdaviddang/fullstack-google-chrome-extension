import argparse
import requests
import os

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
    
    url = f"https://{ip}/redfish/v1/Systems/0"
    auth = ('admin', password)
    response = requests.get(url, auth=auth, verify=False)
    power_status = response.json()['PowerState']
    # print(f"PowerStatus: {power_status}")

    return power_status, password


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="iRMCIP")
    parser.add_argument('iRMCIP', type=str, help="iRMCIP")
    args = parser.parse_args()
    
    if args.iRMCIP.startswith("172.25."):
        pass
    else:
        print("Unknown input")
        os._exit(0)
    
    pwr_status, password = check_power_status(args.iRMCIP)
    
    if pwr_status == "Off":
        print("\n### The unit is already switched off ###\n")
    elif pwr_status == "On":
        url = f'https://{args.iRMCIP}/redfish/v1/Systems/0/Actions/Oem/FTSComputerSystem.Reset'
        auth = ('admin', password)
        data = {"FTSResetType": "PowerOff"}
        response = requests.post(url, json=data, verify=False, auth=auth)
        print("\n### Turning off the unit.. ###\n")
    
    