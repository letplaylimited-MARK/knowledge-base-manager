import tempfile
from pathlib import Path


class TestContentAnalyzerFaults:
    def test_load_ontology_nonexistent(self):
        from content_analyzer import ContentAnalyzer
        analyzer = ContentAnalyzer()
        result = analyzer._load_ontology("/nonexistent/path.json")
        assert result == {}

    def test_load_ontology_invalid_json(self):
        from content_analyzer import ContentAnalyzer
        f = Path(tempfile.mktemp(suffix=".json"))
        f.write_text("not valid json {{{")
        try:
            analyzer = ContentAnalyzer()
            result = analyzer._load_ontology(str(f))
            assert result == {}
        finally:
            f.unlink()


class TestInboxWatcherFaults:
    def test_read_file_preview_nonexistent(self):
        from inbox_watcher import read_file_preview
        result = read_file_preview("Z:\\nonexistent\\path.md")
        assert result == ""

    def test_read_file_preview_binary_dir(self):
        from inbox_watcher import read_file_preview
        d = Path(tempfile.mkdtemp())
        try:
            result = read_file_preview(str(d))
            assert result == ""
        finally:
            d.rmdir()


class TestEnhancedInboxFaults:
    def test_get_file_hash_nonexistent(self):
        from enhanced_inbox_watcher import get_file_hash
        result = get_file_hash("Z:\\nonexistent\\path.md")
        assert result is None


class TestFilePipelineFaults:
    def test_read_spreadsheet_nonexistent(self):
        from file_processing_pipeline import ContentReader
        cr = ContentReader()
        result = cr._read_spreadsheet(Path("Z:\\nonexistent.csv"))
        assert result == ("[Spreadsheet read failed]", "[Spreadsheet failed]")

    def test_get_file_hash_nonexistent(self):
        from file_processing_pipeline import CoexistenceAnalyzer
        ca = CoexistenceAnalyzer()
        result = ca._get_file_hash(Path("Z:\\nonexistent"))
        assert result == ""

    def test_get_cached_content_nonexistent(self):
        from file_processing_pipeline import CoexistenceAnalyzer
        ca = CoexistenceAnalyzer()
        result = ca._get_cached_content(Path("Z:\\nonexistent"))
        assert result == ""
