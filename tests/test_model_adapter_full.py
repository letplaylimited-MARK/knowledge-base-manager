

class TestModelAdapterSandbox:
    def test_sandbox_chat_returns_canned(self):
        from model_adapter import ModelAdapter
        adapter = ModelAdapter(sandbox=True)
        result = adapter.chat("openai-gpt4", [{"role": "user", "content": "Hello"}])
        assert "[SANDBOX]" in result
        assert "openai-gpt4" in result

    def test_sandbox_chat_empty_messages(self):
        from model_adapter import ModelAdapter
        adapter = ModelAdapter(sandbox=True)
        result = adapter.chat("openai-gpt4", [])
        assert "[SANDBOX]" in result

    def test_sandbox_embed_returns_vector(self):
        from model_adapter import ModelAdapter
        adapter = ModelAdapter(sandbox=True)
        result = adapter.embed("test text")
        assert isinstance(result, list)
        assert len(result) == 384
        assert all(isinstance(v, float) for v in result)

    def test_sandbox_embed_deterministic(self):
        from model_adapter import ModelAdapter
        adapter = ModelAdapter(sandbox=True)
        a = adapter.embed("hello world")
        b = adapter.embed("hello world")
        assert a == b

    def test_sandbox_embed_different_inputs_differ(self):
        from model_adapter import ModelAdapter
        adapter = ModelAdapter(sandbox=True)
        a = adapter.embed("hello")
        b = adapter.embed("world")
        assert a != b

    def test_sandbox_auto_detects_missing_keys(self, monkeypatch):
        for k in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "ZHIPU_API_KEY", "YI_API_KEY"]:
            monkeypatch.delenv(k, raising=False)
        from model_adapter import ModelAdapter
        adapter = ModelAdapter()
        assert adapter._sandbox is True

    def test_sandbox_not_active_when_key_present(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-fake")
        from model_adapter import ModelAdapter
        adapter = ModelAdapter()
        assert adapter._sandbox is False
