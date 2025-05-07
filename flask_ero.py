# app.py – improved UI while keeping original logic and structure untouched
from flask import Flask, request, redirect, url_for, render_template_string
import bcrypt, json, time

app = Flask(__name__)

users, logs, math = [], [], {}
next_cost = 10

def add_log(m): logs.append(m)
def parse_bcrypt(h):
    _, alg, cost, tail = h.split('$')
    cost = int(cost)
    salt, hash_ = tail[:22], tail[22:]
    return dict(fullHash=h, alg=alg, cost=cost, salt=salt, hash=hash_)

@app.route('/', methods=['GET'])
def index():
    complexity_per = [(1 << parse_bcrypt(u["hash"])["cost"]) * u["len"] for u in users]
    total_complexity = sum(complexity_per)
    erosolar_data = {
        "labels": ["Love", "Courage", "Wonder", "Joy", "Resilience", "Peace"],
        "datasets": [{
            "label": "Erosolar Spirit",
            "data": [100, 98, 95, 99, 97, 100],
            "backgroundColor": [
                'rgba(255, 99, 132, 0.5)', 'rgba(255, 159, 64, 0.5)',
                'rgba(255, 205, 86, 0.5)', 'rgba(75, 192, 192, 0.5)',
                'rgba(54, 162, 235, 0.5)', 'rgba(153, 102, 255, 0.5)'
            ]
        }]
    }
    complexity_data = {
        "labels": [f"Users: {len(users)}"],
        "datasets": [{
            "label": "Σ 2^cost × |pw|",
            "data": [total_complexity],
            "backgroundColor": "rgba(255, 99, 132, 0.5)"
        }]
    }
    per_user_data = {
        "labels": [u["email"] for u in users],
        "datasets": [{
            "label": "2^cost × |pw| (per user)",
            "data": complexity_per,
            "backgroundColor": "rgba(54, 162, 235, 0.5)"
        }]
    }
    return render_template_string("""
<!doctype html>
<html lang="en" class="scroll-smooth">
  <head>
    <meta charset="utf-8">
    <title>Erosolar Flask</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://cdn.tailwindcss.com?plugins=typography"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  </head>
  <body class="min-h-screen bg-gradient-to-tr from-purple-900 via-indigo-900 to-blue-900 text-white font-sans">
    <header class="backdrop-blur bg-white/10 shadow-lg sticky top-0 z-20">
      <div class="max-w-5xl mx-auto flex items-center justify-between p-4">
        <h1 class="text-2xl font-bold tracking-wide">Password Complexity Visualizer</h1>
        <nav class="space-x-4 text-sm">
          <a href="#charts" class="hover:underline">Charts</a>
          <a href="#logs" class="hover:underline">Logs</a>
          <a href="#math" class="hover:underline">Math</a>
        </nav>
      </div>
    </header>

    <main class="max-w-5xl mx-auto px-4 py-10 space-y-16">
      <!-- Hero -->
      <section class="text-center space-y-4">
        <h2 class="text-4xl font-extrabold">Stronger Hashes ≠ Impossible Breaks</h2>
        <p class="text-lg text-gray-300 max-w-3xl mx-auto">
          Explore how bcrypt’s cost factor grows exponentially to protect against brute-force attacks.  
          Each signup updates live complexity metrics below.
        </p>
      </section>

      <!-- Forms -->
      <section class="grid md:grid-cols-2 gap-8">
        <form class="bg-white/10 rounded-xl p-6 space-y-4" action="{{url_for('signup')}}" method="post">
          <h3 class="text-xl font-semibold">Sign Up</h3>
          <div class="flex gap-2">
            <input name="cost" placeholder="cost" value="{{cost}}" class="w-24 px-3 py-2 rounded-lg text-gray-900" />
            <input name="email" placeholder="email" class="flex-1 px-3 py-2 rounded-lg text-gray-900" />
          </div>
          <input name="pw" placeholder="password" type="password" class="w-full px-3 py-2 rounded-lg text-gray-900" />
          <div class="flex gap-2">
            <button class="flex-1 bg-emerald-600 hover:bg-emerald-700 rounded-lg py-2 font-semibold">Sign Up</button>
            <button formaction="{{url_for('auto_setup')}}" class="bg-indigo-600 hover:bg-indigo-700 rounded-lg px-3 py-2">Auto Demo</button>
          </div>
        </form>

        <form class="bg-white/10 rounded-xl p-6 space-y-4" action="{{url_for('login')}}" method="post">
          <h3 class="text-xl font-semibold">Login</h3>
          <input name="email" placeholder="email" class="w-full px-3 py-2 rounded-lg text-gray-900" />
          <input name="pw" placeholder="password" type="password" class="w-full px-3 py-2 rounded-lg text-gray-900" />
          <button class="w-full bg-orange-600 hover:bg-orange-700 rounded-lg py-2 font-semibold">Login</button>
        </form>

        <form class="bg-white/10 rounded-xl p-6 space-y-4 md:col-span-2" action="{{url_for('detect_leak')}}" method="post">
          <h3 class="text-xl font-semibold">Leak Detector</h3>
          <div class="flex gap-2">
            <input name="pw" placeholder="suspected plaintext" class="flex-1 px-3 py-2 rounded-lg text-gray-900" />
            <button class="bg-pink-600 hover:bg-pink-700 rounded-lg px-4 py-2 font-semibold">Check</button>
          </div>
        </form>
      </section>

      <!-- Charts -->
      <section id="charts" class="space-y-16">
        <div class="bg-white/5 rounded-xl p-6">
          <h3 class="text-xl font-semibold mb-4">Erosolar Spirit</h3>
          <canvas id="erosolar"></canvas>
        </div>

        <div class="grid md:grid-cols-2 gap-8">
          <div class="bg-white/5 rounded-xl p-6">
            <h3 class="text-xl font-semibold mb-4">Total Complexity</h3>
            <canvas id="complexity"></canvas>
          </div>
          <div class="bg-white/5 rounded-xl p-6">
            <h3 class="text-xl font-semibold mb-4">Per-User Complexity</h3>
            <canvas id="peruser"></canvas>
          </div>
        </div>
      </section>

      <!-- Logs & Math -->
      <section id="logs" class="space-y-8">
        <h3 class="text-2xl font-semibold">Logs</h3>
        <pre class="bg-gray-900 rounded-lg p-4 overflow-x-auto text-green-400">{{'\\n'.join(logs)}}</pre>
      </section>

      <section id="math" class="space-y-8">
        <h3 class="text-2xl font-semibold">Bcrypt Math</h3>
        <pre class="bg-gray-900 rounded-lg p-4 overflow-x-auto text-cyan-300">{{math_json}}</pre>
        <p class="text-sm text-gray-400 italic">Σ 2<sup>cost</sup> × |pw| represents the total brute-force space an attacker must traverse.</p>
      </section>
    </main>

    <footer class="py-8 text-center text-gray-400 text-sm">
      Built with ❤ by Bo — <a href="https://erosolar.online" class="underline hover:text-white">Erosolar</a>
    </footer>

    <script>
      const ed={{erosolar|tojson}}, cd={{complexity|tojson}}, pud={{per_user_data|tojson}};
      const baseOpts={responsive:true,plugins:{legend:{position:'top'},title:{display:false}}};
      new Chart(document.getElementById('erosolar'),{type:'bar',data:ed,options:baseOpts});
      new Chart(document.getElementById('complexity'),{type:'bar',data:cd,options:baseOpts});
      if(pud.labels.length){
        new Chart(document.getElementById('peruser'),{type:'bar',data:pud,options:baseOpts});
      }
    </script>
  </body>
</html>
""", logs=logs, math_json=json.dumps(math, indent=2),
       erosolar=erosolar_data, complexity=complexity_data,
       per_user_data=per_user_data, cost=next_cost)

