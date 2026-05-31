from pathlib import Path

from app import WORKSPACE, app


def test_browse_rejects_same_prefix_path_escape():
    base_parent = WORKSPACE / "05-知识沉淀"
    escape_dir = base_parent / "wiki_evil"
    escape_file = escape_dir / "secret.md"
    escape_dir.mkdir(parents=True, exist_ok=True)
    escape_file.write_text("should not be served", encoding="utf-8")
    try:
        client = app.test_client()
        response = client.get("/browse/%2e%2e/wiki_evil/secret.md")
        assert response.status_code == 403
    finally:
        escape_file.unlink(missing_ok=True)
        try:
            escape_dir.rmdir()
        except OSError:
            pass


def test_browse_serves_wiki_file_inside_base():
    wiki_dir = WORKSPACE / "05-知识沉淀" / "wiki"
    test_file = wiki_dir / "__test_browse.md"
    wiki_dir.mkdir(parents=True, exist_ok=True)
    test_file.write_text("# Browse Smoke", encoding="utf-8")
    try:
        client = app.test_client()
        response = client.get("/browse/__test_browse.md")
        assert response.status_code == 200
        assert "Browse Smoke" in response.get_data(as_text=True)
    finally:
        test_file.unlink(missing_ok=True)
