import os
import click
from dotenv import load_dotenv
from .config import load_config
from .backup import run_backup
from .encrypt import encrypt_file
from .remote import upload_file

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


if __name__ == "__main__":
    cli()
