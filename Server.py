from flask import Flask, render_template, request, jsonify, session
import time
import hashlib
import os

# Forza Flask a cercare la cartella templates nel percorso corretto
template_dir = os.path.abspath('templates')
app = Flask(__name__, template_folder=template_dir)

def get_totp_code():
    # Finestra di 180 secondi
    interval = int(time.time() / 180)
    # Cambia 'il-tuo-seed-segreto' con una parola a tua scelta per cambiare i codici
    seed = "mio-progetto-segreto-2026"
    return hashlib.sha256(f"{seed}-{interval}".encode()).hexdigest()[:6].upper()

@app.route('/')
def index():
    # Stampiamo il codice nei log così lo puoi leggere su Render
    print(f"--- LOG SICUREZZA --- Codice Attuale: {get_totp_code()}")
    return render_template('index.html')

@app.route('/api/verify', methods=['POST'])
def verify():
    data = request.json
    if data.get('code') == get_totp_code():
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Codice Errato"}), 401

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
