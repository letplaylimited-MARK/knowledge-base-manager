from types import SimpleNamespace

from batch_import import BatchImporter


class FakeOrganizer:
    def __init__(self):
        self.calls = []

    def process_and_store(self, file_path, dry_run=False):
        self.calls.append((file_path, dry_run))
        return {"executed": True}


class FakeAnalyzer:
    def __init__(self):
        self.calls = []

    def analyze_file(self, file_path):
        self.calls.append(file_path)
        return SimpleNamespace(
            core_topic="Batch Import",
            content_type="测试文档",
            confidence=0.9,
        )


def test_import_directory_passes_path_objects(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    file_path = source / "sample.md"
    file_path.write_text("# sample", encoding="utf-8")

    importer = BatchImporter(str(tmp_path))
    importer.organizer = FakeOrganizer()

    result = importer.import_directory(str(source))

    assert result["success"] == 1
    assert importer.organizer.calls == [(file_path, False)]


def test_preview_import_reads_content_insight_attributes(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    file_path = source / "sample.md"
    file_path.write_text("# sample", encoding="utf-8")

    importer = BatchImporter(str(tmp_path))
    importer.analyzer = FakeAnalyzer()

    result = importer.preview_import(str(source))

    assert result == [{
        "file": str(file_path),
        "topic": "Batch Import",
        "type": "测试文档",
        "confidence": 0.9,
    }]
    assert importer.analyzer.calls == [file_path]
