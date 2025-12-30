# Wir importieren nur unsere Service-Funktionen
import service

print("--- SYSTEM START ---")

# 1. Wir versuchen, Maschinen anzulegen
# Wenn du das Skript mehrmals ausführst, wird er beim zweiten Mal meckern (aber nicht abstürzen!)
service.maschine_erstellen("Hydraulikpresse A", "Halle 3")
service.maschine_erstellen("Schweißroboter B", "Halle 1")

# Versuch, ein Duplikat zu erstellen (Test der Sicherheit)
service.maschine_erstellen("Hydraulikpresse A", "Halle 99") 

# 2. Daten anzeigen
print("\n--- Aktueller Bestand ---")
liste = service.alle_maschinen_holen()
for m in liste:
    print(f"- {m.name} ({m.status})")

# 3. Daten ändern (Business Case: Störung melden)
# Wir nehmen an, die Presse (ID 1) geht kaputt
print("\n--- Simuliere Störung ---")
service.status_aendern(1, "STÖRUNG")

# 4. Kontrolle
print("\n--- Kontrolle nach Update ---")
liste_neu = service.alle_maschinen_holen()
for m in liste_neu:
    if m.id == 1:
        print(f"Status von {m.name} ist jetzt: {m.status}")
