from pathlib import Path


class TestReceiveNewFile:
    def test_receive_creates_log_entry(self):
        from project_decision_workflow import ProjectDecisionWorkflow
        wf = ProjectDecisionWorkflow(str(Path.cwd()))
        result = wf.receive_new_file("/tmp/test.md", "content")
        assert result["status"] == "received"
        assert len(wf.processing_log) == 1
        assert wf.processing_log[0]["stage"] == "received"


class TestDeepContentAnalysis:
    def test_extract_themes(self):
        from project_decision_workflow import ProjectDecisionWorkflow
        wf = ProjectDecisionWorkflow(str(Path.cwd()))
        themes = wf._extract_themes("风控 审核 风险 违规 检测 预警 系统")
        assert "风控审核" in themes

    def test_extract_themes_empty_when_below_threshold(self):
        from project_decision_workflow import ProjectDecisionWorkflow
        wf = ProjectDecisionWorkflow(str(Path.cwd()))
        themes = wf._extract_themes("hello world")
        assert themes == []

    def test_extract_entities_anchor(self):
        from project_decision_workflow import ProjectDecisionWorkflow
        wf = ProjectDecisionWorkflow(str(Path.cwd()))
        entities = wf._extract_entities("主播：张三 工作表现良好")
        assert any(e["type"] == "主播" and "张三" in e["name"] for e in entities)

    def test_extract_entities_system(self):
        from project_decision_workflow import ProjectDecisionWorkflow
        wf = ProjectDecisionWorkflow(str(Path.cwd()))
        entities = wf._extract_entities("风控系统 审核系统")
        types = [e["type"] for e in entities]
        assert "系统" in types

    def test_extract_entities_metric(self):
        from project_decision_workflow import ProjectDecisionWorkflow
        wf = ProjectDecisionWorkflow(str(Path.cwd()))
        entities = wf._extract_entities("钻石：5000 收益：1000")
        assert any(e["type"] == "指标" for e in entities)

    def test_detect_project_mentions(self):
        from project_decision_workflow import ProjectDecisionWorkflow
        wf = ProjectDecisionWorkflow(str(Path.cwd()))
        projects = wf._detect_project_mentions("风控审核系统 v2 design")
        assert "风控审核系统" in projects

    def test_assess_quality_indicators(self):
        from project_decision_workflow import ProjectDecisionWorkflow
        wf = ProjectDecisionWorkflow(str(Path.cwd()))
        indicators = wf._assess_quality_indicators("# A\n# B\n# C\n# D\n- b1\n- b2\n- b3\n- b4\n- b5\n- b6\n- b7\n- b8\n- b9\n- b10\n- b11\n 示例 模板 说明")
        assert indicators["has_examples"] is True
        assert indicators["has_templates"] is True
        assert indicators["has_instructions"] is True
        assert indicators["is_structured"] is True

    def test_version_info_final(self):
        from project_decision_workflow import ProjectDecisionWorkflow
        wf = ProjectDecisionWorkflow(str(Path.cwd()))
        info = wf._extract_version_info("终极版-设计.md", "content")
        assert info["is_final"] is True

    def test_deep_content_analysis_returns_all_keys(self):
        from project_decision_workflow import ProjectDecisionWorkflow
        wf = ProjectDecisionWorkflow(str(Path.cwd()))
        result = wf.deep_content_analysis("/tmp/test.md", "风控审核系统 content")
        assert "detected_themes" in result
        assert "detected_entities" in result
        assert "detected_projects" in result
        assert "quality_indicators" in result
        assert "version_info" in result

    def test_deep_content_analysis_appends_log(self):
        from project_decision_workflow import ProjectDecisionWorkflow
        wf = ProjectDecisionWorkflow(str(Path.cwd()))
        wf.deep_content_analysis("/tmp/t.md", "data")
        assert any(e["stage"] == "content_analysis" for e in wf.processing_log)


class TestIdentifyProjectMatch:
    def test_strong_match(self):
        from project_decision_workflow import ProjectDecisionWorkflow
        wf = ProjectDecisionWorkflow(str(Path.cwd()))
        analysis = {
            "file_path": "/tmp/t.md",
            "detected_themes": ["风控审核"],
            "detected_entities": [{"name": "张三", "type": "主播"}],
            "detected_projects": ["风控审核系统"],
        }
        projects = [{"id": "p1", "name": "风控审核系统", "themes": ["风控审核"], "entities": ["张三"]}]
        result = wf.identify_project_match(analysis, projects)
        assert result["match_type"] == "strong_match"
        assert result["top_matches"][0]["match_score"] > 0.8

    def test_no_match(self):
        from project_decision_workflow import ProjectDecisionWorkflow
        wf = ProjectDecisionWorkflow(str(Path.cwd()))
        analysis = {
            "file_path": "/tmp/t.md",
            "detected_themes": [],
            "detected_entities": [],
            "detected_projects": [],
        }
        result = wf.identify_project_match(analysis, [])
        assert result["match_type"] == "no_match"
        assert result["recommendation"]["action"] == "create_new_project"


