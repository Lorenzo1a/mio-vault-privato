from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

# Database iniziale
db = {
    "riassunto": "I Promessi Sposi raccontano l'avventura di Renzo e Lucia nella Lombardia del '600. La storia culmina nel 'Sugo della Storia': la consapevolezza che i guai arrivano indipendentemente dalla colpa, ma la fede trasforma la sofferenza in un bene superiore.",
    "flashcards": [
        {"q": "Chi è l'Innominato?", "a": "Un potente criminale che si converte grazie a Lucia."},
        {"q": "Cosa rappresenta la pioggia finale?", "a": "La purificazione dalla peste e il rinnovamento."},
    ]
}

# Funzione per simulare Manzoni AI (Usa un'API gratuita o logica interna avanzata)
def manzoni_ai_logic(user_text):
    prompt = f"Rispondi come Alessandro Manzoni, autore dei Promessi Sposi. Usa un linguaggio elegante, ottocentesco ma comprensibile. Spiega il 'sugo della storia' o i personaggi. Domanda: {user_text}"
    
    # Per rendere il server stabile su Render Free, usiamo una logica di risposta simulata colta
    # Se avessi una chiave API Groq/OpenAI, la inseriresti qui.
    risposte_tipo = {
        "sugo": "Figliol mio, il sugo della storia è che i guai vengono spesso perché ci si è dato cagione; ma la condotta più cauta non basta a tenerli lontani. Quando vengono, la fiducia in Dio li raddolcisce.",
        "lucia": "Lucia è l'anima pura, colei che nella sventura non perde mai la bussola della Provvidenza.",
        "default": "Ai posteri l'ardua sentenza. La vostra domanda merita riflessione, ma ricordate che la Provvidenza opera in modi misteriosi."
    }
    
    input_lower = user_text.lower()
    if "sugo" in input_lower: return risposte_tipo["sugo"]
    if "lucia" in input_lower or "renzo" in input_lower: return risposte_tipo["lucia"]
    return risposte_tipo["default"]

