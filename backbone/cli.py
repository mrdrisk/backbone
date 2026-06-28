import os
import glob
import click
from dotenv import load_dotenv
from .config import load_config
from .backup import run_backup, run_restore
from .encrypt import encrypt_file, decrypt_file
from .remote import upload_file, download_file

load_dotenv()


@click.group()
def cli():
    """Backbone - a simple backup-and-restore orchestrator."""
    pass


@cli.command()
@click.option("--config", default="config.yaml", help="Path to config YAML file")
def backup(config):
    """Run backups for all targets defined in the config file."""
    cfg = load_config(config)
    remote_cfg = cfg.get("remote", {})

    for target in cfg["targets"]:
        click.echo(f"Backing up '{target['name']}' ({target['type']})...")
        try:
            path = run_backup(target)
            click.echo(click.style(f"  -> Local backup: {path}", fg="green"))

            if remote_cfg.get("encrypt"):
                public_key = os.environ.get("AGE_PUBLIC_KEY")
                if not public_key:
                    raise RuntimeError("AGE_PUBLIC_KEY not set in .env")
                path = encrypt_file(path, public_key)
                click.echo(click.style(f"  -> Encrypted: {path}", fg="green"))

            if remote_cfg.get("enabled"):
                remote_path = upload_file(path, remote_cfg.get("bucket"))
                click.echo(click.style(f"  -> Uploaded: {remote_path}", fg="green"))

        except Exception as e:
            click.echo(click.style(f"  -> Failed: {e}", fg="red"))


@cli.command()
@click.option("--config", default="config.yaml", help="Path to config YAML file")
@click.option("--target", required=True, help="Name of the target to restore")
@click.option("--from-remote", is_flag=True, help="Download the latest backup from remote storage first")
@click.option("--file", default=None, help="Specific local backup file to restore from (skips auto-detection)")
def restore(config, target, from_remote, file):
    """Restore a target from its most recent local or remote backup."""
    cfg = load_config(config)
    remote_cfg = cfg.get("remote", {})

    target_cfg = next((t for t in cfg["targets"] if t["name"] == target), None)
    if not target_cfg:
        click.echo(click.style(f"No target named '{target}' found in config", fg="red"))
        return

    backup_path = file

    if from_remote:
        if not file:
            click.echo(click.style("--from-remote requires --file (the remote key/filename to download)", fg="red"))
            return
        local_path = os.path.join(target_cfg["destination"], os.path.basename(file))
        click.echo(f"Downloading '{file}' from remote...")
        download_file(file, local_path, remote_cfg.get("bucket"))
        backup_path = local_path

    if not backup_path:
        # Auto-detect the most recent local backup for this target
        pattern = os.path.join(target_cfg["destination"], f"{target}-*")
        matches = sorted(glob.glob(pattern), reverse=True)
        if not matches:
            click.echo(click.style(f"No local backups found for '{target}'", fg="red"))
            return
        backup_path = matches[0]

    click.echo(f"Restoring '{target}' from: {backup_path}")

    try:
        # Decrypt if needed
        if backup_path.endswith(".age"):
            identity_file = os.environ.get("AGE_KEY_FILE", "backbone-key.txt")
            decrypted_path = backup_path[:-4]  # strip .age
            decrypt_file(backup_path, identity_file, decrypted_path)
            click.echo(click.style(f"  -> Decrypted: {decrypted_path}", fg="green"))
            backup_path = decrypted_path

        result = run_restore(backup_path, target_cfg)
        click.echo(click.style(f"  -> Restored successfully to: {result}", fg="green"))

    except Exception as e:
        click.echo(click.style(f"  -> Failed: {e}", fg="red"))

@cli.command()
@click.option("--config", default="config.yaml", help="Path to config YAML file")
@click.option("--cron", required=True, help="Cron expression: 'minute hour day month day_of_week' (e.g. '0 2 * * *' for daily at 2am)")
def schedule(config, cron):
    """Start a scheduler that runs backups automatically on a cron schedule."""
    from .scheduler import start_scheduler
    start_scheduler(config, cron)

if __name__ == "__main__":
    cli()
