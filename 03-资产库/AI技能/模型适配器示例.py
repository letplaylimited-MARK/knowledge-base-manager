#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型适配器示例 - 演示如何在技能中使用不同的AI大模型

此示例展示了如何创建一个可以灵活切换AI模型的技能。
技能会根据配置自动选择合适的模型进行推理。

使用方法:
1. 确保已经在 .workbuddy/AI协作体系/模型配置/ 中配置了所需的模型
2. 在智能体定义中引用此技能
3. 系统将自动处理模型选择和调用
"""

import os
import yaml
from typing import Dict, Any
from pathlib import Path

class ModelAdapter:
    """AI模型适配器 - 负责加载模型配置并提供统一的调用接口"""
    
    def __init__(self, model_name: str):
        """
        初始化模型适配器
        
        Args:
            model_name: 模型标识符，对应.models配置目录中的文件名（不含.yaml后缀）
        """
        self.model_name = model_name
        self.config = self._load_model_config()
        self.provider = self.config.get('provider', 'unknown')
        
    def _load_model_config(self) -> Dict[str, Any]:
        """加载模型配置文件"""
        config_path = Path(f".workbuddy/AI协作体系/模型配置/{self.model_name}.yaml")
        
        if not config_path.exists():
            raise FileNotFoundError(f"模型配置文件不存在: {config_path}")
            
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        # 替换环境变量
        config = self._substitute_env_vars(config)
        return config
        
    def _substitute_env_vars(self, obj: Any) -> Any:
        """递归替换配置中的环境变量引用"""
        if isinstance(obj, dict):
            return {key: self._substitute_env_vars(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._substitute_env_vars(item) for item in obj]
        elif isinstance(obj, str) and obj.startswith("${") and obj.endswith("}"):
            env_var = obj[2:-1]
            return os.environ.get(env_var, "")
        else:
            return obj
            
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "model_name": self.model_name,
            "display_name": self.config.get("model_name", self.model_name),
            "provider": self.provider,
            "version": self.config.get("model_version", "unknown"),
            "supports_streaming": self.config.get("supports_streaming", False),
            "supports_functions": self.config.get("supports_functions", False),
            "supports_vision": self.config.get("supports_vision", False),
            "supports_embedding": self.config.get("supports_embedding", False)
        }
        
    def get_api_config(self) -> Dict[str, Any]:
        """获取API连接配置"""
        return {
            "api_key": self.config.get("api_key", ""),
            "api_base": self.config.get("api_base", ""),
            "api_version": self.config.get("api_version", "v1")
        }
        
    def get_model_parameters(self) -> Dict[str, Any]:
        """获取模型参数"""
        return {
            "temperature": self.config.get("temperature", 0.7),
            "max_tokens": self.config.get("max_tokens", 2048),
            "top_p": self.config.get("top_p", 0.9),
            "frequency_penalty": self.config.get("frequency_penalty", 0.0),
            "presence_penalty": self.config.get("presence_penalty", 0.0)
        }

# 示例技能：基于不同模型的文本摘要生成
class TextSummarizerSkill:
    """文本摘要生成技能 - 演示如何使用模型适配器"""
    
    def __init__(self, model_name: str = "openai-gpt4"):
        """
        初始化文本摘要技能
        
        Args:
            model_name: 要使用的AI模型名称
        """
        self.model_adapter = ModelAdapter(model_name)
        self.skill_name = "文本摘要生成"
        self.description = "根据指定的AI大模型生成文本摘要"
        
    def execute(self, text: str, max_length: int = 200) -> str:
        """
        执行文本摘要生成
        
        Args:
            text: 需要生成摘要的原始文本
            max_length: 摘要最大长度
            
        Returns:
            生成的文本摘要
        """
        # 获取模型信息和配置
        model_info = self.model_adapter.get_model_info()
        api_config = self.model_adapter.get_api_config()
        model_params = self.model_adapter.get_model_parameters()
        
        # 构建提示词
        prompt = f"""请为以下文本生成一个不超过{max_length}字符的简洁摘要：

{text}

