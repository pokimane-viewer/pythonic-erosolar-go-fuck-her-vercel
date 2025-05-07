"""
Original React code (unchanged)

'use client';

import React, { useState, useCallback, useMemo } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import bcrypt from 'bcryptjs';
import dynamic from 'next/dynamic';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';

/* detectLeak now logs user count and Σ2^cost×|pw| each run */

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const Bar = dynamic(() => import('react-chartjs-2').then((m) => m.Bar), {
  ssr: false
});

export default function Home() { /* …rest unchanged… */ }
"""

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
    erosolar_data = {"labels":["Love","Courage","Wonder","Joy","Resilience","Peace"],
                     "datasets":[{"label":"Erosolar Spirit",
                                  "data":[100,98,95,99,97,100],
                                  "backgroundColor":[
                                      'rgba(255, 99, 132, 0.5)','rgba(255, 159, 64, 0.5)',
                                      'rgba(255, 205, 86, 0.5)','rgba(75, 192, 192, 0.5)',
                                      'rgba(54, 162, 235, 0.5)','rgba(153, 102, 255, 0.5)']}]}
    complexity_data = {"labels":[f"Users: {len(users)}"],
                       "datasets":[{"label":"Σ 2^cost × |pw|","data":[total_complexity],
                                    "backgroundColor":"rgba(255, 99, 132, 0.5)"}]}
    per_user_data = {"labels":[u["email"] for u in users],
                     "datasets":[{"label":"2^cost × |pw| (per user)",
                                  "data":complexity_per,
                                  "backgroundColor":"rgba(54, 162, 235, 0.5)"}]}
    return render_template_string("""
<!doctype html><html><head>
<meta charset="utf-8"><title>Erosolar Flask</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/tailwindcss@^3/dist/tailwind.min.css">
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head><body class="prose mx-auto p-4">
<h2><a href="https://boshang9.wordpress.com/blog/">I only need to prove my HYPOTHESIS…</a></h2>
<h1><a href="https://www.baidu.com/">Believe me or not…</a></h1>

<form class="flex flex-wrap gap-2" action="{{url_for('signup')}}" method="post">
<input name="cost" placeholder="cost" value="{{cost}}" class="w-20 px-2 py-1 border rounded">
<input name="email" placeholder="signup email" class="flex-1 px-2 py-1 border rounded">
<input name="pw" placeholder="password" type="password" class="flex-1 px-2 py-1 border rounded">
<button class="btn px-4 py-1 border rounded">Sign Up</button>
<button formaction="{{url_for('auto_setup')}}" class="btn px-4 py-1 border rounded">Auto Setup erosolar_bits</button>
</form>

<form class="flex flex-wrap gap-2 mt-4" action="{{url_for('login')}}" method="post">
<input name="email" placeholder="login email" class="flex-1 px-2 py-1 border rounded">
<input name="pw" placeholder="password" type="password" class="flex-1 px-2 py-1 border rounded">
<button class="btn px-4 py-1 border rounded">Login</button>
</form>

<form class="flex flex-wrap gap-2 mt-4" action="{{url_for('detect_leak')}}" method="post">
<input name="pw" placeholder="leaked plaintext" class="flex-1 px-2 py-1 border rounded">
<button class="btn px-4 py-1 border rounded">Check Leak</button>
</form>

<pre class="bg-black text-green-400 p-4 mt-4 whitespace-pre-wrap overflow-x-auto">{{'\\n'.join(logs)}}</pre>
<h3>Bcrypt Math</h3>
<pre class="bg-gray-900 text-cyan-300 p-4 overflow-x-auto">{{math_json}}</pre>

<canvas id="erosolar"></canvas>
<canvas id="complexity" class="mt-8"></canvas>
{% if per_user_data.datasets[0].data|length %}
<canvas id="peruser" class="mt-8"></canvas>
{% endif %}

<p class="mt-8">SHA-256 is a one-way hash, which is why Twitch allegedly stores SHA-256 hashes of plaintext passwords in</p>

<script>
const ed={{erosolar|tojson}}, cd={{complexity|tojson}}, pud={{per_user_data|tojson}};
new Chart(document.getElementById('erosolar'),{type:'bar',data:ed,options:{responsive:true,plugins:{legend:{position:'top'},title:{display:true,text:'For erosolar – a lovely chart by Bo'}}}});
new Chart(document.getElementById('complexity'),{type:'bar',data:cd,options:{responsive:true,plugins:{legend:{position:'top'},title:{display:true,text:'Total Algorithmic Complexity'}}}});
if(pud.labels.length){
new Chart(document.getElementById('peruser'),{type:'bar',data:pud,options:{responsive:true,plugins:{legend:{position:'top'},title:{display:true,text:'Per-User Complexity'}}}});
}
</script>
</body></html>
""", logs=logs, math_json=json.dumps(math,indent=2),
     erosolar=erosolar_data, complexity=complexity_data,
     per_user_data=per_user_data, cost=next_cost)

