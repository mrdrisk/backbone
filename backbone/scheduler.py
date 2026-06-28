import time
import click
from apscheduler.schedulers.blocking import BlockingScheduler
from .config import load_config


def run_scheduled_backup(config_path):
    """Imported lazily to avoid circular imports with cli.py"""
    from .cli import backup
    from click.testing import CliRunner

    runner = CliRunner()
    result = runner.invoke(backup, ["--config", config_path])
    click.echo(result.output)


def start_scheduler(config_path, cron_expression):
    cfg = load_config(config_path)
    scheduler = BlockingScheduler()

    # cron_expression format: "minute hour day month day_of_week"
    # e.g. "0 2 * * *" = every day at 2am
    parts = cron_expression.split()
    if len(parts) != 5:
        raise ValueError("Cron expression must have 5 fields: minute hour day month day_of_week")

    minute, hour, day, month, day_of_week = parts

    scheduler.add_job(
        run_scheduled_backup,
        "cron",
        args=[config_path],
        minute=minute,
        hour=hour,
        day=day,
        month=month,
        day_of_week=day_of_week,
    )

    click.echo(f"Scheduler started. Running backups on schedule: {cron_expression}")
    click.echo("Press Ctrl+C to stop.")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        click.echo("Scheduler stopped.")
