# Backbone

A simple, self-hostable backup-and-restore orchestrator for Docker volumes, directories, and databases. Named after the Gojira song from their acclaimed album From Mars to Sirius.

## Features

- Back up directories and Docker volumes
- Back up Postgres databases (via `pg_dump`) and SQLite databases (via `.backup`)
- Encrypt backups with `age` before they ever leave your machine
- Upload encrypted backups to Backblaze B2 (S3-compatible storage)
- Simple YAML-based config for defining backup targets

## Status

Milestones 1-3 complete: local backups, encryption + remote storage, and database-aware backups are all working end-to-end. Scheduling, a restore command, notifications, retention policy, and containerization are still in progress.

## Quick start

```bash
python -m venv venv
source venv/Scripts/activate   # Windows (Git Bash)
# source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt

cp config.example.yaml config.yaml
# edit config.yaml with your actual targets

cp .env.example .env
# fill in your B2 credentials and age public key in .env
```

Run a backup:
```bash
python -m backbone.cli backup --config config.yaml
```

## Configuration

Each target in `config.yaml` defines what to back up:

```yaml
targets:
  - name: my-app-data
    type: directory        # directory | volume | postgres | sqlite
    source: ./test-data
    destination: ./backups

  - name: my-db
    type: postgres
    source: my_database_name
    host: localhost
    port: 5432
    user: postgres
    password: ${DB_PASSWORD}
    destination: ./backups

remote:
  enabled: true
  bucket: your-b2-bucket-name
  encrypt: true
```

## Roadmap

- [x] Local backup engine (directory + volume)
- [x] Encryption (age) + remote storage (Backblaze B2)
- [x] Postgres/SQLite-aware backups
- [ ] Scheduling + restore command
- [ ] Notifications + retention policy
- [ ] Dockerized CLI + CI pipeline
