import argparse
import sys
from dataclasses import dataclass
from typing import Annotated


@dataclass
class CLIArgs:
    remote: Annotated[bool, "Use remote model for commit generation"]
    debug: Annotated[bool, "Run the CLI in debug mode"]
    model: Annotated[str | None, "Model to use for commit generation"] = None
    command: Annotated[str | None, "Sub-command passed to the CLI"] = None


def build_parser() -> argparse.ArgumentParser:
    """Builds the CLI argument parser.

    Kept as its own function (rather than module-level code) so that importing
    this package never has side effects like reading sys.argv or calling
    sys.exit(). This makes the package safe to import from tests, notebooks,
    or other tooling.
    """
    parser = argparse.ArgumentParser(
        description="Generate commit message using AI.",
        usage="aic [options]",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Enable debug logging",
        default=False,
    )
    parser.add_argument("-m", "--model", help="Model name to use (Ollama or remote)")

    remote_model_help = """
🐙 Use remote model for commit message generation.
Get an API key for OpenAI, Groq, Gemini, TogetherAI, or Deepseek, and export it to use a remote model.

> export OPENAI_API_KEY=<your-api-key>
"""
    parser.add_argument(
        "-r", "--remote", help=remote_model_help, default=False, action="store_true"
    )

    version_parser = parser.add_subparsers(title="version", dest="command")
    version_parser.add_parser("version", help="Show app version")
    return parser


def parse_cli_args(argv: list[str] | None = None) -> CLIArgs:
    """Parses CLI args into a CLIArgs instance.

    Args:
        argv: Optional explicit argument list (mainly for tests). Defaults to
            sys.argv[1:] when not provided.
    """
    parser = build_parser()
    raw_args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    return CLIArgs(
        remote=raw_args.remote,
        debug=raw_args.debug,
        model=raw_args.model,
        command=raw_args.command,
    )


class _LazyCliArgs:
    """Proxy that defers real argparse parsing until an attribute is actually
    used, instead of parsing sys.argv the moment `ai_commit` (or any module
    that does `from ai_commit import cli_args`) is imported.

    Without this, simply importing the package - e.g. from a test file, a
    notebook, or another tool - would consume sys.argv and could call
    sys.exit() on unrelated/unexpected arguments.
    """

    def __init__(self) -> None:
        self._resolved: CLIArgs | None = None

    def _resolve(self) -> CLIArgs:
        if self._resolved is None:
            self._resolved = parse_cli_args()
        return self._resolved

    def __getattr__(self, name: str):
        return getattr(self._resolve(), name)


# A single shared lazy proxy. Modules do `from ai_commit import cli_args as
# args` and only trigger argparse the first time they read an attribute like
# `args.remote`, not at import time.
cli_args = _LazyCliArgs()
