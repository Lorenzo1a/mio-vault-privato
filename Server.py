from flask import Flask, request, jsonify
import time
import hashlib
import os

app = Flask(__name__)
app.secret_key = "vault_community_pro_2026"

# DATABASE SIMULATO CON CLASSROOM
vault_db = {
    "classrooms": [
        {"id": "main", "name": "Generale", "icon": "fa-globe"},
        {"id": "secret", "name": "Top Secret", "icon": "fa-user-secret"}
    ],
    "posts": [
        {"id": 1, "class_id": "main", "user": "Admin", "content": "Benvenuti nella Community Generale!", "time": "1h fa"},
        {"id": 2, "class_id": "secret", "user": "Admin", "content": "Questo post è visibile solo nella Classroom Secret.", "time": "10m fa"}
    ]
}

def get_totp_code():
    interval = int(time.time() / 600)
    return hashlib.sha256(f"secret-seed-2026-{interval}".encode()).hexdigest()[:6].upper()

HTML_UI = """
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vault Community</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root { --p: #0095f6; --bg: #050505; --card: #181818; --border: #2f2f2f; --txt: #ffffff; }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', sans-serif; }
        body { background: var(--bg); color: var(--txt); display: flex; justify-content: center; min-height: 100vh; }
        
        .app { width: 100%; max-width: 500px; display: flex; flex-direction: column; position: relative; border-left: 1px solid var(--border); border-right: 1px solid var(--border); }

        /* Login */
        #login { padding: 40px; text-align: center; height: 100vh; background: #000; z-index: 1000; position: fixed; width: 100%; max-width: 500px; }
        .logo { font-size: 32px; font-weight: 800; margin: 50px 0; letter-spacing: -1px; }
        .input-box { width: 100%; padding: 15px; background: #111; border: 1px solid var(--border); color: #fff; border-radius: 12px; font-size: 20px; text-align: center; margin-bottom: 20px; }
        .btn-main { width: 100%; padding: 15px; background: var(--p); color: #fff; border: none; border-radius: 12px; font-weight: 700; cursor: pointer; }

        /* Main UI */
        #main-ui { display: none; }
        header { padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); background: rgba(0,0,0,0.9); position: sticky; top: 0; z-index: 100; }
        
        /* Classroom Bar */
        .class-bar { display: flex; gap: 12px; padding: 15px; overflow-x: auto; scrollbar-width: none; background: #0a0a0a; border-bottom: 1px solid var(--border); }
        .class-item { min-width: 100px; padding: 10px; background: var(--card); border: 1px solid var(--border); border-radius: 10px; text-align: center; cursor: pointer; transition: 0.2s; }
        .class-item.active { border-color: var(--p); background: rgba(0, 149, 246, 0.1); }
        .class-item i { display: block; margin-bottom: 5px; color: var(--p); }

        /* Feed */
        .feed { padding: 15px; padding-bottom: 100px; }
        .post { background: var(--card); border-radius: 15px; padding: 15px; margin-bottom: 15px; border: 1px solid var(--border); }
        .post-header { font-size: 14px; font-weight: 800; margin-bottom: 10px; color: var(--p); }
        .post-body { font-size: 15px; line-height: 1.5; color: #ccc; }

        /* Floating Button */
        .fab { position: fixed; bottom: 85px; right: 20px; width: 56px; height: 56px; background: var(--p); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 24px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); cursor: pointer; z-index: 99; }

        /* Bottom Nav */
        nav { position: fixed; bottom: 0; width: 100%; max-width: 500px; background: #000; border-top: 1px solid var(--border); display: flex; justify-content: space-around; padding: 20px; }
    </style>
</head>
<body>

<div class="app">
    <div id="login">
        <div class="logo">VAULT <span style="color:var(--p)">COMMUNITY</span></div>
        <input type="text" id="code-input" class="input-box" placeholder="CODICE ACCESSO">
        <button class="btn-main" onclick="verify()">ENTRA NEL VAULT</button>
    </div>

    <div id="main-ui">
        <header>
            <span id="current-class-title" style="font-weight: 800;">Generale</span>
            <button onclick="createClassroom()" style="background:none; border:1px solid var(--border); color:#888; padding:5px 10px; border-radius:5px; font-size:12px">+ Community</button>
        </header>

        <div class="class-bar" id="class-list"></div>

        <div class="feed" id="post-feed"></div>

        <div class="fab" onclick="writePost()"><i class="fas fa-plus"></i></div>

        <nav>
            <i class="fas fa-home"></i>
            <i class="fas fa-users"></i>
            <i class="fas fa-bell"></i>
            <i class="fas fa-user"></i>
        </nav>
    </div>
</div>

<script>
    let currentClass = 'main';
    let database = {};

    function verify() {
        const code = document.getElementById('code-input').value.toUpperCase();
        fetch('/api/auth', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({code: code})
        }).then(r => r.json()).then(data => {
            if(data.status === "ok") {
                database = data.db;
                document.getElementById('login').style.display = 'none';
                document.getElementById('main-ui').style.display = 'block';
                renderUI();
            } else { alert("Codice errato!"); }
        });
    }

    function renderUI() {
        // Render Classrooms
        const classList = document.getElementById('class-list');
        classList.innerHTML = database.classrooms.map(c => `
            <div class="class-item ${c.id === currentClass ? 'active' : ''}" onclick="switchClass('${c.id}')">
                <i class="fas ${c.icon}"></i>
                <div style="font-size:11px">${c.name}</div>
            </div>
        `).join('');

        // Render Posts
        const feed = document.getElementById('post-feed');
        const filteredPosts = database.posts.filter(p => p.class_id === currentClass);
        feed.innerHTML = filteredPosts.map(p => `
            <div class="post">
                <div class="post-header">@${p.user}</div>
                <div class="post-body">${p.content}</div>
                <div style="font-size:10px; color:#555; margin-top:10px">${p.time}</div>
            </div>
        `).join('');
        
        document.getElementById('current-class-title').innerText = 
            database.classrooms.find(c => c.id === currentClass).name;
    }

    function switchClass(id) {
        currentClass = id;
        renderUI();
    }

    function createClassroom() {
        const name = prompt("Nome della nuova Community:");
        if(name) {
            fetch('/api/create_class', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({name: name})
            }).then(r => r.json()).then(data => {
                database = data;
                renderUI();
            });
        }
    }

    function writePost() {
        const text = prompt("Cosa vuoi scrivere in questa Community?");
        if(text) {
            fetch('/api/add_post', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({class_id: currentClass, content: text})
            }).then(r => r.json()).then(data => {
                database = data;
                renderUI();
            });
        }
    }
</script>
</body>
</html>
"""

@app.route('/')
def home(): return HTML_UI

@app.route('/api/auth', methods=['POST'])
def auth():
    code = get_totp_code()
    if request.json.get('code') == code:
        return jsonify({"status": "ok", "db": vault_db})
    return jsonify({"status": "err"}), 401

@app.route('/api/create_class', methods=['POST'])
def create_class():
    name = request.json.get('name')
    new_id = name.lower().replace(" ", "_")
    vault_db["classrooms"].append({"id": new_id, "name": name, "icon": "fa-users-rectangle"})
    return jsonify(vault_db)

@app.route('/api/add_post', methods=['POST'])
def add_post():
    data = request.json
    new_p = {
        "id": len(vault_db["posts"]) + 1,
        "class_id": data['class_id'],
        "user": "Tu",
        "content": data['content'],
        "time": "Adesso"
    }
    vault_db["posts"].insert(0, new_p)
    return jsonify(vault_db)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
