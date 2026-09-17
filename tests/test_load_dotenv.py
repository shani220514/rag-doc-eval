"""Tests for eval_retrieve.load_dotenv — .env must only load in live CLI paths."""
import os
import sys

from eval_retrieve import load_dotenv


def test_load_dotenv_parses_key_value(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text(
        "# comment\nRETRIEVE_API_KEY=fake-key-123\n"
        'RETRIEVE_WORKSPACE_ID="quoted-ws"\n'
        "RETRIEVE_INDEX_ID='single-idx'\n"
        "BARE_NO_QUOTES\n"
        "\n"
        "EMPTY=val\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("RETRIEVE_API_KEY", raising=False)
    monkeypatch.delenv("RETRIEVE_WORKSPACE_ID", raising=False)
    monkeypatch.delenv("RETRIEVE_INDEX_ID", raising=False)
    monkeypatch.delenv("EMPTY", raising=False)
    monkeypatch.delenv("EVAL_NO_DOTENV", raising=False)
    loaded = load_dotenv(env)
    assert loaded["RETRIEVE_API_KEY"] == "fake-key-123"
    assert loaded["RETRIEVE_WORKSPACE_ID"] == "quoted-ws"
    assert loaded["RETRIEVE_INDEX_ID"] == "single-idx"
    assert "BARE_NO_QUOTES" not in loaded
    assert os.environ["RETRIEVE_API_KEY"] == "fake-key-123"
    assert os.environ["RETRIEVE_WORKSPACE_ID"] == "quoted-ws"


def test_load_dotenv_does_not_override_existing(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text("RETRIEVE_API_KEY=from-file\n", encoding="utf-8")
    monkeypatch.setenv("RETRIEVE_API_KEY", "from-shell")
    monkeypatch.delenv("EVAL_NO_DOTENV", raising=False)
    loaded = load_dotenv(env)
    assert "RETRIEVE_API_KEY" not in loaded
    assert os.environ["RETRIEVE_API_KEY"] == "from-shell"


def test_load_dotenv_skips_when_no_file(tmp_path, monkeypatch):
    monkeypatch.delenv("EVAL_NO_DOTENV", raising=False)
    loaded = load_dotenv(tmp_path / "no-such-.env")
    assert loaded == {}


def test_load_dotenv_respects_eval_no_dotenv(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text("RETRIEVE_API_KEY=should-not-load\n", encoding="utf-8")
    monkeypatch.delenv("RETRIEVE_API_KEY", raising=False)
    monkeypatch.setenv("EVAL_NO_DOTENV", "1")
    loaded = load_dotenv(env)
    assert loaded == {}
    assert not os.environ.get("RETRIEVE_API_KEY")


def test_import_does_not_load_env(monkeypatch):
    import importlib

    monkeypatch.delenv("RETRIEVE_API_KEY", raising=False)
    sys.modules.pop("eval_retrieve", None)
    importlib.import_module("eval_retrieve")
    assert not os.environ.get("RETRIEVE_API_KEY"), "import must not load .env"
