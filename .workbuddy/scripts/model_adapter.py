import os
import json
from pathlib import Path

CONFIG_DIR = Path(__file__).resolve().parent.parent / "AI协作体系" / "模型配置"


class ModelAdapter:
    def __init__(self, config_dir: Path = CONFIG_DIR):
        self.models: dict[str, dict] = {}
        self._clients: dict[str, object] = {}
        self._load_configs(config_dir)

    def _load_configs(self, config_dir: Path):
        import yaml
        if not config_dir.exists():
            return
        for f in sorted(config_dir.glob("*.yaml")):
            try:
                with open(f, encoding="utf-8") as fh:
                    cfg = yaml.safe_load(fh)
                key = cfg.get("model_name", f.stem).lower().replace(" ", "-")
                self.models[key] = cfg
            except Exception:
                pass

    def _get_client(self, model_key: str):
        if model_key in self._clients:
            return self._clients[model_key]
        cfg = self.models.get(model_key)
        if not cfg:
            raise ValueError(f"Unknown model: {model_key}")
        provider = cfg.get("provider", "")
        api_key_var = cfg.get("api_key", "").strip("${} ")
        api_key = os.environ.get(api_key_var)
        if provider == "openai":
            from openai import OpenAI
            self._clients[model_key] = OpenAI(api_key=api_key)
        elif provider == "anthropic":
            from anthropic import Anthropic
            self._clients[model_key] = Anthropic(api_key=api_key)
        elif provider == "zhipu":
            from zhipuai import ZhipuAI
            self._clients[model_key] = ZhipuAI(api_key=api_key)
        elif provider == "yi":
            from openai import OpenAI
            base = cfg.get("api_base", "https://api.lingyiwanwu.com/v1")
            self._clients[model_key] = OpenAI(api_key=api_key, base_url=base)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        return self._clients[model_key]

    def chat(self, model_key: str, messages: list, stream: bool = False,
             temperature: float = None, max_tokens: int = None) -> str:
        cfg = self.models.get(model_key)
        if not cfg:
            raise ValueError(f"Unknown model: {model_key}")
        client = self._get_client(model_key)
        provider = cfg.get("provider", "")
        model_version = cfg.get("model_version", "")
        if provider == "openai":
            resp = client.chat.completions.create(
                model=model_version, messages=messages,
                temperature=temperature or cfg.get("temperature", 0.7),
                max_tokens=max_tokens or cfg.get("max_tokens", 4096),
                stream=stream)
            return resp.choices[0].message.content if not stream else resp
        elif provider == "anthropic":
            msgs = messages
            system = None
            if messages and messages[0].get("role") == "system":
                system = messages[0]["content"]
                msgs = messages[1:]
            resp = client.messages.create(
                model=model_version, messages=msgs,
                system=system, max_tokens=max_tokens or cfg.get("max_tokens", 4096),
                temperature=temperature or cfg.get("temperature", 0.7))
            return resp.content[0].text
        elif provider in ("zhipu", "yi"):
            resp = client.chat.completions.create(
                model=model_version, messages=messages,
                temperature=temperature or cfg.get("temperature", 0.7))
            return resp.choices[0].message.content
        return ""

    def embed(self, text: str, model_key: str = None) -> list[float]:
        if not model_key:
            for k, v in self.models.items():
                if v.get("supports_embedding"):
                    model_key = k
                    break
        if not model_key:
            raise ValueError("No model supports embedding")
        cfg = self.models[model_key]
        client = self._get_client(model_key)
        provider = cfg.get("provider", "")
        model_version = cfg.get("model_version", "")
        if provider == "openai":
            resp = client.embeddings.create(model=model_version, input=text)
            return resp.data[0].embedding
        raise ValueError(f"Provider {provider} does not support embeddings")

    def list_models(self) -> dict:
        return {k: {
            "provider": v.get("provider"),
            "version": v.get("model_version"),
            "supports_streaming": v.get("supports_streaming"),
            "supports_functions": v.get("supports_functions"),
            "supports_vision": v.get("supports_vision"),
            "supports_embedding": v.get("supports_embedding"),
        } for k, v in self.models.items()}
