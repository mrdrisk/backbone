import os
import glob


def apply_retention(target, keep_last=5, max_age_days=None):
    """Deletes old local backups for a target, keeping only the most
    recent `keep_last` files (and optionally enforcing a max age in days)."""
    pattern = os.path.join(target["destination"], f"{target['name']}-*")
    matches = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)

    deleted = []

    # Enforce max count
    for old_file in matches[keep_last:]:
        os.remove(old_file)
        deleted.append(old_file)

    # Enforce max age, if specified
    if max_age_days:
        import time
        cutoff = time.time() - (max_age_days * 86400)
        remaining = matches[:keep_last]
        for f in remaining:
            if os.path.getmtime(f) < cutoff and f not in deleted:
                os.remove(f)
                deleted.append(f)

    return deleted
