from flask import Flask, request, jsonify
import os

app = Flask(__name__)
app.secret_key = "vault_social_accounts_2026"

# DATABASE SIMULATO (Si resetta se il server si spegne su Render Free)
db = {
    "users": {"admin": "1234"}, # Utente di default
    "classrooms": [
        {"id": "main", "name": "Generale", "icon": "fa-globe"},
        {"id": "social", "name": "Community", "icon": "fa-users"}
    ],
    "posts": [
        {"user": "Admin", "class_id": "main", "content": "Benvenuti! Create un account per postare.", "time": "Ora"}
    ]
}

HTML_UI = """
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vault Social</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root { --p: #0095f6; --bg: #000; --card: #121212; --border: #262626; --txt: #fff; }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', sans-serif; }
        body { background: var(--bg); color: var(--txt); display: flex; justify-content: center; min-height: 100vh; }
        .app { width: 100%; max-width: 480px; border-left: 1px solid var(--border); border-right: 1px solid var(--border); position: relative; }

        /* Auth Screens */
        .auth-screen { padding: 40px; text-align: center; height: 100vh; background: #000; display: flex; flex-direction: column; justify-content: center; }
        .logo { font-size: 36px; font-weight: 800; margin-bottom: 40px; color: var(--p); }
        .field { width: 100%; padding: 14px; background: #1a1a1a; border: 1px solid var(--border); color: #fff; border-radius: 8px; margin-bottom: 15px; font-size: 16px; }
        .btn { width: 100%; padding: 14px; background: var(--p); color: #fff; border: none; border-radius: 8px; font-weight: 700; cursor: pointer; margin-top: 10px; }
        .toggle-link { margin-top: 20px; color: #888; font-size: 14px; cursor: pointer; }

        /* Main UI */
        #main-ui { display: none; }
        header { padding: 15px 20px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; background: rgba(0,0,0,0.8); backdrop-filter: blur(10px); position: sticky; top: 0; z-index: 10; }
        .class-bar { display: flex; gap: 10px; padding: 15px; overflow-x: auto; border-bottom: 1px solid var(--border); }
        .class-btn { padding: 8px 15px; background: var(--card); border: 1px solid var(--border); border-radius: 20px; font-size: 12px; cursor: pointer; white-space: nowrap; }
        .class-btn.active { background: var(--p); border-color: var(--p); }
        
        .feed { padding: 15px; padding-bottom: 100px; }
        .post { background: var(--card); border-radius: 12px; padding: 15px; margin-bottom: 15px; border: 1px solid var(--border); }
        .post-user { font-weight: 800; color: var(--p); margin-bottom: 5px; font-size: 14px; }
        
        .fab { position: fixed; bottom: 80px; right: 20px; width: 56px; height: 56px; background: var(--p); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 24px; cursor: pointer; box-shadow: 0 4px 15px rgba(0,0,0,0.4); }
        nav { position: fixed; bottom: 0; width: 100%; max-width: 480px; background: #000; border-top: 1px solid var(--border); display: flex; justify-content: space-around; padding: 15px; }
    </style>
</head>
<body>

<div class="app">
    <div id="auth-section" class="auth-screen">
        <div class="logo">VAULT SOCIAL</div>
        <div id="login-form">
            <input type="text" id="user-in" class="field" placeholder="Username">
            <input type="password" id="pass-in" class="field" placeholder="Password">
            <button class="btn" onclick="handleAuth('login')">Accedi</button>
            <p class="toggle-link" onclick="toggleAuth()">Non hai un account? Registrati</p>
        </div>
        <div id="reg-form" style="display:none">
            <input type="text" id="reg-user" class="field" placeholder="Scegli Username">
            <input type="password" id="reg-pass" class="field" placeholder="Crea Password">
            <button class="btn" onclick="handleAuth('register')">Crea Account</button>
            <p class="toggle-link" onclick="toggleAuth()">Hai già un account? Accedi</p>
        </div>
    </div>

    <div id="main-ui">
        <header>
            <span style="font-weight: 800; font-size: 20px;">Vault</span>
            <span id="my-name" style="color:var(--p); font-size: 14px;"></span>
        </header>
        
        <div class="class-bar" id="class-list"></div>
        <div class="feed" id="post-feed"></div>

        <div class="fab" onclick="addPost()"><i class="fas fa-plus"></i></div>
        
        <nav>
            <i class="fas fa-home"></i>
            <i class="fas fa-search"></i>
            <i class="fas fa-users" onclick="createClass()"></i>
            <i class="fas fa-user" onclick="location.reload()"></i>
        </nav>
    </div>
</div>

<script>
    let currentUser = "";
    let currentClass = "main";

    function toggleAuth() {
        const login = document.getElementById('login-form');
        const reg = document.getElementById('reg-form');
        login.style.display = login.style.display === 'none' ? 'block' : 'none';
        reg.style.display = reg.style.display === 'none' ? 'block' : 'none';
    }

    function handleAuth(type) {
        const u = document.getElementById(type === 'login' ? 'user-in' : 'reg-user').value;
        const p = document.getElementById(type === 'login' ? 'pass-in' : 'reg-pass').value;
        
        fetch('/api/' + type, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({user: u, pass: p})
        }).then(r => r.json()).then(data => {
            if(data.status === "ok") {
                currentUser = u;
                document.getElementById('auth-section').style.display = 'none';
                document.getElementById('main-ui').style.display = 'block';
                document.getElementById('my-name').innerText = "@" + u;
                loadData();
            } else { alert(data.msg); }
        });
    }

    function loadData() {
        fetch('/api/data').then(r => r.json()).then(data => {
            // Classrooms
            document.getElementById('class-list').innerHTML = data.classrooms.map(c => `
                <div class="class-btn ${c.id === currentClass ? 'active' : ''}" onclick="currentClass='${c.id}';loadData()">
                    ${c.name}
                </div>
            `).join('');

            // Posts
            const feed = document.getElementById('post-feed');
            const filtered = data.posts.filter(p => p.class_id === currentClass);
            feed.innerHTML = filtered.map(p => `
                <div class="post">
                    <div class="post-user">@${p.user}</div>
                    <div style="color:#ccc">${p.content}</div>
                </div>
            `).join('');
        });
    }

    function addPost() {
        const txt = prompt("Cosa vuoi pubblicare?");
        if(txt) {
            fetch('/api/post', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({user: currentUser, class_id: currentClass, content: txt})
            }).then(() => loadData());
        }
    }

    function createClass() {
        const name = prompt("Nome nuova Community:");
        if(name) {
            fetch('/api/class', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({name: name})
            }).then(() => loadData());
        }
    }
</script>
</body>
</html>
"""

@app.route('/')
def home(): return HTML_UI

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    if db["users"].get(data['user']) == data['pass']:
        return jsonify({"status": "ok"})
    return jsonify({"status": "err", "msg": "Credenziali errate"}), 401

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    if data['user'] in db["users"]:
        return jsonify({"status": "err", "msg": "Username già preso"}), 400
    db["users"][data['user']] = data['pass']
    return jsonify({"status": "ok"})

@app.route('/api/data')
def get_data(): return jsonify(db)

@app.route('/api/post', methods=['POST'])
def post():
    d = request.json
    db["posts"].insert(0, {"user": d['user'], "class_id": d['class_id'], "content": d['content'], "time": "Ora"})
    return jsonify({"status": "ok"})

@app.route('/api/class', methods=['POST'])
def make_class():
    n = request.json['name']
    db["classrooms"].append({"id": n.lower(), "name": n})
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
