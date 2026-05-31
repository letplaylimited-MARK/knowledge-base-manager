import pytest
import tempfile

import os

# Ensure FAISS path is ASCII (tmp dir avoids Chinese-path fopen issue)
import uuid

os.environ["TEMP"] = tempfile.gettempdir()


@pytest.fixture()
def vector_search_module(tmp_path, monkeypatch):
    import vector_search
    workspace = tmp_path / "workspace"
    index_dir = workspace / ".workbuddy" / "index"
    workspace.mkdir()

    monkeypatch.setattr(vector_search, "WORKSPACE", workspace)
    monkeypatch.setattr(vector_search, "INDEX_DIR", index_dir)
    monkeypatch.setattr(vector_search, "DB_PATH", index_dir / "search_index.db")
    monkeypatch.setattr(vector_search, "FAISS_PATH", tmp_path / "vectors.faiss")
    return vector_search


def _workspace_temp(workspace, suffix: str):
    return workspace / f"__test_tmp_{uuid.uuid4().hex[:8]}{suffix}"


class TestIndexFile:
    def test_index_file_creates_db_entry(self, vector_search_module):
        tmp = _workspace_temp(vector_search_module.WORKSPACE, ".md")
        tmp.write_text("# Test\nhello world")
        assert vector_search_module.index_file(tmp)
        conn = vector_search_module._get_db()
        rel = str(tmp.relative_to(vector_search_module.WORKSPACE))
        row = conn.execute("SELECT path FROM documents WHERE path=?", (rel,)).fetchone()
        conn.close()
        assert row is not None

    def test_index_file_skips_directory(self, vector_search_module):
        tmpdir = _workspace_temp(vector_search_module.WORKSPACE, "_dir")
        tmpdir.mkdir()
        assert not vector_search_module.index_file(tmpdir)

    def test_rebuild_index_returns_count(self, vector_search_module):
        count = vector_search_module.rebuild_index()
        assert isinstance(count, int)
        assert count >= 0


class TestSearchKeyword:
    def test_search_existing(self, vector_search_module):
        tmp = _workspace_temp(vector_search_module.WORKSPACE, ".md")
        tmp.write_text("pytest_special_keyword_abc123")
        vector_search_module.index_file(tmp)
        results = vector_search_module.search_keyword("pytest_special_keyword_abc123")
        assert len(results) >= 1

    def test_search_nonexistent(self, vector_search_module):
        results = vector_search_module.search_keyword("zzz_nonexistent_999")
        assert isinstance(results, list)


class TestBuildFaiss:
    def test_build_faiss_returns_int(self, vector_search_module):
        if not vector_search_module.HAS_VECTOR:
            pytest.skip("FAISS not installed")
        count = vector_search_module.build_faiss_index()
        assert isinstance(count, int)
