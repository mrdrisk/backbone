import os
import subprocess
import tarfile
from datetime import datetime


def _timestamp():
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def backup_directory(target):
    os.makedirs(target["destination"], exist_ok=True)
    archive_name = f"{target['name']}-{_timestamp()}.tar.gz"
    archive_path = os.path.join(target["destination"], archive_name)

    with tarfile.open(archive_path, "w:gz") as tar:
        tar.add(target["source"], arcname=os.path.basename(target["source"]))

    return archive_path


def backup_volume(target):
    os.makedirs(target["destination"], exist_ok=True)
    archive_name = f"{target['name']}-{_timestamp()}.tar.gz"
    dest_abs = os.path.abspath(target["destination"])

    cmd = [
        "docker", "run", "--rm",
        "-v", f"{target['source']}:/data:ro",
        "-v", f"{dest_abs}:/backup",
        "alpine",
        "tar", "czf", f"/backup/{archive_name}", "-C", "/data", "."
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Docker backup failed: {result.stderr}")

    return os.path.join(target["destination"], archive_name)


def run_backup(target):
    if target["type"] == "directory":
        return backup_directory(target)
    elif target["type"] == "volume":
        return backup_volume(target)
    else:
        raise NotImplementedError(
            f"Backup type '{target['type']}' not implemented yet (coming in a later milestone)"
        )