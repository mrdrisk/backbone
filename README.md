# Backbone

![CI](https://github.com/mrdrisk/backbone/actions/workflows/ci.yml/badge.svg)

A simple, self-hostable backup tool for your homelab. Backbone automatically backs up your files, Docker volumes, and databases, encrypts them so only you can read them, and uploads them to cloud storage — all on a schedule, with a Discord notification when it's done.

Named after the Gojira song from their album *From Mars to Sirius*.

## Why this exists

If you're running anything at home — a Docker app, a small database, a folder of files you care about — eventually you'll lose something to a bad update, a dead drive, or a fat-fingered `rm -rf`. Backbone exists so that doesn't have to be a disaster: it takes regular, encrypted, off-site backups automatically, and gives you a one-command way to restore.

## What it does

- 📁 Backs up directories, Docker volumes, Postgres databases, and SQLite databases
- 🔒 Encrypts every backup with [age](https://github.com/FiloSottile/age) before it ever leaves your machine
- ☁️ Uploads encrypted backups to Backblaze B2 (or any S3-compatible storage)
- ⏰ Runs automatically on a schedule you define
- ♻️ One-command restore when something goes wrong
- 🔔 Sends a Discord notification after every run
- 🧹 Automatically cleans up old backups so storage doesn't grow forever

## How it works (the short version)

1. You tell Backbone what to back up in a simple config file
2. It copies/dumps that data into a compressed archive
3. It encrypts the archive with a key only you hold
4. It uploads the encrypted archive to cloud storage
5. It deletes old backups beyond however many you want to keep
6. It posts a summary to Discord

If something breaks later, you run one command and Backbone decrypts and restores the most recent backup for you.

## Getting started

### Things you'll need

- [Python 3.10+](https://www.python.org/downloads/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (only needed if you're backing up Docker volumes, Postgres, etc.)
- A free [Backblaze B2](https://www.backblaze.com/cloud-storage) account for off-site storage
- [age](https://github.com/FiloSottile/age) for encryption — install instructions below
- (Optional) A Discord server and webhook for notifications

### 1. Clone the repo

```bash
git clone https://github.com/mrdrisk/backbone.git
cd backbone
```

### 2. Set up a Python virtual environment

This keeps Backbone's dependencies separate from everything else on your system.

**Windows (Git Bash):**
```bash
python -m venv venv
source venv/Scripts/activate
```

**macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

You'll know it worked if you see `(venv)` appear at the start of your terminal prompt. You'll need to run the `source` command again every time you open a new terminal and want to use Backbone.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install age (for encryption)

**Windows:**
```powershell
winget install --id FiloSottile.age -e
```

**macOS:**
```bash
brew install age
```

**Linux:**
```bash
sudo apt install age
```

Close and reopen your terminal afterward, then confirm it worked:
```bash
age --version
```

### 5. Generate your encryption key

```bash
age-keygen -o backbone-key.txt
```

This creates a private key file (`backbone-key.txt`) and prints a public key starting with `age1...` — copy that public key, you'll need it in a minute.

**Keep `backbone-key.txt` safe and private.** It's the only thing that can decrypt your backups. If you lose it, your backups become unreadable. It's already excluded from git so it never gets accidentally uploaded anywhere.

### 6. Set up cloud storage (Backblaze B2)

1. Sign up at [backblaze.com](https://www.backblaze.com/cloud-storage) (free tier: 10GB)
2. Create a **private** bucket
3. Go to **App Keys** → create a new key scoped to that bucket
4. Note down the **keyID**, **applicationKey**, and the bucket's **Endpoint** URL

### 7. Set up Discord notifications (optional)

1. Create a Discord server (or use one you already have)
2. Right-click a channel → **Edit Channel** → **Integrations** → **Webhooks** → **New Webhook**
3. Copy the webhook URL

### 8. Configure your environment

```bash
cp .env.example .env
```

Open `.env` and fill in your real values:

```env
B2_KEY_ID=your-key-id-here
B2_APPLICATION_KEY=your-application-key-here
B2_BUCKET_NAME=your-bucket-name
B2_ENDPOINT_URL=https://s3.us-east-005.backblazeb2.com
AGE_PUBLIC_KEY=age1yourpublickeyhere
AGE_KEY_FILE=backbone-key.txt
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your-webhook-here
```

### 9. Configure what to back up

```bash
cp config.example.yaml config.yaml
```

Open `config.yaml` and edit it to match what you actually want backed up. Example:

```yaml
targets:
  - name: my-app-data
    type: directory          # directory | volume | postgres | sqlite
    source: ./my-app-data
    destination: ./backups
    retention:
      keep_last: 5           # only keep the 5 most recent backups

  - name: my-database
    type: postgres
    source: my_database_name
    host: localhost
    port: 5432
    user: postgres
    password: ${DB_PASSWORD}
    destination: ./backups
    retention:
      keep_last: 3

remote:
  enabled: true
  bucket: your-bucket-name
  encrypt: true
```

## Running Backbone

### Run a backup right now

```bash
python -m backbone.cli backup --config config.yaml
```

### Restore a backup

Restore the most recent backup for a target:
```bash
python -m backbone.cli restore --config config.yaml --target my-app-data
```

Restore from a specific local file:
```bash
python -m backbone.cli restore --config config.yaml --target my-app-data --file ./backups/my-app-data-20260628-165400.tar.gz.age
```

Restore by downloading from cloud storage first:
```bash
python -m backbone.cli restore --config config.yaml --target my-app-data --from-remote --file my-app-data-20260628-165400.tar.gz.age
```

### Run backups automatically on a schedule

```bash
python -m backbone.cli schedule --config config.yaml --cron "0 2 * * *"
```

This runs Backbone in the foreground and triggers a backup according to the cron schedule you give it. The format is `minute hour day month day_of_week` — `"0 2 * * *"` means "every day at 2am". Leave the terminal window open (or run it inside something like `tmux`/`screen`, or as a background service) for it to keep working.

## Running with Docker

If you don't want to install Python and dependencies directly on your machine, you can run Backbone entirely inside Docker instead.

**Build the image:**
```bash
docker build -t backbone .
```

**Run a backup:**
```bash
docker run --rm \
  -v $(pwd)/config.yaml:/app/config.yaml \
  -v $(pwd)/.env:/app/.env \
  -v $(pwd)/backbone-key.txt:/app/backbone-key.txt \
  -v $(pwd)/backups:/app/backups \
  backbone backup --config config.yaml
```

## Project status

All planned milestones are complete:

- [x] Local backup engine (directories + Docker volumes)
- [x] Encryption (age) + remote storage (Backblaze B2)
- [x] Postgres/SQLite-aware backups
- [x] Scheduling + restore command
- [x] Discord notifications + retention policy
- [x] Dockerized CLI + CI pipeline

## A note on security

- Your private encryption key (`backbone-key.txt`) and `.env` file are never committed to git — keep them backed up somewhere separate from your actual backups (a password manager or an offline USB drive works well)
- Backups are encrypted *before* they're uploaded, so even if your cloud storage account were ever compromised, your data stays unreadable without your private key
