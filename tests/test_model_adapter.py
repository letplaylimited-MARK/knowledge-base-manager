import pytest


class TestModelAdapterConfigLoad:
    def test_list_models_returns_all(self):
        from model_adapter import ModelAdapter
        m = ModelAdapter()
        models = m.list_models()
        assert len(models) >= 4
        assert "openai-gpt4" in models
        assert "anthropic-claude3" in models
        assert "zhipu-glm4" in models
        assert "yi-light" in models

    def test_model_has_provider(self):
        from model_adapter import ModelAdapter
        m = ModelAdapter()
        for key, info in m.list_models().items():
            assert info["provider"] is not None

    def test_embed_support_flag(self):
        from model_adapter import ModelAdapter
        m = ModelAdapter()
        models = m.list_models()
        assert models["openai-gpt4"]["supports_embedding"] is True

    def test_unknown_model_raises(self):
        from model_adapter import ModelAdapter
        m = ModelAdapter()
        with pytest.raises(ValueError, match="Unknown model"):
            m._get_client("nonexistent_model_xyz")
