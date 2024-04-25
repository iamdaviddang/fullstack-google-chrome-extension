import requests
from requests.auth import HTTPBasicAuth


server_ip = "172.25.161.244"
username = "admin"

default_hesla = [
    "admin",
    "Password@123",
    "Admin-lzH5p5POBYkJ",
    "Admin-SguvlCskXm3L",
    "Admin-6FLdkraSUuTi",
    "adminADMIN11"
]

url = f"https://{server_ip}/redfish/v1/Managers/iRMC/Actions/iRMC.ResetPassword"

for default_heslo in default_hesla:
    nove_heslo = "adminADMIN111"

    data = {
        "Password": nove_heslo
    }
    
    response = requests.post(url, json=data, auth=HTTPBasicAuth(username, default_heslo), verify=False)
    print(response)

    if response.status_code == 200:
        print("Nové heslo pro iRMC bylo úspěšně nastaveno.")
        print("Použité výchozí heslo:", default_heslo)
        break
    else:
        print("Pokus o změnu hesla s výchozím heslem", default_heslo, "selhal.")
