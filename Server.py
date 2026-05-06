from flask import Flask, request, jsonify
import time
import hashlib
import os

app = Flask(__name__)
app.secret_key = "vault_ultra_secret_2026"

# HTML INCORPORATO DIRETTAMENTE NEL CODICE
HTML_UI = """
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vault Pro | Identity</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary: #1a73e8;
            --primary-dark: #0d47a1;
            --accent: #a142f5;
            --bg: #f8fafd;
            --surface: #ffffff;
            --text-main: #1c1b1f;
            --text-sub: #49454f;
            --shadow-soft: 0 12px 40px rgba(0,0,0,0.08);
            --shadow-deep: 0 24px 68px rgba(0,0,0,0.12);
        }

        * { transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); box-sizing: border-box; }

        body {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background: radial-gradient(circle at top right, #eef2f7, var(--bg));
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            color: var(--text-main);
        }

        .app-card {
            width: 100%;
            max-width: 420px;
            background: var(--surface);
            border: 1px solid rgba(255,255,255,0.7);
            box-shadow: var(--shadow-deep);
            position: relative;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }

        /* Designer Header */
        .header {
            padding: 50px 30px;
            background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
            color: white;
            text-align: center;
            position: relative;
        }

        .header::after {
            content: '';
            position: absolute;
            bottom: -20px;
            left: 0;
            width: 100%;
            height: 40px;
            background: var(--surface);
            clip-path: polygon(0 50%, 100% 100%, 0% 100%);
        }

        .header h1 { font-weight: 800; font-size: 28px; margin: 0; letter-spacing: -0.5px; }
        .header p { opacity: 0.9; font-size: 14px; margin-top: 8px; font-weight: 400; }

        .content { padding: 40px 35px; }

        /* Professional Input */
        .input-wrapper { margin-bottom: 25px; }
        .label { display: block; font-size: 12px; font-weight: 600; color: var(--primary); text-transform: uppercase; margin-bottom: 8px; letter-spacing: 1px; }
        
        .auth-field {
            width: 100%;
            padding: 18px;
            background: #f1f3f4;
            border: 2px solid transparent;
            font-size: 26px;
            text-align: center;
            letter-spacing: 10px;
            font-weight: 800;
            color: var(--text-main);
        }

        .auth-field:focus {
            background: white;
            border-color: var(--primary);
            box-shadow: 0 0 0 4px rgba(26,115,232,0.1);
            outline: none;
        }

        .btn-unlock {
            width: 100%;
            padding: 18px;
            background: var(--primary);
            color: white;
            border: none;
            font-weight: 700;
            font-size: 16px;
            cursor: pointer;
            letter-spacing: 0.5px;
            box-shadow: 0 8px 20px rgba(26,115,232,0.25);
        }

        .btn-unlock:hover {
            background: var(--primary-dark);
            transform: translateY(-2px);
            box-shadow: 0 12px 25px rgba(26,115,232,0.35);
        }

        /* Dashboard View */
        #dashboard { display: none; opacity: 0; transform: translateY(10px); }
        .card-item {
            background: #fff;
            padding: 20px;
            margin-bottom: 15px;
            border: 1px solid #eee;
            display: flex;
            align-items: center;
            gap: 20px;
            position: relative;
        }
        .card-item i { color: var(--primary); background: #f0f4ff; padding: 12px; font-size: 20px; }
        .card-item h3 { margin: 0; font-size: 16px; font-weight: 700; }
        .card-item p { margin: 4px 0 0; font-size: 13px; color: var(--text-sub); }

        /* Badge h24 */
        .status-badge {
            display: inline-block;
            padding: 4px 10px;
            background: #e6f4ea;
            color: #1e8e3e;
            font-size: 11px;
            font-weight: 700;
            margin-top: 10px;
        }

        @keyframes fadeIn {
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>
<body>

<div class="app-card">
    <div class="header">
        <i class="fas fa-shield-halved fa-3x" style="margin-bottom:15px; opacity:0.8"></i>
        <h1>PRIVATE VAULT</h1>
        <p>Enterprise-Grade Authentication</p>
    </div>

    <div class="content">
        <div id="login-screen">
            <div class="input-wrapper">
                <span class="label">Authenticator Code (180s)</span>
                <input type="text" id="code-input" class="auth-field" placeholder="000000" maxlength="6" autocomplete="off">
            </div>
            <button class="btn-unlock" onclick="unlock()">Sblocca Caveau</button>
        </div>

        <div id="dashboard">
            <div class="card-item">
                <i class="fas fa-user-shield"></i>
                <div>
                    <h3>Identità Verificata</h3>
                    <p>Utente: Root Admin</p>
                </div>
            </div>
            <div class="card-item">
                <i class="fas fa-folder-open"></i>
                <div>
                    <h3>File Sensibili</h3>
                    <p>4 Documenti Criptati</p>
                </div>
            </div>
            <div class="status-badge"><i class="fas fa-circle" style="font-size:8px; margin-right:5px"></i> SISTEMA LIVE h24</div>
        </div>
    </div>
</div>

<script>
    function unlock() {
        const code = document.getElementById('code-input').value;
        const btn = document.querySelector('.btn-unlock');
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Validazione...';
        
        fetch('/api/verify', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({code: code.toUpperCase()})
        }).then(res => {
            if(res.ok) {
                document.getElementById('login-screen').style.display = 'none';
                const dash = document.getElementById('dashboard');
                dash.style.display = 'block';
                setTimeout(() => { dash.style.animation = 'fadeIn 0.5s forwards'; }, 50);
            } else {
                alert("Codice di accesso non valido o scaduto.");
                btn.innerHTML = 'Sblocca Caveau';
                document.getElementById('code-input').value = '';
            }
        });
    }
</script>

</body>
</html>
"""

def get_totp_code():
    interval = int(time.time() / 180)
    seed = "mio-progetto-segreto-2026"
    return hashlib.sha256(f"{seed}-{interval}".encode()).hexdigest()[:6].upper()

@app.route('/')
def index():
    print(f"--- LOG SICUREZZA --- Codice Attuale: {get_totp_code()}")
    return HTML_UI

@app.route('/api/verify', methods=['POST'])
def verify():
    data = request.json
    if data.get('code') == get_totp_code():
        return jsonify({"status": "success"})
    return jsonify({"status": "error"}), 401

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
