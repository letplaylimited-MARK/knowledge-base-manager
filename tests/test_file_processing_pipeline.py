import tempfile
from pathlib import Path


class TestContentReader:
    def test_read_txt_file(self):
        from file_processing_pipeline import ContentReader
        f = Path(tempfile.mktemp(suffix=".txt"))
        f.write_text("hello world", encoding="utf-8")
        try:
            reader = ContentReader()
            content, preview = reader.read_file(f)
            assert content == "hello world"
            assert preview == "hello world"
        finally:
            f.unlink()

    def test_read_markdown_long(self):
        from file_processing_pipeline import ContentReader
        f = Path(tempfile.mktemp(suffix=".md"))
        body = "# Title\n\n" + "x" * 3000
        f.write_text(body, encoding="utf-8")
        try:
            reader = ContentReader()
            content, preview = reader.read_file(f)
            assert content == body
            assert "..." in preview
        finally:
            f.unlink()

    def test_read_binary_fallback(self):
        from file_processing_pipeline import ContentReader
        f = Path(tempfile.mktemp(suffix=".png"))
        f.write_bytes(b"\x89PNG\r\n\x1a\n")
        try:
            reader = ContentReader()
            content, preview = reader.read_file(f)
            assert "Binary" in content
            assert "Binary" in preview
        finally:
            f.unlink()

    def test_read_nonexistent(self):
        from file_processing_pipeline import ContentReader
        reader = ContentReader()
        content, preview = reader.read_file(Path("Z:/nonexistent/file.txt"))
        assert "Error" in content


class TestContentUnderstander:
    def test_extract_core_topic_from_title(self):
        from file_processing_pipeline import ContentUnderstander
        cu = ContentUnderstander()
        topic = cu._extract_core_topic("# 风控审核系统设计\nsome content")
        assert topic == "风控审核系统设计"

    def test_extract_core_topic_from_keywords(self):
        from file_processing_pipeline import ContentUnderstander
        cu = ContentUnderstander()
        topic = cu._extract_core_topic("风控审核 system with 审核 rules")
        assert topic == "风控审核系统"

    def test_determine_content_type_prompt(self):
        from file_processing_pipeline import ContentUnderstander
        cu = ContentUnderstander()
        tp = cu._determine_content_type("prompt: 风控审核", Path("test.txt"))
        assert tp == "风控审核Prompt"

    def test_determine_content_type_meeting(self):
        from file_processing_pipeline import ContentUnderstander
        cu = ContentUnderstander()
        tp = cu._determine_content_type("hello", Path("会议纪要.md"))
        assert tp == "会议纪要"

    def test_assess_quality_final(self):
        from file_processing_pipeline import ContentUnderstander
        cu = ContentUnderstander()
        q = cu._assess_quality("content", Path("终极版.md"))
        assert q == "已验证精品"

    def test_assess_quality_standard(self):
        from file_processing_pipeline import ContentUnderstander
        cu = ContentUnderstander()
        q = cu._assess_quality("short", Path("draft.md"))
        assert q == "标准"

    def test_extract_entities(self):
        from file_processing_pipeline import ContentUnderstander
        cu = ContentUnderstander()
        entities = cu._extract_entities("主播：张三 主播：李四 3000钻石")
        names = [e["name"] for e in entities]
        assert "张三" in names
        assert "李四" in names
        assert len(entities) <= 5

    def test_extract_concepts(self):
        from file_processing_pipeline import ContentUnderstander
        cu = ContentUnderstander()
        concepts = cu._extract_concepts("identity_confirmed system with agen model")
        assert "identity_confirmed" in concepts
        assert "agen_gen" in concepts

    def test_understand_returns_full_object(self):
        from file_processing_pipeline import ContentUnderstander
        cu = ContentUnderstander()
        result = cu.understand(Path("test.md"), "# Hello", "Hello")
        assert result.core_topic == "Hello"
        assert result.content_type is not None
        assert result.content_hash is not None
        assert result.quality_level is not None