HTML_UI = """
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manzoni OS - Desktop</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root { --bg: #f5f5f7; --sidebar: #e8e8ed; --accent: #0071e3; --text: #1d1d1f; }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'SF Pro Display', -apple-system, sans-serif; }
        
        body { background: var(--bg); color: var(--text); display: flex; height: 100vh; overflow: hidden; }

        /* Sidebar Desktop Style */
        .sidebar { width: 260px; background: var(--sidebar); padding: 30px 20px; display: flex; flex-direction: column; gap: 10px; border-right: 1px solid #d1d1d6; }
        .nav-item { padding: 12px 15px; border-radius: 10px; cursor: pointer; display: flex; align-items: center; gap: 12px; transition: 0.2s; color: #424245; font-weight: 500; }
        .nav-item:hover { background: #dcdce0; }
        .nav-item.active { background: var(--accent); color: white; }

        /* Main Content */
        .main { flex: 1; padding: 60px; overflow-y: auto; display: none; }
        .main.active { display: block; animation: slideIn 0.5s ease; }
        @keyframes slideIn { from { opacity: 0; transform: scale(0.98); } to { opacity: 1; transform: scale(1); } }

        h1 { font-size: 40px; font-weight: 700; margin-bottom: 30px; letter-spacing: -1px; }

        /* Card Apple Style */
        .glass-card { background: white; border-radius: 24px; padding: 40px; box-shadow: 0 8px 30px rgba(0,0,0,0.04); margin-bottom: 30px; line-height: 1.6; font-size: 18px; }

        /* AI Chat Box */
        .chat-container { display: flex; flex-direction: column; height: 500px; background: white; border-radius: 20px; overflow: hidden; border: 1px solid #d1d1d6; }
        .chat-messages { flex: 1; padding: 20px; overflow-y: auto; background: #fafafa; }
        .bubble { padding: 12px 18px; border-radius: 18px; margin-bottom: 10px; max-width: 80%; font-size: 15px; }
        .user-b { align-self: flex-end; background: var(--accent); color: white; margin-left: auto; }
        .manzoni-b { align-self: flex-start; background: #e9e9eb; color: black; }
        .chat-input { display: flex; padding: 15px; border-top: 1px solid #d1d1d6; background: white; }
        .chat-input input { flex: 1; padding: 10px; border: none; outline: none; font-size: 16px; }

        /* Flashcards Grid */
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 20px; }
        .f-card { aspect-ratio: 1; background: white; border-radius: 20px; display: flex; align-items: center; justify-content: center; text-align: center; padding: 20px; cursor: pointer; border: 1px solid #eee; transition: 0.3s; font-weight: 600; }
        .f-card:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.05); }
    </style>
</head>
<body>

    <div class="sidebar">
        <div style="font-weight: 800; font-size: 20px; margin-bottom: 30px; padding-left: 10px;">Manzoni Hub</div>
        <div class="nav-item active" onclick="setView('summary', this)"><i class="fas fa-book"></i> Riassunto</div>
        <div class="nav-item" onclick="setView('chat', this)"><i class="fas fa-comment-dots"></i> Parla con l'Autore</div>
        <div class="nav-item" onclick="setView('flash', this)"><i class="fas fa-clone"></i> Flashcards</div>
    </div>

    <div class="main active" id="summary">
        <h1>Riassunto Esecutivo.</h1>
        <div class="glass-card" id="riassunto-text">Caricamento...</div>
        <div class="glass-card" style="background: linear-gradient(135deg, #0071e3, #42a5f5); color: white;">
            <h2>Il Sugo della Storia</h2>
            <p>La morale definitiva dell'opera racchiusa in un'esperienza digitale.</p>
        </div>
    </div>

    <div class="main" id="chat">
        <h1>Chiedi ad Alessandro.</h1>
        <div class="chat-container">
            <div class="chat-messages" id="chat-box">
                <div class="bubble manzoni-b">Benvenuto, caro lettore. Sono Alessandro. Cosa desiderate approfondire del mio modesto romanzo?</div>
            </div>
            <div class="chat-input">
                <input type="text" id="user-msg" placeholder="Chiedi del sugo della storia...">
                <button onclick="sendMessage()" style="background:none; border:none; color:var(--accent); font-weight:700; cursor:pointer;">Invia</button>
            </div>
        </div>
    </div>

    <div class="main" id="flash">
        <h1>Esercitati.</h1>
        <div class="grid" id="flash-grid"></div>
    </div>

    <script>
        function setView(id, el) {
            document.querySelectorAll('.main').forEach(m => m.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            document.getElementById(id).classList.add('active');
            el.classList.add('active');
        }

        function loadData() {
            fetch('/api/data').then(r => r.json()).then(data => {
                document.getElementById('riassunto-text').innerText = data.riassunto;
                const grid = document.getElementById('flash-grid');
                grid.innerHTML = data.flashcards.map(f => `
                    <div class="f-card" onclick="alert('${f.a}')">${f.q}</div>
                `).join('');
            });
        }

        function sendMessage() {
            const input = document.getElementById('user-msg');
            const msg = input.value;
            if(!msg) return;

            const box = document.getElementById('chat-box');
            box.innerHTML += `<div class="bubble user-b">${msg}</div>`;
            input.value = "";

            fetch('/api/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({msg: msg})
            }).then(r => r.json()).then(data => {
                box.innerHTML += `<div class="bubble manzoni-b">${data.reply}</div>`;
                box.scrollTop = box.scrollHeight;
            });
        }

        window.onload = loadData;
    </script>
</body>
</html>
"""

@app.route('/')
def home(): return HTML_UI

@app.route('/api/data')
def get_data(): return jsonify(db)

@app.route('/api/chat', methods=['POST'])
def chat():
    user_msg = request.json.get('msg')
    reply = manzoni_ai_logic(user_msg)
    return jsonify({"reply": reply})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
