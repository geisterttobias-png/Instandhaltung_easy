import requests
import json

# Die Adresse unseres Servers (wo server.py läuft)
SERVER_URL = "http://127.0.0.1:5000"

# Wir simulieren den Prozess
if __name__ == "__main__":
    # 1. Maschine anlegen
    requests.post(f"{SERVER_URL}/maschinen", json={"name": "Presse X", "standort": "Halle 1"})
    
    # 2. Wir holen uns die Liste, um die ID der neuen Maschine zu finden
    resp = requests.get(f"{SERVER_URL}/maschinen").json()
    presse_id = resp[0]['id'] # Wir nehmen einfach die erste Maschine
    print(f"Maschine ID ist: {presse_id}")
    
    # 3. TICKET ERSTELLEN
    print("--- Erstelle Ticket ---")
    ticket_daten = {
        "maschine_id": presse_id,
        "problem": "Hydraulik leckt",
        "prio": "HOCH"
    }
    requests.post(f"{SERVER_URL}/tickets", json=ticket_daten)
    
    # 4. PRÜFEN: Hat sich der Maschinen-Status geändert?
    # In service.py haben wir gesagt: Ticket neu -> Maschine STÖRUNG.
    check = requests.get(f"{SERVER_URL}/maschinen").json()
    print(f"Status der Maschine ist jetzt: {check[0]['status']}")