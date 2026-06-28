import os
import subprocess
import tarfile
import shutil
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


def backup_postgres(target):
    """Dumps a Postgres database using pg_dump (run inside a throwaway
    container if the DB itself is in a container, otherwise locally)."""
    os.makedirs(target["destination"], exist_ok=True)
    archive_name = f"{target['name']}-{_timestamp()}.sql"
    dump_path = os.path.join(target["destination"], archive_name)

    host = target.get("host", "localhost")
    port = target.get("port", 5432)
    user = target.get("user", "postgres")
    password = target.get("password", "")
    db_name = target["source"]

    env = os.environ.copy()
    if password:
        env["PGPASSWORD"] = password

    cmd = [
        "pg_dump",
        "-h", host,
        "-p", str(port),
        "-U", user,
        "-d", db_name,
        "-f", dump_path,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        raise RuntimeError(f"pg_dump failed: {result.stderr}")

    # Compress the SQL dump
    archive_path = f"{dump_path}.tar.gz"
    with tarfile.open(archive_path, "w:gz") as tar:
        tar.add(dump_path, arcname=os.path.basename(dump_path))
    os.remove(dump_path)

    return archive_path


def backup_sqlite(target):
    """Creates a safe, consistent snapshot of a SQLite DB file using the
    sqlite3 .backup command, then compresses it."""
    os.makedirs(target["destination"], exist_ok=True)
    snapshot_name = f"{target['name']}-{_timestamp()}.db"
    snapshot_path = os.path.join(target["destination"], snapshot_name)

    cmd = ["sqlite3", target["source"], f".backup '{snapshot_path}'"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"SQLite backup failed: {result.stderr}")

    archive_path = f"{snapshot_path}.tar.gz"
    with tarfile.open(archive_path, "w:gz") as tar:
        tar.add(snapshot_path, arcname=os.path.basename(snapshot_path))
    os.remove(snapshot_path)

    return archive_path


def run_backup(target):
    if target["type"] == "directory":
        return backup_directory(target)
    elif target["type"] == "volume":
        return backup_volume(target)
    elif target["type"] == "postgres":
        return backup_postgres(target)
    elif target["type"] == "sqlite":
        return backup_sqlite(target)
    else:
        raise NotImplementedError(f"Backup type '{target['type']}' not implemented")


def restore_directory(archive_path, target):
    """Extracts a directory archive to its original source location
    (or a custom destination if provided)."""
    dest = target.get("restore_to", os.path.dirname(target["source"]) or ".")
    with tarfile.open(archive_path, "r:gz") as tar:
        tar.extractall(path=dest)
    return dest


def restore_volume(archive_path, target):
    """Restores a tar.gz archive into a Docker volume."""
    archive_abs = os.path.abspath(archive_path)
    archive_dir = os.path.dirname(archive_abs)
    archive_name = os.path.basename(archive_abs)

    cmd = [
        "docker", "run", "--rm",
        "-v", f"{target['source']}:/data",
        "-v", f"{archive_dir}:/backup",
        "alpine",
        "tar", "xzf", f"/backup/{archive_name}", "-C", "/data"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Docker restore failed: {result.stderr}")
    return target["source"]


def restore_postgres(archive_path, target):
    """Extracts a .sql.tar.gz dump and restores it with psql."""
    extract_dir = os.path.dirname(archive_path)
    with tarfile.open(archive_path, "r:gz") as tar:
        tar.extractall(path=extract_dir)
        sql_filename = tar.getnames()[0]
    sql_path = os.path.join(extract_dir, sql_filename)

    host = target.get("host", "localhost")
    port = target.get("port", 5432)
    user = target.get("user", "postgres")
    password = target.get("password", "")
    db_name = target["source"]

    env = os.environ.copy()
    if password:
        env["PGPASSWORD"] = password

    cmd = ["psql", "-h", host, "-p", str(port), "-U", user, "-d", db_name, "-f", sql_path]
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        raise RuntimeError(f"psql restore failed: {result.stderr}")

    os.remove(sql_path)
    return db_name


def restore_sqlite(archive_path, target):
    """Extracts a .db.tar.gz snapshot and copies it over the target source."""
    extract_dir = os.path.dirname(archive_path)
    with tarfile.open(archive_path, "r:gz") as tar:
        tar.extractall(path=extract_dir)
        db_filename = tar.getnames()[0]
    extracted_db_path = os.path.join(extract_dir, db_filename)

    dest = target.get("restore_to", target["source"])
    shutil.copy2(extracted_db_path, dest)
    os.remove(extracted_db_path)
    return dest


def run_restore(archive_path, target):
    if target["type"] == "directory":
        return restore_directory(archive_path, target)
    elif target["type"] == "volume":
        return restore_volume(archive_path, target)
    elif target["type"] == "postgres":
        return restore_postgres(archive_path, target)
    elif target["type"] == "sqlite":
        return restore_sqlite(archive_path, target)
    else:
        raise NotImplementedError(f"Restore type '{target['type']}' not implemented")
