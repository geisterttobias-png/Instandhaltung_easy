# Verbndung und Bauplan aus datenmodell
from datenmodell import engine, Maschine
from sqlalchemy.orm import sessionmaker

# 1. Die Session starten (Fenster öffnen)
# Wir binden die Session an unsere Datenbank

Session = sessionmaker(bind=engine)
session = Session()

print("--- START: Daten einfügen ---")

# 2. Objekte erstellen (Pthon Klassen)
presse = Maschine(name="Hydraulikpresse A", standort="Halle 3",
                  bereich="P", status="OK")
roboter = Maschine(name="Schweißroboter B", standort="Halle 1", bereich="P",
                   status="Wartung")

# 3. In den Einkaufswagen legen
session.add(presse)
session.add(roboter)

# 4. Abschließen = Commit zu DB
session.commit
print("-> 2 Maschinen wurden gespeichert.")


print("\n--- START: Daten auslesen ---")

# 5. Abfrage Query
# Überstezt "Gib mir alle Daten vom Typ Maschine
alle_maschinen = session.query(Maschine).all()

for m in alle_maschinen:
    print(f"ID: {m.id} | Name: {m.name} | Bereich: {m.bereich} | Status: {m.status}")

# 6. Filtern (Wo in SQL)
print("\n--- Suche Maschinen in Wartung ---")
kaputte_maschinen = session.query(Maschine).filter(Maschine.status ==
                                                   "Wartung").all()
for m in kaputte_maschinen:
    print(f"Achtung: {m.name} ist in Wartung")
