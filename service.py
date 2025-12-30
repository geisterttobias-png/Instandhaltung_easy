from sqlalchemy.orm import sessionmaker
from datenmodell import engine, Maschine, Ticket, User

Session = sessionmaker(bind=engine)

# --- USER MANAGEMENT ---
def setup_demo_users():
    """Erstellt Test-User, falls keine da sind"""
    session = Session()
    if not session.query(User).first():
        u1 = User(username="max", password="123", rolle="Operator")
        u2 = User(username="chef", password="123", rolle="Meister")
        session.add_all([u1, u2])
        session.commit()
        print("Demo-User erstellt: max / 123")
    session.close()

def login_check(username, password):
    session = Session()
    user = session.query(User).filter(User.username == username, User.password == password).first()
    session.close()
    if user:
        return {"id": user.id, "name": user.username, "rolle": user.rolle}
    return None

# --- MASCHINEN ---
def alle_maschinen_holen(filter_bereich=None):
    session = Session()
    query = session.query(Maschine)
    
    if filter_bereich and filter_bereich != "Alle":
        query = query.filter(Maschine.bereich == filter_bereich)
        
    maschinen = query.all()
    session.close()
    return maschinen

def maschine_erstellen(name, standort, bereich):
    session = Session()
    try:
        # Hier vereinfacht ohne Duplikat-Check für Kürze
        m = Maschine(name=name, standort=standort, bereich=bereich)
        session.add(m)
        session.commit()
        return True
    except:
        return False
    finally:
        session.close()

# --- TICKETS ---
def ticket_erstellen(maschine_id, melder_id, beschreibung, prio):
    session = Session()
    try:
        m = session.query(Maschine).get(maschine_id)
        if m:
            t = Ticket(maschine_id=maschine_id, melder_id=melder_id, beschreibung=beschreibung, prio=prio)
            m.status = "STÖRUNG" # Automatisch rot setzen
            session.add(t)
            session.commit()
            return True
        return False
    except Exception as e:
        print(e)
        return False
    finally:
        session.close()

# --- TICKETS UPDATE ---
def ticket_bearbeiten(ticket_id, neuer_status, loesung_text):
    session = Session()
    try:
        t = session.query(Ticket).get(ticket_id)
        if t:
            t.status = neuer_status
            t.loesung = loesung_text
            
            # Logik: Wenn Ticket FERTIG, prüfe ob Maschine wieder OK sein soll
            # (Wir machen es hier einfach: Wenn fertig, Maschine OK)
            if neuer_status == "FERTIG":
                t.maschine.status = "OK"
            
            session.commit()
            return True
        return False
    except Exception as e:
        print(e)
        return False
    finally:
        session.close()

# WICHTIG: Die Funktion ticket_erstellen muss auch noch da sein (siehe vorheriger Schritt)
# Die Funktion tickets_holen_fuer_maschine muss auch da sein.
# Und neu: Ein einzelnes Ticket laden
def ticket_details_holen(ticket_id):
    session = Session()
    t = session.query(Ticket).get(ticket_id)
    # Wir müssen die Daten extrahieren, bevor wir die Session schließen
    if t:
        data = {
            "id": t.id,
            "beschreibung": t.beschreibung,
            "prio": t.prio,
            "status": t.status,
            "loesung": t.loesung,
            "melder": t.melder.username if t.melder else "Unbekannt",
            "erstellt_am": str(t.erstellt_am),
            "maschine_name": t.maschine.name
        }
        session.close()
        return data
    session.close()
    return None