@app.route('/signup', methods=['POST'])
def signup():
    global next_cost
    cost = int(request.form.get('cost',10) or 10)
    email, pw = request.form['email'].strip(), request.form['pw']
    if not email or not pw: add_log('Signup failed – email and password required'); return redirect(url_for('index'))
    if any(u["email"]==email for u in users): add_log(f'Signup failed – {email} exists'); return redirect(url_for('index'))
    salt = bcrypt.gensalt(rounds=cost)
    h = bcrypt.hashpw(pw.encode(), salt).decode()
    users.append(dict(email=email,salt=salt.decode(),hash=h,len=len(pw)))
    math[email]=parse_bcrypt(h)
    add_log(f'Signup {email} → hash saved (cost={cost})')
    next_cost=cost
    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    email, pw = request.form['email'].strip(), request.form['pw']
    u = next((x for x in users if x["email"]==email), None)
    if not u: add_log(f'Login failed – unknown user {email}'); return redirect(url_for('index'))
    ok = bcrypt.checkpw(pw.encode(), u["hash"].encode())
    add_log(f'Login {u["email"]} with "{pw}" → {"success" if ok else "failure"}')
    return redirect(url_for('index'))

@app.route('/detect_leak', methods=['POST'])
def detect_leak():
    pw = request.form['pw']
    add_log(f'Users in DB: {len(users)}')
    complexity = sum((1 << parse_bcrypt(u["hash"])["cost"]) * u["len"] for u in users)
    add_log(f'Complexity this check: {complexity}')
    found=False
    for u in users:
        h = bcrypt.hashpw(pw.encode(), (u["salt"]).encode()).decode()
        if h==u["hash"]:
            cost=parse_bcrypt(u["hash"])["cost"]; add_log(f'Leak match: "{pw}" for {u["email"]} (cost={cost})'); found=True
    if not found: add_log(f'Leak check: "{pw}" matched no users')
    return redirect(url_for('index'))

@app.route('/auto_setup', methods=['POST'])
def auto_setup():
    for idx,pw in enumerate(['password123','password321']):
        email=f'erosolar_bits_{int(time.time()*1000)}_{idx}@auto.bot'
        cost=int(request.form.get('cost',10) or 10)
        salt=bcrypt.gensalt(rounds=cost)
        h=bcrypt.hashpw(pw.encode(),salt).decode()
        users.append(dict(email=email,salt=salt.decode(),hash=h,len=len(pw)))
        math[email]=parse_bcrypt(h)
        add_log(f'Signup {email} → hash saved (cost={cost})')
        detect_leak_internal(pw)
    return redirect(url_for('index'))

def detect_leak_internal(pw):
    add_log(f'Users in DB: {len(users)}')
    complexity = sum((1 << parse_bcrypt(u["hash"])["cost"]) * u["len"] for u in users)
    add_log(f'Complexity this check: {complexity}')
    found=False
    for u in users:
        h=bcrypt.hashpw(pw.encode(),u["salt"].encode()).decode()
        if h==u["hash"]:
            cost=parse_bcrypt(u["hash"])["cost"]; add_log(f'Leak match: "{pw}" for {u["email"]} (cost={cost})'); found=True
    if not found: add_log(f'Leak check: "{pw}" matched no users')

if __name__=='__main__':
    app.run(debug=True)