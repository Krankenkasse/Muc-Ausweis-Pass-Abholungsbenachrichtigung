import time, sys, signal, requests, schedule, configparser

# Config
config = configparser.ConfigParser()
config.read('config.ini')


URL = "https://www17.muenchen.de/Passverfolgung/"
PAYLOAD = {
    "ifNummer": config.get('PassTracking', 'ifNummer'),
    "pbAbfragen": "Abfragen"
}


def check_website():
    response = requests.post(URL, data=PAYLOAD)
    if 'liegt zur<B STYLE="color: green"> Abholung bereit.' in response.text:
        send_telegram_message("Ihr Pass liegt zur Abholung bereit!")
    else:
        send_telegram_message("Noch kein Pass..")


def send_telegram_message(message):
    url = "https://api.telegram.org/bot" + config.get('Telegram', 'bot_token') + "/sendMessage"
    params = {
        'chat_id': config.get('Telegram', 'chat_id'),
        'text': message
    }

    try:
        response = requests.post(url, params=params)
        response.raise_for_status()
        print("Nachricht erfolgreich gesendet!")
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"Request Error: {err}")

def exit_gracefully(signum, frame):
    print("Program terminated. Sending notification...")
    send_telegram_message("Ausweis Py wurde beendet")
    sys.exit(0)


send_telegram_message("Startup Ausweis")

if __name__ == "__main__":
    signal.signal(signal.SIGINT, exit_gracefully)
    
    schedule.every().day.at("08:00").do(check_website)
    schedule.every().day.at("14:00").do(check_website)
    schedule.every().day.at("20:00").do(check_website)

    while True:
        schedule.run_pending()
        time.sleep(1)