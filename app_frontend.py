import streamlit as st
import requests

API_URL = "http://127.0.0.1:5000"

st.set_page_config(page_title="Instandhaltung Pro", layout="wide")

# --- STATE MANAGEMENT ---
# Wir steuern die "Seiten" über den Session State
if 'current_view' not in st.session_state:
    st.session_state['current_view'] = 'dashboard' # Startseite

# --- AUTHENTIFIZIERUNG ---
def login():
    u = st.session_state.username_input
    p = st.session_state.password_input
    try:
        r = requests.post(f"{API_URL}/login", json={"username": u, "password": p})
        if r.status_code == 200:
            st.session_state['user'] = r.json()
            st.rerun()
        else:
            st.error("Login fehlgeschlagen")
    except:
        st.error("Server down")

def logout():
    st.session_state.clear()
    st.rerun()

# --- NAVIGATION FUNKTIONEN ---
def go_to_history(maschine):
    st.session_state['selected_machine'] = maschine
    st.session_state['current_view'] = 'history'
    # Hack: Rerun damit die Seite sofort umschaltet
    
def go_to_ticket(ticket_id):
    st.session_state['selected_ticket_id'] = ticket_id
    st.session_state['current_view'] = 'ticket_edit'

def go_back_dashboard():
    st.session_state['current_view'] = 'dashboard'
    if 'selected_ticket_id' in st.session_state: del st.session_state['selected_ticket_id']

# --- LOGIN SCREEN ---
if 'user' not in st.session_state:
    st.title("🔐 Login")
    st.text_input("User", key="username_input")
    st.text_input("Pass", type="password", key="password_input")
    st.button("Login", on_click=login)
    st.stop() # Hier stoppt das Skript, wenn nicht eingeloggt

# --- APP START ---
user = st.session_state['user']

# Sidebar immer sichtbar
with st.sidebar:
    st.write(f"👤 **{user['name']}** ({user['rolle']})")
    if st.button("🏠 Dashboard"):
        go_back_dashboard()
        st.rerun()
    if st.button("Abmelden"):
        logout()

# --- ANSICHT 1: DASHBOARD (Maschinen Übersicht) ---
if st.session_state['current_view'] == 'dashboard':
    st.title("Übersicht: Anlagen")
    
    # Neue Anlage Button
    with st.expander("Neue Anlage anlegen"):
        n_name = st.text_input("Name")
        n_ber = st.selectbox("Bereich", ["P400", "Montage"])
        if st.button("Speichern"):
            requests.post(f"{API_URL}/maschinen", json={"name": n_name, "standort": "Werk 1", "bereich": n_ber})
            st.rerun()
            
    # Maschinen Liste laden
    try:
        maschinen = requests.get(f"{API_URL}/maschinen").json()
        cols = st.columns(3)
        for idx, m in enumerate(maschinen):
            with cols[idx % 3]:
                with st.container(border=True):
                    color = "red" if m['status'] == "STÖRUNG" else "green"
                    st.markdown(f"### :{color}[{m['name']}]")
                    st.write(f"Status: **{m['status']}**")
                    
                    c1, c2 = st.columns(2)
                    # Button 1: Störung melden (Modal)
                    if c1.button("⚠️ Melden", key=f"btn_rep_{m['id']}"):
                        st.session_state['report_machine'] = m
                        st.rerun()
                    
                    # Button 2: Historie ansehen (Navigation)
                    if c2.button("📂 Historie", key=f"btn_hist_{m['id']}"):
                        go_to_history(m)
                        st.rerun()
                        
    except Exception as e:
        st.error(f"Fehler: {e}")

    # Modal: Störung melden (Overlay)
    if 'report_machine' in st.session_state:
        m = st.session_state['report_machine']
        with st.form("new_ticket"):
            st.write(f"### Störung: {m['name']}")
            prob = st.text_area("Problem")
            prio = st.select_slider("Prio", ["Niedrig", "Mittel", "HOCH"])
            if st.form_submit_button("Senden"):
                requests.post(f"{API_URL}/tickets", json={
                    "maschine_id": m['id'], "melder_id": user['id'], "problem": prob, "prio": prio
                })
                del st.session_state['report_machine']
                st.rerun()

# --- ANSICHT 2: HISTORIE (Ticket Liste) ---
elif st.session_state['current_view'] == 'history':
    m = st.session_state['selected_machine']
    st.title(f"📂 Tickets für: {m['name']}")
    
    tickets = requests.get(f"{API_URL}/maschinen/{m['id']}/tickets").json()
    
    if tickets:
        # Wir zeigen die Tickets als Tabelle oder Liste
        for t in tickets:
            with st.container(border=True):
                col1, col2, col3 = st.columns([1, 4, 1])
                col1.write(f"**#{t['id']}**")
                col2.write(f"{t['beschreibung']} ({t['status']})")
                if col3.button("Bearbeiten", key=f"edit_{t['id']}"):
                    go_to_ticket(t['id'])
                    st.rerun()
    else:
        st.info("Keine Tickets vorhanden.")

# --- ANSICHT 3: TICKET DETAILS & BEARBEITEN ---
elif st.session_state['current_view'] == 'ticket_edit':
    tid = st.session_state['selected_ticket_id']
    st.title(f"Ticket #{tid} bearbeiten")
    
    # Details laden
    t_data = requests.get(f"{API_URL}/tickets/{tid}").json()
    
    st.info(f"Anlage: {t_data['maschine_name']} | Gemeldet von: {t_data['melder']} | Am: {t_data['erstellt_am'][:16]}")
    st.write(f"**Fehler:** {t_data['beschreibung']}")
    
    st.divider()
    
    # Bearbeitungs-Formular
    with st.form("edit_ticket"):
        st.write("🔧 **Maßnahmen & Status**")
        
        # Aktuellen Status vorwählen
        options = ["NEU", "IN_ARBEIT", "WARTEN", "FERTIG"]
        current_index = 0
        if t_data['status'] in options:
            current_index = options.index(t_data['status'])
            
        new_status = st.selectbox("Neuer Status", options, index=current_index)
        
        # Lösungstext (vorherigen Inhalt anzeigen falls vorhanden)
        prev_loesung = t_data.get('loesung') if t_data.get('loesung') else ""
        new_loesung = st.text_area("Durchgeführte Arbeiten / Lösung", value=prev_loesung)
        
        if st.form_submit_button("Speichern"):
            # Update an API senden (PUT)
            requests.put(f"{API_URL}/tickets/{tid}", json={
                "status": new_status,
                "loesung": new_loesung
            })
            st.success("Gespeichert!")
            # Zurück zur Historie
            st.session_state['current_view'] = 'history'
            st.rerun()