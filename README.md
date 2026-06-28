# Backbone

A simple, self-hostable backup-and-restore orchestrator for Docker volumes and directories. Named after the Gojira song from their acclaimed album From Mars to Sirius.

## Status

Milestone 1: local backup engine (directory + Docker volume support). Encryption, remote storage (S3/B2), database-aware backups, scheduling, and restore commands are coming in later milestones.

## Quick start

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp config.example.yaml config.yaml
# edit config.yaml with your actual targets

python -m backbone.cli backup --config config.yaml
```

## Roadmap

- [x] Local backup engine (directory + volume)
- [x] Encryption + S3/B2 upload
- [x] Postgres/SQLite-aware backups
- [ ] Scheduling + restore command
- [ ] Notifications + retention policy
- [ ] Dockerized CLI + CI pipeline
