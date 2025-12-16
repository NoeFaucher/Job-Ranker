import yaml
from pathlib import Path
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Job Finder - Job Search and AI sorting tool"
    )
    parser.add_argument(
        "--process-only",
        "-p",
        action="store_true",
        help="Process existing jobs without scraping (text preprocessing and distance calculation only)"
    )
    parser.add_argument(
        "--config",
        "-c",
        type=str,
        required=True,
        help="Path to your YAML configuration file"
    )

    # Optional overrides
    parser.add_argument("--search_term", type=str, help="Override: job search term")
    parser.add_argument("--location", type=str, help="Override: job search location")
    parser.add_argument("--results_wanted", type=int, help="Override: number of results")

    return parser.parse_args()

def load_yaml_config(path: str) -> dict:
    config_path = Path(path)

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def merge_config(base_config: dict, args: argparse.Namespace) -> dict:
    if "search" not in base_config:
        base_config["search"] = {}

    # CLI overrides only for user-facing parameters
    if args.search_term:
        base_config["search"]["search_term"] = args.search_term
    if args.location:
        base_config["search"]["location"] = args.location

    # Required defaults if missing
    base_config["search"].setdefault("site_name", ["linkedin"])
    base_config["search"].setdefault("country_indeed", "france")
    base_config["search"].setdefault("hours_old", 1000)

    # filtering + ai left unchanged
    base_config.setdefault("filtering", {})

    return base_config

def validate_config(config: dict):
    required_search_fields = ["search_term", "locations"]

    for field in required_search_fields:
        if field not in config["search"]:
            raise ValueError(f"Missing required field in config.search: {field}")

def load_config(args):

    yaml_config = load_yaml_config(args.config)
    final_config = merge_config(yaml_config, args)

    validate_config(final_config)

    return final_config