class TestGenerateDecisionQuestions:
    def test_create_new_project_question(self):
        from project_decision_workflow import ProjectDecisionWorkflow
        wf = ProjectDecisionWorkflow(str(Path.cwd()))
        analysis = {"file_path": "/tmp/new.md", "detected_themes": [], "detected_entities": [], "content_length": 100}
        match_result = {
            "recommendation": {"action": "create_new_project", "reason": "no match", "confidence": 0.7}
        }
        questions = wf.generate_decision_questions(analysis, match_result)
        types = [q["type"] for q in questions]
        assert "project_creation" in types

    def test_add_to_existing_question(self):
        from project_decision_workflow import ProjectDecisionWorkflow
        wf = ProjectDecisionWorkflow(str(Path.cwd()))
        analysis = {"file_path": "/tmp/t.md", "detected_themes": ["风控审核"], "detected_entities": [], "content_length": 200}
        match_result = {
            "recommendation": {"action": "add_to_existing", "target_project": "风控审核系统", "confidence": 0.9}
        }
        questions = wf.generate_decision_questions(analysis, match_result)
        types = [q["type"] for q in questions]
        assert "project_addition" in types

    def test_naming_question_when_name_short(self):
        from project_decision_workflow import ProjectDecisionWorkflow
        wf = ProjectDecisionWorkflow(str(Path.cwd()))
        analysis = {
            "file_path": "/tmp/s.md",
            "detected_themes": ["风控审核"],
            "detected_entities": [{"name": "张三", "type": "主播"}],
            "content_length": 300,
            "content_summary": "风控审核 Prompt",
            "version_info": {"is_final": False, "is_draft": False, "detected_version": None},
        }
        match_result = {"recommendation": {"action": "create_new_project", "confidence": 0.5}}
        questions = wf.generate_decision_questions(analysis, match_result)
        types = [q["type"] for q in questions]
        assert "naming_optimization" in types


class TestExecuteDecision:
    def test_execute_create(self):
        from project_decision_workflow import ProjectDecisionWorkflow
        wf = ProjectDecisionWorkflow(str(Path.cwd()))
        result = wf.execute_decision("/tmp/t.md", {}, "create_new_project")
        assert "create_project" in result["actions"]
        assert "07-项目文档" in result["new_location"]

    def test_execute_join(self):
        from project_decision_workflow import ProjectDecisionWorkflow
        wf = ProjectDecisionWorkflow(str(Path.cwd()))
        result = wf.execute_decision("/tmp/t.md", {}, "join_风控审核系统")
        assert "add_to_project" in result["actions"]
        assert "风控审核系统" in result["new_location"]

    def test_execute_shared(self):
        from project_decision_workflow import ProjectDecisionWorkflow
        wf = ProjectDecisionWorkflow(str(Path.cwd()))
        result = wf.execute_decision("/tmp/t.md", {}, "shared")
        assert "create_shared_component" in result["actions"]

    def test_execute_appends_decision(self):
        from project_decision_workflow import ProjectDecisionWorkflow
        wf = ProjectDecisionWorkflow(str(Path.cwd()))
        wf.execute_decision("/tmp/t.md", {}, "keep_original")
        assert len(wf.decisions) == 1
        assert wf.decisions[0].file_path == "/tmp/t.md"


class TestGenerateInsights:
    def test_theme_cluster_creates_pattern_insight(self):
        from project_decision_workflow import ProjectDecisionWorkflow
        wf = ProjectDecisionWorkflow(str(Path.cwd()))
        files = [
            {"file_path": "/a.md", "detected_themes": ["风控审核"], "detected_entities": []},
            {"file_path": "/b.md", "detected_themes": ["风控审核"], "detected_entities": []},
            {"file_path": "/c.md", "detected_themes": ["风控审核"], "detected_entities": []},
        ]
        insights = wf.generate_insights(files)
        pattern_insights = [i for i in insights if i.insight_type == "pattern"]
        assert len(pattern_insights) > 0

    def test_isolated_files_creates_suggestion(self):
        from project_decision_workflow import ProjectDecisionWorkflow
        wf = ProjectDecisionWorkflow(str(Path.cwd()))
        files = [
            {"file_path": "/iso1.md", "detected_themes": [], "detected_entities": []},
            {"file_path": "/iso2.md", "detected_themes": [], "detected_entities": []},
            {"file_path": "/iso3.md", "detected_themes": [], "detected_entities": []},
        ]
        insights = wf.generate_insights(files)
        suggestion_insights = [i for i in insights if i.insight_type == "suggestion"]
        assert len(suggestion_insights) > 0

    def test_empty_files_no_insight(self):
        from project_decision_workflow import ProjectDecisionWorkflow
        wf = ProjectDecisionWorkflow(str(Path.cwd()))
        insights = wf.generate_insights([])
        assert insights == []


class TestProcessNewFile:
    def test_process_new_file_full_flow(self):
        from project_decision_workflow import ProjectDecisionWorkflow
        wf = ProjectDecisionWorkflow(str(Path.cwd()))
        result = wf.process_new_file("/tmp/test.md", "风控审核系统 v2 with 张三")
        assert result["workflow_status"] == "awaiting_decision"
        assert "analysis" in result
        assert "match_result" in result
        assert "decision_questions" in result
        assert len(result["decision_questions"]) > 0

    def test_process_new_file_with_existing_projects(self):
        from project_decision_workflow import ProjectDecisionWorkflow
        wf = ProjectDecisionWorkflow(str(Path.cwd()))
        projects = [{"id": "p1", "name": "风控审核系统", "themes": ["风控审核"], "entities": ["张三"]}]
        result = wf.process_new_file("/tmp/t.md", "风控审核系统 version 2 uses 主播：张三", projects)
        assert result["match_result"]["match_type"] == "strong_match"


class TestGenerateReport:
    def test_generate_comprehensive_report(self):
        from project_decision_workflow import ProjectDecisionWorkflow
        wf = ProjectDecisionWorkflow(str(Path.cwd()))
        wf.execute_decision("/tmp/t.md", {}, "create_new_project")
        report = wf.generate_comprehensive_report()
        assert "workflow_summary" in report
        assert "decisions" in report
        assert "insights" in report
        assert "processing_log" in report
        assert report["workflow_summary"]["total_decisions"] == 1