摘要："""
        
        # 这里应该调用实际的AI模型API
        # 由于这是一个示例，我们返回一个模拟结果
        # 实际使用时需要根据model_info.provider调用相应的API
        
        provider = model_info["provider"]
        
        if provider == "openai":
            return self._call_openai_api(prompt, api_config, model_params)
        elif provider == "anthropic":
            return self._call_anthropic_api(prompt, api_config, model_params)
        elif provider == "zhipu":
            return self._call_zhipu_api(prompt, api_config, model_params)
        elif provider == "yi":
            return self._call_yi_api(prompt, api_config, model_params)
        else:
            # 默认返回模拟结果用于演示
            return f"[使用{model_info['display_name']}生成的摘要] {text[:max_length]}..."
            
    def _call_openai_api(self, prompt: str, api_config: Dict, params: Dict) -> str:
        """调用OpenAI API（示例）"""
        # 实际实现需要使用openai库
        # 这里返回模拟结果
        return f"[OpenAI GPT-4摘要] {prompt[:100]}..."
        
    def _call_anthropic_api(self, prompt: str, api_config: Dict, params: Dict) -> str:
        """调用Anthropic API（示例）"""
        # 实际实现需要使用anthropic库
        # 这里返回模拟结果
        return f"[Claude 3摘要] {prompt[:100]}..."
        
    def _call_zhipu_api(self, prompt: str, api_config: Dict, params: Dict) -> str:
        """调用智谱AI API（示例）"""
        # 实际实现需要使用智谱AI库
        # 这里返回模拟结果
        return f"[智谱GLM-4摘要] {prompt[:100]}..."
        
    def _call_yi_api(self, prompt: str, api_config: Dict, params: Dict) -> str:
        """调用零一万物 API（示例）"""
        # 实际实现需要使用零一万物库
        # 这里返回模拟结果
        return f"[Yi-Light摘要] {prompt[:100]}..."

# 使用示例
if __name__ == "__main__":
    # 示例文本
    sample_text = """
    人工智能（Artificial Intelligence，AI）是研究、开发用于模拟、延伸和扩展人的智能的理论、方法、技术及应用系统的一门新的技术科学。 
    人工智能是计算机科学的一个分支，它企图了解智能的实质，并生产出一种能以类似人类智能的方式做出反应的智能机器。
    该领域的研究包括机器人、语言识别、图像识别、自然语言处理和专家系统等。
    人工智能从诞生以来，理论和技术日益成熟，应用领域也不断扩展。
    可以设想，人工智能带来的科技产品，将会是人们智能信息的"容器"。 
    人工智能可以替代人的意识与信息的处理过程。人不是感受到客观世界，而是感受到的人们所主观感觉到的客观世界，而人工智能就是这种主观感觉的处理过程。
    """

    print("=== 模型适配器示例 ===\n")
    
    # 测试不同模型
    models_to_test = [
        "openai-gpt4",
        "anthropic-claude3", 
        "zhipu-glm4",
        "yi-light"
    ]
    
    for model_name in models_to_test:
        try:
            print(f"--- 使用模型: {model_name} ---")
            summarizer = TextSummarizerSkill(model_name)
            
            # 显示模型信息
            model_info = summarizer.model_adapter.get_model_info()
            print(f"模型名称: {model_info['display_name']}")
            print(f"提供商: {model_info['provider']}")
            print(f"版本: {model_info['version']}")
            print(f"支持特性: 流式={model_info['supports_streaming']}, "
                  f"函数调用={model_info['supports_functions']}, "
                  f"视觉={model_info['supports_vision']}, "
                  f"嵌入={model_info['supports_embedding']}")
            
            # 生成摘要
            summary = summarizer.execute(sample_text, max_length=150)
            print(f"生成摘要: {summary}\n")
            
        except Exception as e:
            print(f"错误: {e}\n")
    
    print("=== 示例结束 ===")
    print("注意: 此示例返回模拟结果。实际使用时需要:")
    print("1. 配置有效的API密钥环境变量")
    print("2. 安装相应的AI模型库 (openai, anthropic, etc.)")
    print("3. 替换调用方法中的实际API调用代码")