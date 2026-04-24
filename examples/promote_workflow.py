"""Promote an existing workflow by publishing a new version."""

from __future__ import annotations

import argparse
from pathlib import Path

from alteryx_server_py import AlteryxClient


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Publish a new version of an existing workflow.")
    parser.add_argument("--workflow-id", required=True, help="Target workflow ID.")
    parser.add_argument("--package", required=True, help="Path to the updated workflow package.")
    parser.add_argument("--comments", default=None, help="Optional version comment.")
    return parser.parse_args()


def promote_workflow(args: argparse.Namespace) -> None:
    """Publish a new version for an existing workflow.

    Args:
        args (argparse.Namespace): Parsed CLI arguments.
    """
    package_path = Path(args.package)
    if not package_path.exists():
        raise FileNotFoundError(f"Package not found: {package_path}")

    client = AlteryxClient.from_env()
    version = client.workflows.publish_version(
        workflow_id=args.workflow_id,
        file_path=str(package_path),
        comments=args.comments,
    )
    print(f"Published workflow version {version.id} for {args.workflow_id}")

    versions = client.workflows.list_versions(args.workflow_id)
    print(f"Workflow now has {len(versions)} version(s).")


def main() -> None:
    """Run the workflow promotion example."""
    args = parse_args()
    promote_workflow(args)


if __name__ == "__main__":
    main()
