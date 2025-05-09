from flask import Flask, request, redirect, url_for, render_template_string
import bcrypt, json, time, math as _m
from waitress import serve  # production WSGI server

app = Flask(__name__)

users, logs, math = [], [], {}
next_cost = 10

def add_log(m): logs.append(m)
def parse_bcrypt(h):
    _, alg, cost, tail = h.split('$')
    cost = int(cost)
    salt, hash_ = tail[:22], tail[22:]
    return dict(fullHash=h, alg=alg, cost=cost, salt=salt, hash=hash_)

def compute_aws_vs_twitch_proof():
    twitch_users = 10**12
    cost = 14
    avg_pw_len = 10
    ops_needed = twitch_users * (1 << cost) * avg_pw_len
    aws_vcpu = 400_000_000
    ops_per_core = 1
    aws_ops = aws_vcpu * ops_per_core
    years = ops_needed / (aws_ops * 31536000)
    return {
        "twitch_users": twitch_users,
        "bcrypt_cost": cost,
        "avg_pw_len": avg_pw_len,
        "ops_needed": ops_needed,
        "aws_vcpu": aws_vcpu,
        "aws_ops_per_sec": aws_ops,
        "years_to_complete": years,
        "summary": f"Even with {aws_ops:_} bcrypt/s, AWS needs {years:.1f} years – infeasible for plaintext recovery."
    }

@app.route('/ero', methods=['GET'])
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
    proof = compute_aws_vs_twitch_proof()
    math_full = {"users": math, "aws_vs_twitch": proof}
    return render_template_string("""
<!doctype html>
<html lang="en" class="scroll-smooth">
  <head>
    <meta charset="utf-8">
    <title>Erosolar Flask</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="icon" href="{{ url_for('static', filename='favicon.ico') }}" type="image/x-icon">
    <script src="https://cdn.tailwindcss.com?plugins=typography"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  </head>
  <body class="min-h-screen bg-gradient-to-tr from-purple-950 via-indigo-950 to-blue-950 text-white font-sans overflow-x-hidden">

    <!-- PANDA DOMINANCE ZONE -->
    <section id="panda-zone" class="relative h-48 pointer-events-none">
      <div class="absolute inset-0 flex flex-col items-center justify-center animate-bounce space-y-2">
        <img src="{{ url_for('static', filename='favicon.ico') }}" alt="Panda" class="h-28 w-28 drop-shadow-xl">
        <span class="bg-black/60 px-4 py-1 rounded-lg text-sm whitespace-nowrap">
          AWS & Twitch, even all your servers can’t crack a trillion bcrypt hashes!
        </span>
      </div>
    </section>

    <!-- Women's History Month Hero -->
    <div class="relative w-full">
      <img src="{{ url_for('static', filename='Sam_Womens_History.png') }}"
           alt="Women's History Month"
           class="w-full max-h-96 object-cover shadow-2xl border-4 border-pink-400/70 rounded-b-3xl">
      <div class="absolute inset-0 flex flex-col items-center justify-center text-center bg-black/40 backdrop-blur-sm">
        <h2 class="text-5xl font-extrabold tracking-widest drop-shadow-lg mb-3 bg-gradient-to-r from-pink-300 via-rose-300 to-amber-200 text-transparent bg-clip-text">
          Happy Women's History Month!
        </h2>
        <p class="max-w-3xl text-lg font-semibold text-pink-100">
          Honoring the visionaries, dreamers & trailblazers whose brilliance lights up our past, present & future.
        </p>
      </div>
    </div>

    <header class="backdrop-blur bg-white/10 shadow-lg sticky top-48 z-20">
      <div class="max-w-5xl mx-auto flex items-center justify-between p-4">
        <h1 class="text-2xl font-bold tracking-wide">Password Complexity Visualizer</h1>
        <nav class="space-x-4 text-sm">
          <a href="#charts" class="hover:underline">Charts</a>
          <a href="#aws_proof" class="hover:underline">AWS Proof</a>
          <a href="#logs" class="hover:underline">Logs</a>
          <a href="#math" class="hover:underline">Math</a>
        </nav>
      </div>
    </header>

    <main class="max-w-5xl mx-auto px-4 py-10 space-y-16">
      <section class="text-center space-y-4">
        <h2 class="text-4xl font-extrabold">Stronger Hashes ≠ Impossible Breaks</h2>
        <p class="text-lg text-gray-300 max-w-3xl mx-auto">
          Explore how bcrypt’s cost factor grows exponentially to protect against brute-force attacks.  
          Each signup updates live complexity metrics below.
        </p>
      </section>

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

      <section id="aws_proof" class="space-y-8">
        <h3 class="text-2xl font-semibold">AWS Proof – 13+ Years to Crack</h3>
        <pre class="bg-gray-900 rounded-lg p-4 overflow-x-auto text-yellow-300">{{proof_json}}</pre>
        <p class="text-sm text-pink-200 italic">Happy Women's History Month – we rise by lifting others!</p>
      </section>

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
""", logs=logs, math_json=json.dumps(math_full, indent=2),
       erosolar=erosolar_data, complexity=complexity_data,
       per_user_data=per_user_data, cost=next_cost, proof_json=json.dumps(proof, indent=2))

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
            add_log(f'Leak match: "{pw}" for {u["email"]} (cost={cost})')
            found = True
    if not found:
        add_log(f'Leak check: "{pw}" matched no users')
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
            add_log(f'Leak match: "{pw}" for {u["email"]} (cost={cost})')
            found = True
    if not found:
        add_log(f'Leak check: "{pw}" matched no users')

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5999)