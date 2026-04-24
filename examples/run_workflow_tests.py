"""Execute a workflow and report success or failure for CI/CD usage."""

from __future__ import annotations

import argparse

from alteryx_server_py import AlteryxClient


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Run a workflow and wait for completion.")
    parser.add_argument("--workflow-id", required=True, help="Workflow ID to execute.")
    parser.add_argument("--priority", default="Default", help="Job priority.")
    parser.add_argument("--timeout", type=int, default=1800, help="Timeout in seconds.")
    parser.add_argument("--poll-interval", type=int, default=10, help="Polling interval in seconds.")
    parser.add_argument(
        "--question",
        action="append",
        default=[],
        help="Question override in key=value format. Repeat for multiple values.",
    )
    return parser.parse_args()


def parse_questions(raw_questions: list[str]) -> dict[str, str]:
    """Parse repeated key=value question arguments.

    Args:
        raw_questions (list[str]): Raw `--question` arguments.

    Returns:
        dict[str, str]: Parsed question mapping.
    """
    questions: dict[str, str] = {}
    for raw_value in raw_questions:
        if "=" not in raw_value:
            raise ValueError(f"Invalid question format: {raw_value}")
        key, value = raw_value.split("=", 1)
        questions[key] = value
    return questions


def run_workflow_test(args: argparse.Namespace) -> None:
    """Execute a workflow and print a CI-friendly summary.

    Args:
        args (argparse.Namespace): Parsed CLI arguments.
    """
    client = AlteryxClient.from_env()
    questions = parse_questions(args.question)
    job = client.jobs.run_and_wait(
        workflow_id=args.workflow_id,
        questions=questions or None,
        priority=args.priority,
        timeout=args.timeout,
        poll_interval=args.poll_interval,
    )

    print(f"Job {job.id} finished with status {job.status.value}")
    for message in job.messages:
        print(f"[{message.level or 'Info'}] {message.message}")
    for output in job.outputs:
        print(f"Output: {output.id} {output.name}")


def main() -> None:
    """Run the workflow test example."""
    args = parse_args()
    run_workflow_test(args)


if __name__ == "__main__":
    main()
