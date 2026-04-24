"""Deploy a workflow package to Alteryx Server."""

from __future__ import annotations

import argparse
from pathlib import Path

from alteryx_server_py import AlteryxClient


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Publish or update a workflow package.")
    parser.add_argument("--package", required=True, help="Path to the .yxzp or .yxmd package.")
    parser.add_argument("--name", required=True, help="Workflow name on the server.")
    parser.add_argument("--owner-id", help="Owner ID required when publishing a new workflow.")
    parser.add_argument("--workflow-id", help="Existing workflow ID to update directly.")
    parser.add_argument("--comments", default=None, help="Optional deployment comment.")
    parser.add_argument("--public", action="store_true", help="Publish the workflow as public.")
    return parser.parse_args()


def deploy_workflow(args: argparse.Namespace) -> None:
    """Publish a new workflow or update an existing one.

    Args:
        args (argparse.Namespace): Parsed CLI arguments.
    """
    package_path = Path(args.package)
    if not package_path.exists():
        raise FileNotFoundError(f"Package not found: {package_path}")

    client = AlteryxClient.from_env()

    workflow_id = args.workflow_id
    if workflow_id is None:
        matches = client.workflows.list(name=args.name)
        if matches:
            workflow_id = matches[0].id

    if workflow_id:
        workflow = client.workflows.update(
            workflow_id=workflow_id,
            file_path=str(package_path),
            name=args.name,
            is_public=args.public,
            comments=args.comments,
        )
        print(f"Updated workflow {workflow.id}: {workflow.name}")
        return

    if not args.owner_id:
        raise ValueError("--owner-id is required when publishing a new workflow.")

    workflow = client.workflows.publish(
        file_path=str(package_path),
        name=args.name,
        owner_id=args.owner_id,
        is_public=args.public,
        comments=args.comments,
    )
    print(f"Published workflow {workflow.id}: {workflow.name}")


def main() -> None:
    """Run the deployment example."""
    args = parse_args()
    deploy_workflow(args)


if __name__ == "__main__":
    main()
