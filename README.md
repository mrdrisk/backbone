# Backbone

A simple, self-hostable backup-and-restore orchestrator for Docker volumes, directories, and databases. Named after the Gojira song from their acclaimed album From Mars to Sirius.

## Features

- Back up directories and Docker volumes
- Back up Postgres databases (via `pg_dump`) and SQLite databases (via `.backup`)
- Encrypt backups with `age` before they ever leave your machine
- Upload encrypted backups to Backblaze B2 (S3-compatible storage)
- Simple YAML-based config for defining backup targets

## Status

Milestones 1-5 complete: local backups, encryption + remote storage, database-aware backups, scheduling, restore, Discord notifications, and retention policy are all working end-to-end. Containerization and a CI pipeline (Milestone 6) are still in progress.

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

## Restoring a backup

Restore a target from its most recent local backup:
```bash
python -m backbone.cli restore --config config.yaml --target my-app-data
```

Restore from a specific local file:
```bash
python -m backbone.cli restore --config config.yaml --target my-app-data --file ./backups/my-app-data-20260628-165400.tar.gz.age
```

Restore by downloading from remote storage first:
```bash
python -m backbone.cli restore --config config.yaml --target my-app-data --from-remote --file my-app-data-20260628-165400.tar.gz.age
```

## Scheduling automatic backups

Run backups on a recurring cron schedule (stays running in the foreground):
```bash
python -m backbone.cli schedule --config config.yaml --cron "0 2 * * *"
```

Cron format: `minute hour day month day_of_week`. Example: `"0 2 * * *"` runs daily at 2am.

## Roadmap

- [x] Local backup engine (directory + volume)
- [x] Encryption (age) + remote storage (Backblaze B2)
- [x] Postgres/SQLite-aware backups
- [x] Scheduling + restore command
- [x] Notifications + retention policy
- [ ] Dockerized CLI + CI pipeline
