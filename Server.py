from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

# Configurazione Groq (Llama 3)
GROQ_API_KEY = os.environ.get("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")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# Database dei contenuti
db = {
    "riassunto": "I Promessi Sposi sono il capolavoro di Alessandro Manzoni. Ambientato nella Lombardia del XVII secolo sotto il dominio spagnolo, narra le peripezie di Renzo Tramaglino e Lucia Mondella. L'opera si conclude con il celebre 'Sugo della Storia': la riflessione che i guai colpiscono chiunque, ma la fede in Dio li trasforma in un bene.",
    "flashcards": [
        {"q": "Chi sono i Bravi?", "a": "Sgherri al servizio dei potenti del '600."},
        {"q": "Cos'è la Provvidenza?", "a": "L'intervento divino che guida gli eventi umani."},
        {"q": "Chi è l'Innominato?", "a": "Un potente peccatore che si converte grazie a Lucia."}
    ]
}

def call_llama_manzoni(text):
    if not GROQ_API_KEY:
        return "Errore: Inserisci la GROQ_API_KEY su Render per farmi parlare!"
    
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": "Sei Alessandro Manzoni. Rispondi con tono colto, saggio ed elegante. Spiega la morale del tuo romanzo e i personaggi come se fossi l'autore originale."},
            {"role": "user", "content": text}
        ],
        "temperature": 0.6
    }
    try:
        r = requests.post(GROQ_URL, headers=headers, json=payload)
        return r.json()['choices'][0]['message']['content']
    except:
        return "Le mie riflessioni sono momentaneamente interrotte. Riprova tra poco."

HTML_UI = """
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manzoni OS | Apple Desktop</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root { --bg: #f5f5f7; --side: #e8e8ed; --accent: #0071e3; --text: #1d1d1f; }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'SF Pro Display', -apple-system, sans-serif; }
        
        body { background: var(--bg); color: var(--text); display: flex; height: 100vh; overflow: hidden; }

        /* Sidebar con Animazione */
        .sidebar { width: 280px; background: var(--side); padding: 40px 20px; border-right: 1px solid #d1d1d6; display: flex; flex-direction: column; gap: 8px; }
        .nav-item { padding: 14px 18px; border-radius: 12px; cursor: pointer; display: flex; align-items: center; gap: 15px; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); color: #424245; font-weight: 500; }
        .nav-item:hover { background: rgba(0,0,0,0.05); transform: translateX(5px); }
        .nav-item.active { background: var(--accent); color: white; box-shadow: 0 4px 12px rgba(0,113,227,0.3); }

        /* Main Area Animata */
        .main { flex: 1; padding: 80px; overflow-y: auto; display: none; opacity: 0; transform: translateY(20px); }
        .main.active { display: block; animation: appleAppear 0.6s forwards; }
        @keyframes appleAppear { to { opacity: 1; transform: translateY(0); } }

        h1 { font-size: 44px; font-weight: 700; margin-bottom: 40px; letter-spacing: -1.2px; }

        /* Glass Cards */
        .card { background: white; border-radius: 24px; padding: 40px; box-shadow: 0 10px 40px rgba(0,0,0,0.03); line-height: 1.6; font-size: 19px; border: 1px solid rgba(0,0,0,0.05); }

        /* Chat AI */
        .chat-ui { display: flex; flex-direction: column; height: 600px; background: white; border-radius: 24px; border: 1px solid #d1d1d6; overflow: hidden; }
        .messages { flex: 1; padding: 25px; overflow-y: auto; display: flex; flex-direction: column; gap: 15px; background: #fafafa; }
        .bubble { padding: 14px 20px; border-radius: 20px; max-width: 75%; font-size: 16px; animation: pop 0.3s ease; }
        @keyframes pop { from { transform: scale(0.9); opacity: 0; } to { transform: scale(1); opacity: 1; } }
        .user { align-self: flex-end; background: var(--accent); color: white; border-bottom-right-radius: 4px; }
        .manzoni { align-self: flex-start; background: #e9e9eb; color: black; border-bottom-left-radius: 4px; }
        .input-bar { display: flex; padding: 20px; background: white; border-top: 1px solid #eee; }
        .input-bar input { flex: 1; border: none; outline: none; font-size: 17px; padding: 10px; }

        /* Flashcards Grid */
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 20px; }
        .f-card { aspect-ratio: 1; background: white; border-radius: 22px; display: flex; align-items: center; justify-content: center; text-align: center; padding: 25px; cursor: pointer; transition: all 0.4s; border: 1px solid #eee; font-weight: 600; box-shadow: 0 4px 15px rgba(0,0,0,0.02); }
        .f-card:hover { transform: scale(1.05) rotate(2deg); box-shadow: 0 15px 35px rgba(0,0,0,0.08); border-color: var(--accent); }
    </style>
</head>
<body>

    <div class="sidebar">
        <div style="font-size: 24px; font-weight: 800; margin-bottom: 40px; color: var(--accent)">ManzoniOS</div>
        <div class="nav-item active" onclick="go('summary', this)"><i class="fas fa-book-open"></i> Riassunto</div>
        <div class="nav-item" onclick="go('chat', this)"><i class="fas fa-magic"></i> Chiedi all'Autore</div>
        <div class="nav-item" onclick="go('flash', this)"><i class="fas fa-clone"></i> Flashcards</div>
    </div>

    <div class="main active" id="summary">
        <h1>Il Romanzo.</h1>
        <div class="card" id="summary-content">Caricamento...</div>
    </div>

    <div class="main" id="chat">
        <h1>Conversazione.</h1>
        <div class="chat-ui">
            <div class="messages" id="chat-box">
                <div class="bubble manzoni">Benvenuto. Io sono Alessandro. Quale curiosità nutrite sul Sugo della Storia?</div>
            </div>
            <div class="input-bar">
                <input type="text" id="user-in" placeholder="Scrivete qui la vostra domanda...">
                <button onclick="ask()" style="background:none; border:none; color:var(--accent); font-weight:700; cursor:pointer; font-size:16px">Invia</button>
            </div>
        </div>
    </div>

    <div class="main" id="flash">
        <h1>Ripasso Rapido.</h1>
        <div class="grid" id="flash-grid"></div>
    </div>

    <script>
        function go(id, el) {
            document.querySelectorAll('.main').forEach(m => m.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            document.getElementById(id).classList.add('active');
            el.classList.add('active');
        }

        function ask() {
            const inp = document.getElementById('user-in');
            const box = document.getElementById('chat-box');
            if(!inp.value) return;

            box.innerHTML += `<div class="bubble user">${inp.value}</div>`;
            const query = inp.value;
            inp.value = "";
            box.scrollTop = box.scrollHeight;

            fetch('/api/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({msg: query})
            }).then(r => r.json()).then(data => {
                box.innerHTML += `<div class="bubble manzoni">${data.reply}</div>`;
                box.scrollTop = box.scrollHeight;
            });
        }

        fetch('/api/data').then(r => r.json()).then(data => {
            document.getElementById('summary-content').innerText = data.riassunto;
            document.getElementById('flash-grid').innerHTML = data.flashcards.map(f => `
                <div class="f-card" onclick="this.innerText='${f.a}'; this.style.color='#0071e3'">${f.q}</div>
            `).join('');
        });
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
    return jsonify({"reply": call_llama_manzoni(user_msg)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
