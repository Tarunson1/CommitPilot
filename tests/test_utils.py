from ai_commit.utils import parse_host


def test_parse_host_defaults_to_localhost():
    assert parse_host(None) == "http://127.0.0.1:11434"
    assert parse_host("") == "http://127.0.0.1:11434"


def test_parse_host_hostname_only():
    assert parse_host("localhost") == "http://localhost:11434"


def test_parse_host_with_scheme():
    assert parse_host("http://localhost") == "http://localhost:80"
    assert parse_host("https://example.com") == "https://example.com:443"


def test_parse_host_with_explicit_port():
    assert parse_host("https://example.com:8080") == "https://example.com:8080"


def test_parse_host_with_path():
    assert (
        parse_host("https://example.com:8080/api/v1")
        == "https://example.com:8080/api/v1"
    )


def test_parse_host_ipv6():
    assert parse_host("[::1]") == "http://[::1]:11434"


def test_parse_host_malformed_falls_back_instead_of_crashing():
    # Regression test: an unbracketed IPv6 host used to raise an unhandled
    # ValueError from urllib.parse, crashing the whole CLI at import time.
    assert parse_host("::1") == "http://127.0.0.1:11434"
