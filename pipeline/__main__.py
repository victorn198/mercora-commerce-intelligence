from __future__ import annotations

import argparse

from .build import build_database
from .capture import capture_screenshots
from .config import Settings
from .download import download_dataset
from .package import build_deploy_package
from .validate import run_validation


def main() -> None:
    parser = argparse.ArgumentParser(description="Olist analytics pipeline")
    subparsers = parser.add_subparsers(dest="command", required=True)
    download_parser = subparsers.add_parser("download")
    download_parser.add_argument("--force", action="store_true")
    subparsers.add_parser("build")
    subparsers.add_parser("validate")
    subparsers.add_parser("package")
    capture_parser = subparsers.add_parser("capture")
    capture_parser.add_argument("--url", default="http://127.0.0.1:8050/")
    arguments = parser.parse_args()
    settings = Settings.load()

    if arguments.command == "download":
        download_dataset(settings, force=arguments.force)
    elif arguments.command == "build":
        build_database(settings)
    elif arguments.command == "validate":
        run_validation(settings)
    elif arguments.command == "package":
        build_deploy_package(settings)
    elif arguments.command == "capture":
        capture_screenshots(settings, arguments.url)


if __name__ == "__main__":
    main()
