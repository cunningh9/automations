#!/usr/bin/env python3
"""Minecraft Scene Generator — Web UI (Flask)."""

import base64
import io
import os
import sys

# Make sure imports find minecraft_scene.py in the same directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template_string, request, jsonify
from minecraft_scene import BIOMES, TIMES, SPRITES, generate_scene

app = Flask(__name__)

# ── All selectable entities ────────────────────────────────────────────────────
ALL_ENTITIES = sorted(SPRITES.keys())

# ── HTML template ─────────────────────────────────────────────────────────────
HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Minecraft Scene Generator</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    font-family: 'Segoe UI', system-ui, sans-serif;
    background: #1a1a2e;
    color: #e0e0e0;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 32px 16px;
  }

  h1 {
    font-size: 2rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #5cb85c;
    text-shadow: 0 0 16px #3a7a3a;
    margin-bottom: 8px;
  }

  .subtitle {
    color: #888;
    font-size: 0.9rem;
    margin-bottom: 28px;
  }

  .card {
    background: #16213e;
    border: 1px solid #2a3a5e;
    border-radius: 12px;
    padding: 28px 32px;
    width: 100%;
    max-width: 680px;
    margin-bottom: 24px;
  }

  .card h2 {
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #5cb85c;
    margin-bottom: 16px;
  }

  .row {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
    margin-bottom: 20px;
  }

  .field {
    flex: 1;
    min-width: 140px;
  }

  label {
    display: block;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #aaa;
    margin-bottom: 6px;
  }

  select {
    width: 100%;
    padding: 10px 12px;
    background: #0f3460;
    color: #e0e0e0;
    border: 1px solid #2a4a8e;
    border-radius: 6px;
    font-size: 0.95rem;
    cursor: pointer;
    appearance: none;
    -webkit-appearance: none;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath fill='%235cb85c' d='M6 8L0 0h12z'/%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 12px center;
    padding-right: 32px;
  }

  select:focus { outline: none; border-color: #5cb85c; }

  /* Multi-select entity grid */
  .entity-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 4px;
  }

  .entity-chip {
    position: relative;
  }

  .entity-chip input[type=checkbox] {
    display: none;
  }

  .entity-chip label {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 7px 14px;
    background: #0f3460;
    border: 1px solid #2a4a8e;
    border-radius: 20px;
    cursor: pointer;
    font-size: 0.85rem;
    text-transform: capitalize;
    letter-spacing: 0;
    color: #ccc;
    transition: all 0.15s;
    white-space: nowrap;
    user-select: none;
  }

  .entity-chip input[type=checkbox]:checked + label {
    background: #1a5a1a;
    border-color: #5cb85c;
    color: #90ee90;
  }

  .entity-chip label:hover {
    border-color: #5cb85c;
    color: #e0e0e0;
  }

  /* Emoji icons per mob */
  .entity-chip label::before {
    content: attr(data-icon);
    font-size: 1.1em;
  }

  .select-all-row {
    display: flex;
    gap: 10px;
    margin-bottom: 12px;
  }

  .btn-small {
    padding: 4px 12px;
    font-size: 0.78rem;
    background: none;
    border: 1px solid #2a4a8e;
    border-radius: 12px;
    color: #aaa;
    cursor: pointer;
    transition: all 0.15s;
  }
  .btn-small:hover { border-color: #5cb85c; color: #5cb85c; }

  .generate-btn {
    width: 100%;
    max-width: 680px;
    padding: 15px;
    font-size: 1.1rem;
    font-weight: bold;
    text-transform: uppercase;
    letter-spacing: 2px;
    background: #2d6a2d;
    color: #b0ffb0;
    border: none;
    border-radius: 10px;
    cursor: pointer;
    transition: background 0.2s;
    margin-bottom: 28px;
  }

  .generate-btn:hover  { background: #3a8a3a; }
  .generate-btn:active { background: #1e4e1e; }
  .generate-btn:disabled { background: #333; color: #666; cursor: default; }

  .result-card {
    width: 100%;
    max-width: 1280px;
    background: #16213e;
    border: 1px solid #2a3a5e;
    border-radius: 12px;
    padding: 20px;
    display: none;
  }

  .result-card.visible { display: block; }

  .result-meta {
    font-size: 0.82rem;
    color: #aaa;
    margin-bottom: 12px;
    letter-spacing: 0.5px;
  }

  .result-meta span { color: #5cb85c; font-weight: bold; }

  .result-card img {
    width: 100%;
    height: auto;
    border-radius: 6px;
    image-rendering: pixelated;
    image-rendering: crisp-edges;
  }

  .spinner {
    display: none;
    text-align: center;
    color: #5cb85c;
    font-size: 0.9rem;
    margin-bottom: 20px;
  }
  .spinner.visible { display: block; }

  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
  .spinner span { animation: pulse 1.2s infinite; }
</style>
</head>
<body>

<h1>⛏ Minecraft Scene Generator</h1>
<p class="subtitle">Procedural pixel-art world builder</p>

<div class="card">
  <h2>World Settings</h2>
  <div class="row">
    <div class="field">
      <label for="biome">Biome</label>
      <select id="biome" name="biome">
        <option value="random">🎲 Random</option>
        {% for b in biomes %}
        <option value="{{ b }}">{{ b.capitalize() }}</option>
        {% endfor %}
      </select>
    </div>
    <div class="field">
      <label for="tod">Time of Day</label>
      <select id="tod" name="tod">
        <option value="random">🎲 Random</option>
        {% for t in times %}
        <option value="{{ t }}">{{ t.capitalize() }}</option>
        {% endfor %}
      </select>
    </div>
  </div>
</div>

<div class="card">
  <h2>Entities to Include</h2>
  <div class="select-all-row">
    <button class="btn-small" onclick="setAll(true)">Select All</button>
    <button class="btn-small" onclick="setAll(false)">Clear All</button>
    <button class="btn-small" onclick="setRandom()">Random Mix</button>
  </div>
  <div class="entity-grid" id="entityGrid">
    {% for mob in entities %}
    <div class="entity-chip">
      <input type="checkbox" id="mob_{{ mob }}" value="{{ mob }}" checked>
      <label for="mob_{{ mob }}" data-icon="{{ icons[mob] }}">{{ mob }}</label>
    </div>
    {% endfor %}
  </div>
</div>

<button class="generate-btn" id="genBtn" onclick="generate()">Generate Scene</button>

<div class="spinner" id="spinner"><span>Generating scene…</span></div>

<div class="result-card" id="resultCard">
  <div class="result-meta" id="resultMeta"></div>
  <img id="resultImg" src="" alt="Generated scene">
  <a id="downloadBtn" href="#" download="scene.png" style="display:none; margin-top:14px; display:none;">
    <button class="btn-small" style="padding:8px 18px; font-size:0.9rem;">⬇ Download PNG</button>
  </a>
</div>

<script>
const MOB_ICONS = {{ icons_json | safe }};

function setAll(v) {
  document.querySelectorAll('#entityGrid input[type=checkbox]')
    .forEach(cb => cb.checked = v);
}

function setRandom() {
  document.querySelectorAll('#entityGrid input[type=checkbox]')
    .forEach(cb => cb.checked = Math.random() > 0.5);
}

async function generate() {
  const btn = document.getElementById('genBtn');
  const spinner = document.getElementById('spinner');
  const resultCard = document.getElementById('resultCard');

  const selected = Array.from(
    document.querySelectorAll('#entityGrid input[type=checkbox]:checked')
  ).map(cb => cb.value);

  if (selected.length === 0) {
    alert('Please select at least one entity.');
    return;
  }

  btn.disabled = true;
  spinner.classList.add('visible');
  resultCard.classList.remove('visible');

  try {
    const resp = await fetch('/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        biome: document.getElementById('biome').value,
        tod: document.getElementById('tod').value,
        entities: selected
      })
    });
    const data = await resp.json();

    if (data.error) {
      alert('Error: ' + data.error);
      return;
    }

    const imgSrc = 'data:image/png;base64,' + data.image;
    document.getElementById('resultImg').src = imgSrc;
    document.getElementById('resultMeta').innerHTML =
      `Biome: <span>${data.biome.toUpperCase()}</span> &nbsp;|&nbsp; ` +
      `Time: <span>${data.tod.toUpperCase()}</span> &nbsp;|&nbsp; ` +
      `Entities: <span>${data.mobs}</span>`;
    const dl = document.getElementById('downloadBtn');
    dl.href = imgSrc;
    dl.download = data.filename;
    dl.style.display = 'inline-block';
    resultCard.classList.add('visible');
    resultCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
  } catch (err) {
    alert('Request failed: ' + err);
  } finally {
    btn.disabled = false;
    spinner.classList.remove('visible');
  }
}
</script>
</body>
</html>
"""

# Emoji icons for each mob
MOB_ICONS = {
    "steve":     "🧑",
    "creeper":   "💚",
    "zombie":    "🧟",
    "skeleton":  "💀",
    "enderman":  "👁️",
    "villager":  "👳",
    "pig":       "🐷",
    "cow":       "🐄",
    "chicken":   "🐔",
    "spider":    "🕷️",
}

import json

@app.route("/")
def index():
    icons = {mob: MOB_ICONS.get(mob, "◼") for mob in ALL_ENTITIES}
    return render_template_string(
        HTML,
        biomes=BIOMES,
        times=TIMES,
        entities=ALL_ENTITIES,
        icons=icons,
        icons_json=json.dumps(icons),
    )


@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.get_json()
        biome    = data.get("biome")   or None
        tod      = data.get("tod")     or None
        entities = data.get("entities") or None

        if biome == "random":
            biome = None
        if tod == "random":
            tod = None

        img, path, used_biome, used_tod, mobs = generate_scene(
            biome=biome,
            tod=tod,
            forced_entities=entities if entities else None,
        )

        # Encode image as base64 to send inline
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        b64 = base64.b64encode(buf.read()).decode()

        return jsonify({
            "image":    b64,
            "biome":    used_biome,
            "tod":      used_tod,
            "mobs":     mobs,
            "filename": os.path.basename(path),
        })
    except Exception as exc:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    import socket, subprocess, threading, time

    port = int(os.environ.get("PORT", 5555))

    # Resolve LAN IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        lan_ip = s.getsockname()[0]
        s.close()
    except Exception:
        lan_ip = "127.0.0.1"

    def open_chrome():
        time.sleep(0.9)
        url = f"http://127.0.0.1:{port}"
        subprocess.run(
            ["open", "-a", "Google Chrome", url],
            check=False
        )

    threading.Thread(target=open_chrome, daemon=True).start()

    print(f"\n  ⛏  Minecraft Scene Generator")
    print(f"  Local  → http://127.0.0.1:{port}")
    print(f"  LAN    → http://{lan_ip}:{port}  (use this on iOS)\n")

    app.run(host="0.0.0.0", port=port, debug=False)
