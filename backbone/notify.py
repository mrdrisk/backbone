import os
import requests


def send_discord_notification(message, success=True):
    """Sends a message to the configured Discord webhook."""
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        return  # silently skip if not configured

    color = 3066993 if success else 15158332  # green or red

    payload = {
        "embeds": [
            {
                "title": "Backbone Backup Report",
                "description": message,
                "color": color,
            }
        ]
    }

    try:
        requests.post(webhook_url, json=payload, timeout=10)
    except Exception:
        pass  # don't let notification failures break the backup run
