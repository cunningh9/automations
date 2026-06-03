# Minecraft Scene Generator

A procedural pixel-art Minecraft scene generator with a Flask web UI.

## Features

- Choose biome, time of day, and entities to include
- Generates a pixel-art scene image on demand
- Randomize options for variety

## Run locally

```bash
pip install -r requirements.txt
python web_app.py
```

Opens automatically at `http://127.0.0.1:5555`.

## Deploy to Render

1. Push this repo to GitHub
2. Create a new **Web Service** on [render.com](https://render.com) and connect the repo
3. Set the start command to:
   ```
   gunicorn web_app:app
   ```
4. Render will install dependencies from `requirements.txt` automatically

Generated scenes are saved to `/tmp/minecraft_scenes/` (cleared on restart).
