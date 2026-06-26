import yaml
import os

REQUIRED_TARGET_FIELDS = ["name", "type", "source", "destination"]
VALID_TYPES = ["volume", "directory", "postgres", "sqlite"]


def load_config(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(path, "r") as f:
        config = yaml.safe_load(f)

    if not config or "targets" not in config:
        raise ValueError("Config must contain a 'targets' list")

    for target in config["targets"]:
        for field in REQUIRED_TARGET_FIELDS:
            if field not in target:
                raise ValueError(f"Target missing required field '{field}': {target}")
        if target["type"] not in VALID_TYPES:
            raise ValueError(
                f"Invalid type '{target['type']}' for target '{target['name']}'. "
                f"Must be one of {VALID_TYPES}"
            )

    return config