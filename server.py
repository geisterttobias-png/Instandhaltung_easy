from flask import Flask, jsonify, request
import service

app = Flask(__name__)

# Beim Start einmal Demo-User anlegen
service.setup_demo_users()

# 1. LOGIN
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = service.login_check(data.get('username'), data.get('password'))
    if user:
        return jsonify(user), 200
    return jsonify({"error": "Falsche Daten"}), 401

# 2. MASCHINEN (Mit Filter)
@app.route('/maschinen', methods=['GET', 'POST'])
def handle_maschinen():
    if request.method == 'POST':
        d = request.json
        service.maschine_erstellen(d['name'], d['standort'], d['bereich'])
        return jsonify({"msg": "OK"}), 201
    
    else:
        # Filter aus URL lesen: /maschinen?bereich=P400
        bereich = request.args.get('bereich')
        lst = service.alle_maschinen_holen(bereich)
        # Umwandeln in JSON
        return jsonify([{"id": m.id, "name": m.name, "bereich": m.bereich, "status": m.status} for m in lst])

# 3. TICKETS
@app.route('/tickets', methods=['POST'])
def create_ticket():
    d = request.json
    # Hier kommt jetzt die melder_id dazu!
    ok = service.ticket_erstellen(d['maschine_id'], d['melder_id'], d['problem'], d['prio'])
    return jsonify({"success": ok})

# NEU: Einzelnes Ticket holen
@app.route('/tickets/<int:id>', methods=['GET'])
def get_ticket_detail(id):
    t = service.ticket_details_holen(id)
    if t:
        return jsonify(t)
    return jsonify({"error": "Nicht gefunden"}), 404

# NEU: Ticket bearbeiten (Update)
@app.route('/tickets/<int:id>', methods=['PUT'])
def update_ticket(id):
    d = request.json
    # Wir erwarten Status und Lösung
    ok = service.ticket_bearbeiten(id, d['status'], d['loesung'])
    if ok:
        return jsonify({"success": True})
    return jsonify({"error": "Fehler beim Update"}), 500

# WICHTIG: Die Route für die Liste der Tickets einer Maschine muss bleiben:
@app.route('/maschinen/<int:id>/tickets', methods=['GET'])
def get_tickets_by_maschine(id):
    # Hier müssen wir service.tickets_holen_fuer_maschine(id) nutzen (aus Schritt vorher)
    # Falls du die Funktion nicht mehr hast, hier die Kurzform für service.py:
    # def tickets_holen_fuer_maschine(mid): session=Session(); res=session.query(Ticket).filter(Ticket.maschine_id==mid).all(); ... return res
    
    # Da wir Service Code oben nicht komplett wiederholt haben, check bitte kurz service.py
    # Hier die Logik für den Server Teil:
    session = service.Session()
    tickets = session.query(service.Ticket).filter(service.Ticket.maschine_id == id).all()
    ergebnis = [{"id": t.id, "beschreibung": t.beschreibung, "status": t.status, "erstellt": str(t.erstellt_am)} for t in tickets]
    session.close()
    return jsonify(ergebnis)

if __name__ == '__main__':
    app.run(debug=True, port=5000)