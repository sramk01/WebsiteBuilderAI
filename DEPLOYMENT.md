# Deploying This to a Server

This app has no accounts, database, or billing — hosting it just means
running the same Flask app on a machine other than your laptop, reachable
by URL. Three options below, easiest first.

---

## Option A — Render.com (easiest, no server admin, free tier)

Best if you don't want to manage a server at all.

1. Push this `webgen/` folder to a GitHub repo (create one if you don't
   have one: `git init`, `git add .`, `git commit -m "init"`, push to a new
   GitHub repo).
2. Go to https://render.com → New → Web Service → connect that repo.
3. Render auto-detects the `Dockerfile` in this folder — just confirm and
   deploy. (If it asks for a start command instead of using the
   Dockerfile, use: `gunicorn --bind 0.0.0.0:$PORT app:app`)
4. Optional: under Environment, add `ANTHROPIC_API_KEY` if you want a
   server-wide fallback AI key (users can also just paste their own key
   into the wizard each time — that always takes priority).
5. Render gives you a public `https://your-app.onrender.com` URL — done.

No Docker knowledge needed; Render builds the image for you from the
Dockerfile already in this project.

---

## Option B — Any VPS with Docker (DigitalOcean, Linode, Hetzner, AWS Lightsail, etc.)

Best if you already have (or want) your own server and full control.

1. Spin up a small Linux VPS (Ubuntu 22.04+ is a safe default). $4-6/month
   tiers are plenty for this tool.
2. SSH in, install Docker:
   ```bash
   curl -fsSL https://get.docker.com | sh
   ```
3. Copy this `webgen/` folder to the server (e.g. `scp -r webgen you@your-server-ip:~/`
   or clone your GitHub repo there with `git clone ...`).
4. From inside the folder:
   ```bash
   cd webgen
   docker compose up -d --build
   ```
5. Your app is now running on port 8000. Visit `http://your-server-ip:8000`.
6. **To use a real domain + HTTPS**, put Nginx in front of it:
   ```bash
   sudo apt install nginx certbot python3-certbot-nginx
   ```
   Create `/etc/nginx/sites-available/webgen`:
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```
   Then:
   ```bash
   sudo ln -s /etc/nginx/sites-available/webgen /etc/nginx/sites-enabled/
   sudo nginx -t && sudo systemctl reload nginx
   sudo certbot --nginx -d yourdomain.com   # free HTTPS certificate
   ```
7. Point your domain's DNS A record at the server's IP. Done — your site
   is now live at `https://yourdomain.com` with a valid SSL certificate,
   and `docker compose up -d` means it restarts automatically on reboot.

To update after making changes: `git pull && docker compose up -d --build`.

---

## Option C — Bare VPS without Docker (gunicorn + systemd)

Same idea as Option B, but running Python directly instead of in a
container — use this if you'd rather not install Docker.

```bash
sudo apt install python3-pip python3-venv
git clone <your-repo-url> webgen && cd webgen
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create `/etc/systemd/system/webgen.service`:
```ini
[Unit]
Description=Landing Page Generator
After=network.target

[Service]
User=www-data
WorkingDirectory=/home/you/webgen
Environment="PATH=/home/you/webgen/venv/bin"
ExecStart=/home/you/webgen/venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 2 --timeout 120 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable --now webgen
```

Then set up Nginx + certbot exactly as in Option B, step 6.

---

## What's actually running in production vs. what you had locally

- Locally you ran `python app.py --port 8000` — Flask's built-in dev
  server. That's fine for your own machine but explicitly not meant to
  face the internet (it says so in its own warning message).
- In all three options above, **Gunicorn** runs the app instead — a real
  production WSGI server. Nothing about the app's code changes; Gunicorn
  just imports the same `app` object from `app.py` and serves it properly
  (multiple worker processes, no debug/reloader, no `Only one usage of
  each socket address` issue since there's no reloader involved at all).

## Security notes for a public deployment

- There's still no login system — anyone with the URL can generate sites
  and use your AI key if you set one server-wide. If that's a concern,
  put it behind a simple HTTP Basic Auth rule in Nginx, or just don't set
  a server-side `ANTHROPIC_API_KEY` and let each user paste their own.
- Uploaded images are capped at ~8MB each (`MAX_CONTENT_LENGTH` in
  `app.py`) — lower this if you want tighter limits on a public server.
- Generated job files are written to the OS temp directory and deleted
  right after the zip is sent — nothing persists between requests.
