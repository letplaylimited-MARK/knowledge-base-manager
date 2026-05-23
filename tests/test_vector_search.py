import pytest
from pathlib import Path
import tempfile

import os

# Ensure FAISS path is ASCII (tmp dir avoids Chinese-path fopen issue)
import uuid

os.environ["TEMP"] = tempfile.gettempdir()


WORKSPACE = Path(__file__).resolve().parent.parent
_test_counter = 0


def _workspace_temp(suffix: str) -> Path:
    global _test_counter
    _test_counter += 1
    return WORKSPACE / f"__test_tmp_{_test_counter}_{uuid.uuid4().hex[:8]}{suffix}"


class TestIndexFile:
    def test_index_file_creates_db_entry(self):
        from vector_search import index_file, _get_db, DB_PATH
        if DB_PATH.exists():
            DB_PATH.unlink()
        tmp = _workspace_temp(".md")
        tmp.write_text("# Test\nhello world")
        try:
            assert index_file(tmp)
            conn = _get_db()
            rel = str(tmp.relative_to(WORKSPACE))
            row = conn.execute("SELECT path FROM documents WHERE path=?", (rel,)).fetchone()
            conn.close()
            assert row is not None
        finally:
            tmp.unlink()

    def test_index_file_skips_directory(self):
        from vector_search import index_file
        tmpdir = _workspace_temp("_dir")
        tmpdir.mkdir()
        try:
            assert not index_file(tmpdir)
        finally:
            tmpdir.rmdir()

    def test_rebuild_index_returns_count(self):
        from vector_search import rebuild_index, DB_PATH
        if DB_PATH.exists():
            DB_PATH.unlink()
        count = rebuild_index()
        assert isinstance(count, int)
        assert count >= 0


class TestSearchKeyword:
    def test_search_existing(self):
        from vector_search import search_keyword, index_file, DB_PATH
        if not DB_PATH.exists():
            import importlib
            importlib.import_module("vector_search").rebuild_index()
        tmp = _workspace_temp(".md")
        tmp.write_text("pytest_special_keyword_abc123")
        try:
            index_file(tmp)
            results = search_keyword("pytest_special_keyword_abc123")
            assert len(results) >= 1
        finally:
            tmp.unlink()

    def test_search_nonexistent(self):
        from vector_search import search_keyword
        results = search_keyword("zzz_nonexistent_999")
        assert isinstance(results, list)


class TestBuildFaiss:
    def test_build_faiss_returns_int(self):
        from vector_search import build_faiss_index, HAS_VECTOR
        if not HAS_VECTOR:
            pytest.skip("FAISS not installed")
        count = build_faiss_index()
        assert isinstance(count, int)
