from flask import Flask, render_template, request, jsonify, session
import time
import hashlib
import os

app = Flask(__name__)
app.secret_key = "super_secret_vault_key_2026"

# Simulazione Database (in produzione usa SQLite come nel PDF precedente)
vault_storage = {
    "admin": {"posts": ["Benvenuto nel mio Vault privato."], "docs": ["cv_segreto.pdf"]}
}

def get_totp_code():
    # Genera codice unico ogni 180 secondi
    interval = int(time.time() / 180)
    return hashlib.sha256(f"secret-seed-{interval}".encode()).hexdigest()[:6].upper()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/verify', methods=['POST'])
def verify():
    code = request.json.get('code')
    if code == get_totp_code():
        return jsonify({"status": "success", "token": "access_granted_123"})
    return jsonify({"status": "error", "message": "Codice errato o scaduto"}), 401

@app.route('/api/data', methods=['GET'])
def get_data():
    # Restituisce i dati del vault
    return jsonify(vault_storage["admin"])

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)