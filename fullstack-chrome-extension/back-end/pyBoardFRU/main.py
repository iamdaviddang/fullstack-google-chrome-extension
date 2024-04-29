from flask import Flask, request, jsonify
from flask_cors import CORS
from functions import *
from markupsafe import escape
import json

app = Flask(__name__)
CORS(app)




@app.route('/api/fru', methods=['POST'])
def handle_fru_update():
    logging.basicConfig(filename='LOGs/LOG-FRU-rewrite.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    data = request.json
    usn = data.get('USN')
    logging.info(f"USN: {usn}")
    
    #zkontrolovani delky USN
    if len(usn) > 10:
        logging.error("USN length is not correct")
        return jsonify({'message': 'USN length is not correct'})
    
    # zkontrolovani USN
    if not usn.startswith(("EWCC", "EWCE", "EWCD", "EWCP")):
        logging.error('message - Unsupported model specified.')
        return jsonify({'message': 'Unsupported model specified.'})
    
    #nacteni dat z SFCS z endpointu + nahrani dat do promennych
    if load_data(usn) != None:
        sfcs_data = load_data(usn)
        unit_status = sfcs_data["status"]
        unit_mobo_sn = sfcs_data["data"]["mobo_sn"]
        unit_model = sfcs_data["data"]["model"]
        unit_irmc_ip = find_ip_for_mac(sfcs_data["data"]["irmc_mac"])
    else:
        logging.error('message - Failed to get data for your USN from SFCS')
        return jsonify({'message': 'Failed to get data for your USN from SFCS'})
    
    #zkontrolovani jestli nacteni dat z SFCS bylo uspesne
    if unit_status != "ok":
        logging.error('message - Failed to get data for your USN from SFCS, stauts is not OK')
        return jsonify({'message': 'Failed to get data for your USN from SFCS, stauts is not OK'})
    
    #Prepsani USN v souboru
    rewrite_serial_number(unit_mobo_sn, unit_model)
    
    #vymazani soucastneho souboru
    delete_current_idp()
    
    #presunitu prepsaneho noveho souboru do hlavniho adresare
    move_file(unit_model)
    
    #preformatovani souboru
    reformat_file()
    
    if is_server_available(unit_irmc_ip):
        upload_fru_to_unit(unit_irmc_ip, usn)
        logging.info(f'message - Done. Wait for the iRMC to reboot itself, USN: {usn}, IP: {unit_irmc_ip}')
        return jsonify({'message': 'Done. Wait for the iRMC to reboot itself','USN':usn, 'IP':unit_irmc_ip})
    else:
        numberOfAttempts = 1
        maxAttempts = 15
        while True:
            if numberOfAttempts <= maxAttempts:
                if is_server_available(unit_irmc_ip):
                    logging.warning("iRMC connection is available. Waiting 30 second more to let iRMC fully boot up")
                    print("iRMC connection is available. Waiting 30 second more to let iRMC fully boot up")
                    time.sleep(30)
                    upload_fru_to_unit(unit_irmc_ip, usn)
                    break
                else:
                    print((f"iRMC IP not available yet, FRU will try to send again in 15 seconds...(Attempt#{numberOfAttempts}/{maxAttempts})"))
                    logging.warning((f"iRMC IP not available yet, FRU will try to send again in 15 seconds...(Attempt#{numberOfAttempts}/{maxAttempts})"))
                    time.sleep(15)
                numberOfAttempts += 1
            else:
                print(f"Number of attempts is bigger than {maxAttempts} and iRMC IP is not still available. Please check iRMC again")
                logging.error(f"Number of attempts is bigger than {maxAttempts} and iRMC IP is not still available. Please check iRMC again")
                break
    logging.info('message - Done. Wait for the iRMC to reboot itself, USN :{usn}, IP:{unit_irmc_ip}')
    return jsonify({'message': 'Done. Wait for the iRMC to reboot itself','USN':usn, 'IP':unit_irmc_ip})


@app.route("/api/ipfinder/<usn>", methods=['GET'])
def ipfinder(usn):
    
    logging.info(f"USN: {usn}")
    
    #zkontrolovani delky USN
    if len(usn) > 10:
        logging.error("USN length is not correct")
        return jsonify({'message': 'USN length is not correct'})
    
    # zkontrolovani USN
    if not usn.startswith(("EWCC", "EWCE", "EWCD", "EWCP", "EWCM", "EWCR", "EWCQ", "EWCT", "EWCS", "EWCL")):
        logging.error('message - Unsupported model specified.')
        return jsonify({'message': 'Unsupported model specified.'})
    
    #nacteni dat z SFCS z endpointu + nahrani dat do promennych
    if load_data(usn) != None:
        sfcs_data = load_data(usn)
        unit_status = sfcs_data["status"]
        unit_mobo_sn = sfcs_data["data"]["mobo_sn"]
        unit_model = sfcs_data["data"]["model"]
        unit_irmc_ip = find_ip_for_mac(sfcs_data["data"]["irmc_mac"])
    else:
        logging.error('message - Failed to get data for your USN from SFCS')
        return jsonify({'message': 'Failed to get data for your USN from SFCS'})
    
    #zkontrolovani jestli nacteni dat z SFCS bylo uspesne
    if unit_status != "ok":
        logging.error('message - Failed to get data for your USN from SFCS, stauts is not OK')
        return jsonify({'message': 'Failed to get data for your USN from SFCS, stauts is not OK'})
    
    if sfcs_data:
        if unit_irmc_ip:
            logging.info(f"for USN: {usn} is iRMC-IP:{unit_irmc_ip}")
            return {"iRMCIP":unit_irmc_ip}
        else:
            logging.error("message - No IP found for the given MAC address.")
            return {"message":"No IP found for the given MAC address."}
    else:
        logging.error("message - Failed to load data for USN")
        return {"message":"Failed to load data for USN"}

@app.route("/api/upload-tasks/", methods=['GET'])
def uploadTasks():
    # Načtení JSON souboru
    with open('data.json') as f:
        data = json.load(f)

    # Vytvoření JSON objektu s daty
    response_data = {}
    for name, info in data.items():
        response_data[name] = {
            "USN": info["USN"],
            "position": info["position"],
        }

    return jsonify(response_data)


@app.route("/api/receive-data/", methods=['POST'])
def updateTasks():
    # Načtení JSON souboru
    with open('data.json') as f:
        data = json.load(f)

    # Získání dat z formuláře JSON
    name = request.json['name']
    usn = request.json['usn']
    position = request.json['position']

    # Aktualizace záznamu v JSON souboru
    if name in data:
        data[name]['USN'] = usn
        data[name]['position'] = position

        # Uložení aktualizovaných dat do JSON souboru
        with open('data.json', 'w') as f:
            json.dump(data, f, indent=4)

        return jsonify({'message': f"Data pro {name} byla aktualizována."})
    else:
        return jsonify({'error': f"Student s jménem {name} nebyl nalezen."})



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