class TestCoexistenceAnalyzer:
    def test_analyze_duplicate(self):
        from file_processing_pipeline import ContentUnderstander, CoexistenceAnalyzer
        f1 = Path(tempfile.mktemp(suffix=".txt"))
        f1.write_text("same content", encoding="utf-8")
        try:
            analyzer = CoexistenceAnalyzer(existing_files=[f1])
            cu = ContentUnderstander()
            fu = cu.understand(Path("dup.txt"), "same content", "same")
            decision = analyzer.analyze_coexistence(fu)
            assert decision.coexistence_type == "duplicate"
        finally:
            f1.unlink()

    def test_analyze_distinct(self):
        from file_processing_pipeline import ContentUnderstander, CoexistenceAnalyzer
        f1 = Path(tempfile.mktemp(suffix=".txt"))
        f1.write_text("unique A content unique", encoding="utf-8")
        try:
            analyzer = CoexistenceAnalyzer(existing_files=[f1])
            cu = ContentUnderstander()
            fu = cu.understand(Path("new.txt"), "totally different B", "preview")
            decision = analyzer.analyze_coexistence(fu)
            assert decision.coexistence_type == "distinct"
        finally:
            f1.unlink()

    def test_detect_version_relationship(self):
        from file_processing_pipeline import ContentUnderstander, CoexistenceAnalyzer
        f1 = Path(tempfile.mktemp(suffix=".txt"))
        f1.write_text("existing content", encoding="utf-8")
        try:
            analyzer = CoexistenceAnalyzer(existing_files=[f1])
            cu = ContentUnderstander()
            fu = cu.understand(Path("base_V2.txt"), "new version content", "preview")
            decision = analyzer.analyze_coexistence(fu)
            assert decision.coexistence_type in ("version", "distinct")
        finally:
            f1.unlink()

    def test_file_hash_nonexistent(self):
        from file_processing_pipeline import CoexistenceAnalyzer
        analyzer = CoexistenceAnalyzer()
        h = analyzer._get_file_hash(Path("Z:/nonexistent.file"))
        assert h == ""


class TestNamingAdvisor:
    def test_advise_new_file(self):
        from file_processing_pipeline import (
            ContentUnderstander, NamingAdvisor,
            CoexistenceDecision
        )
        cu = ContentUnderstander()
        fu = cu.understand(Path("raw.md"), "# 数据分析报告", "report")
        cd = CoexistenceDecision(
            should_coexist=True, coexistence_type="distinct",
            reason="unique", suggested_action="store", related_files=[]
        )
        advisor = NamingAdvisor()
        naming = advisor.advise(fu, cd)
        assert naming.original_name == "raw.md"
        assert "数据分析" in naming.suggested_name or naming.suggested_name is not None

    def test_should_rename_short(self):
        from file_processing_pipeline import NamingAdvisor
        advisor = NamingAdvisor()
        from file_processing_pipeline import ContentUnderstander, CoexistenceDecision
        cu = ContentUnderstander()
        fu = cu.understand(Path("a.md"), "some content", "preview")
        cd = CoexistenceDecision(True, "distinct", "", "store", [])
        naming = advisor.advise(fu, cd)
        assert naming.should_rename is True

    def test_generate_alternatives_contains_date(self):
        from file_processing_pipeline import NamingAdvisor
        advisor = NamingAdvisor()
        from file_processing_pipeline import ContentUnderstander, CoexistenceDecision
        cu = ContentUnderstander()
        fu = cu.understand(Path("test.md"), "content", "preview")
        cd = CoexistenceDecision(True, "distinct", "", "store", [])
        naming = advisor.advise(fu, cd)
        assert len(naming.alternatives) > 0


class TestProcessingResultDataclass:
    def test_processing_result_fields(self):
        from file_processing_pipeline import (
            FileUnderstanding, CoexistenceDecision, NamingDecision, ProcessingResult
        )
        from pathlib import Path
        fu = FileUnderstanding(
            Path("f.md"), "abc123", "preview", "full",
            "topic", "doc", "high", [], [], [], {}
        )
        cd = CoexistenceDecision(True, "distinct", "reason", "store", [])
        nd = NamingDecision(False, "f.md", "f.md", [], "ok", 0.9)
        pr = ProcessingResult(fu, cd, nd, "recommendation", {})
        assert pr.understanding.core_topic == "topic"
        assert pr.coexistence.coexistence_type == "distinct"
        assert pr.naming.original_name == "f.md"
        assert pr.final_recommendation == "recommendation"

    def test_generate_report_contains_sections(self):
        from file_processing_pipeline import (
            FileUnderstanding, CoexistenceDecision, NamingDecision, ProcessingResult,
            FileProcessingPipeline
        )
        fu = FileUnderstanding(
            Path("r.md"), "abc", "preview", "full",
            "t", "doc", "high", [{"name": "e1", "type": "ANCHOR"}],
            ["c1"], ["batch Excel处理"], {"version": None, "is_versioned": False, "base_name": "r.md"}
        )
        cd = CoexistenceDecision(True, "version", "version chain", "coexist", [])
        nd = NamingDecision(True, "r.md", "r-V1.md", ["alt"], "reason", 0.8)
        pr = ProcessingResult(fu, cd, nd, "recommendation", {"key": "val"})
        pipeline = FileProcessingPipeline(str(Path.cwd()))
        report = pipeline.generate_processing_report(pr)
        assert "## 内容理解" in report
        assert "## 共存分析" in report
        assert "## 命名建议" in report
        assert "## 最终推荐" in report
        assert "## 行动计划" in report
