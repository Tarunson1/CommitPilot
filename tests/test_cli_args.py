import sys

import ai_commit
from ai_commit import parse_cli_args


def test_parse_cli_args_defaults():
    parsed = parse_cli_args([])
    assert parsed.remote is False
    assert parsed.debug is False
    assert parsed.model is None
    assert parsed.command is None


def test_parse_cli_args_flags():
    parsed = parse_cli_args(["-r", "-d", "-m", "llama3.2:3b"])
    assert parsed.remote is True
    assert parsed.debug is True
    assert parsed.model == "llama3.2:3b"


def test_parse_cli_args_version_subcommand():
    parsed = parse_cli_args(["version"])
    assert parsed.command == "version"


def test_importing_package_does_not_parse_sys_argv(monkeypatch):
    # Regression test: importing ai_commit used to eagerly call
    # argparse.parse_args() against the real sys.argv at import time, which
    # meant merely importing the package (e.g. under pytest, where sys.argv
    # contains pytest's own flags) could crash or exit the process.
    monkeypatch.setattr(sys, "argv", ["pytest", "--not-a-real-aic-flag"])
    fresh_proxy = ai_commit._LazyCliArgs()
    # Constructing/importing must not resolve anything yet.
    assert fresh_proxy._resolved is None