@app.route('/signup', methods=['POST'])
def signup():
    global next_cost
    cost = int(request.form.get('cost', 10) or 10)
    email, pw = request.form['email'].strip(), request.form['pw']
    if not email or not pw:
        add_log('Signup failed – email and password required')
        return redirect(url_for('index'))
    if any(u["email"] == email for u in users):
        add_log(f'Signup failed – {email} exists')
        return redirect(url_for('index'))
    salt = bcrypt.gensalt(rounds=cost)
    h = bcrypt.hashpw(pw.encode(), salt).decode()
    users.append(dict(email=email, salt=salt.decode(), hash=h, len=len(pw)))
    math[email] = parse_bcrypt(h)
    add_log(f'Signup {email} → hash saved (cost={cost})')
    next_cost = cost
    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    email, pw = request.form['email'].strip(), request.form['pw']
    u = next((x for x in users if x["email"] == email), None)
    if not u:
        add_log(f'Login failed – unknown user {email}')
        return redirect(url_for('index'))
    ok = bcrypt.checkpw(pw.encode(), u["hash"].encode())
    add_log(f'Login {u["email"]} with "{pw}" → {"success" if ok else "failure"}')
    return redirect(url_for('index'))

@app.route('/detect_leak', methods=['POST'])
def detect_leak():
    pw = request.form['pw']
    add_log(f'Users in DB: {len(users)}')
    complexity = sum((1 << parse_bcrypt(u["hash"])["cost"]) * u["len"] for u in users)
    add_log(f'Complexity this check: {complexity}')
    found = False
    for u in users:
        h = bcrypt.hashpw(pw.encode(), (u["salt"]).encode()).decode()
        if h == u["hash"]:
            cost = parse_bcrypt(u["hash"])["cost"]
            add_log(f'Leak match: \"{pw}\" for {u["email"]} (cost={cost})')
            found = True
    if not found:
        add_log(f'Leak check: \"{pw}\" matched no users')
    return redirect(url_for('index'))

@app.route('/auto_setup', methods=['POST'])
def auto_setup():
    for idx, pw in enumerate(['password123', 'password321']):
        email = f'erosolar_bits_{int(time.time()*1000)}_{idx}@auto.bot'
        cost = int(request.form.get('cost', 10) or 10)
        salt = bcrypt.gensalt(rounds=cost)
        h = bcrypt.hashpw(pw.encode(), salt).decode()
        users.append(dict(email=email, salt=salt.decode(), hash=h, len=len(pw)))
        math[email] = parse_bcrypt(h)
        add_log(f'Signup {email} → hash saved (cost={cost})')
        detect_leak_internal(pw)
    return redirect(url_for('index'))

def detect_leak_internal(pw):
    add_log(f'Users in DB: {len(users)}')
    complexity = sum((1 << parse_bcrypt(u["hash"])["cost"]) * u["len"] for u in users)
    add_log(f'Complexity this check: {complexity}')
    found = False
    for u in users:
        h = bcrypt.hashpw(pw.encode(), u["salt"].encode()).decode()
        if h == u["hash"]:
            cost = parse_bcrypt(u["hash"])["cost"]
            add_log(f'Leak match: \"{pw}\" for {u["email"]} (cost={cost})')
            found = True
    if not found:
        add_log(f'Leak check: \"{pw}\" matched no users')

if __name__ == '__main__':
    app.run(debug=True)