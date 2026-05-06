from flask import Flask, render_template, request, jsonify
import time
import hashlib
import os

# CONFIGURAZIONE PERCORSI (Questa parte risolve l'errore 500)
base_dir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(base_dir, 'templates')

app = Flask(__name__, template_folder=template_dir)
app.secret_key = "vault_ultra_secret_2026"

def get_totp_code():
    # Codice dinamico ogni 180 secondi
    interval = int(time.time() / 180)
    seed = "mio-progetto-segreto-2026"
    return hashlib.sha256(f"{seed}-{interval}".encode()).hexdigest()[:6].upper()

@app.route('/')
def index():
    # Questo apparirà nei LOGS di Render
    print(f"--- LOG SICUREZZA --- Codice Attuale: {get_totp_code()}")
    try:
        return render_template('index.html')
    except Exception as e:
        return f"Errore caricamento template: {str(e)}", 500

@app.route('/api/verify', methods=['POST'])
def verify():
    data = request.json
    if data.get('code') == get_totp_code():
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Codice Errato"}), 401

if __name__ == '__main__':
    # Render usa la porta 10000 di default
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
