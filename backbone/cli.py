import click
from .config import load_config
from .backup import run_backup


@click.group()
def cli():
    """Backbone - a simple backup-and-restore orchestrator."""
    pass


@cli.command()
@click.option("--config", default="config.yaml", help="Path to config YAML file")
def backup(config):
    """Run backups for all targets defined in the config file."""
    cfg = load_config(config)
    for target in cfg["targets"]:
        click.echo(f"Backing up '{target['name']}' ({target['type']})...")
        try:
            path = run_backup(target)
            click.echo(click.style(f"  -> Success: {path}", fg="green"))
        except Exception as e:
            click.echo(click.style(f"  -> Failed: {e}", fg="red"))


if __name__ == "__main__":
    cli()