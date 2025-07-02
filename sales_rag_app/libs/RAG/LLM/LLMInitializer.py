from langchain_community.llms import Ollama
import os

class LLMInitializer:
    def __init__(self, model_name: str = "deepseek-r1:7b", temperature: float = 0.1):
        """
        初始化 LLM。
        :param model_name: 在 Ollama 中運行的模型名稱。
        :param temperature: 控制生成文本的隨機性。
        """
        self.model_name = model_name
        self.temperature = temperature
        self.llm = None
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        """
        載入系統提示詞
        """
        try:
            prompt_path = os.path.join(
                os.path.dirname(__file__), 
                "sysiniprompt.txt"
            )
            with open(prompt_path, 'r', encoding='utf-8') as f:
                system_prompt = f.read()
                print(f"成功載入系統提示詞: {prompt_path}")
                return system_prompt
        except FileNotFoundError:
            print(f"系統提示詞文件不存在: {prompt_path}")
            return self._get_default_system_prompt()
        except Exception as e:
            print(f"載入系統提示詞失敗: {e}")
            return self._get_default_system_prompt()

    def _get_default_system_prompt(self) -> str:
        """
        獲取預設的系統提示詞
        """
        return """System Rule Settings

General Principle
For every message received, the System must always initiate a comprehensive and explicit thinking process before generating any response. This thinking process must be clearly documented and enclosed within <think></think> tags to distinguish it from the final output. The goal is to ensure that every response is the result of deep reflection, thorough analysis, and a full exploration of all possible solutions.

Language and Presentation Requirements
All responses must be presented in Simplified Chinese, except for technology-related terms (such as programming languages, frameworks, or technical jargon), which should remain in English.
Ensure that the language used is clear, accurate, and accessible to the intended audience.
When translating or explaining, retain all technology terms in their original English form for clarity and precision.

Critical Reminder
The System's thinking process must be extremely comprehensive, thorough, and exhaustive.
This level of detail is essential to fully capture the user's underlying meaning, intent, and context, and to ensure that all possible avenues to the best response are considered.
Only after this rigorous thinking process should the System proceed to generate and deliver the final answer."""

    def get_system_prompt(self) -> str:
        """
        獲取系統提示詞
        """
        return self.system_prompt

    def create_enhanced_prompt(self, user_prompt: str) -> str:
        """
        創建包含系統提示詞的增強提示
        
        Args:
            user_prompt: 用戶提示詞
            
        Returns:
            包含系統提示詞的完整提示詞
        """
        return f"{self.system_prompt}\n\n{user_prompt}"

    def invoke_with_system_prompt(self, user_prompt: str) -> str:
        """
        使用系統提示詞調用 LLM
        
        Args:
            user_prompt: 用戶提示詞
            
        Returns:
            LLM 回應
        """
        enhanced_prompt = self.create_enhanced_prompt(user_prompt)
        return self.get_llm().invoke(enhanced_prompt)

    def get_llm(self):
        """獲取已初始化的 LLM 實例"""
        if self.llm is None:
            try:
                self.llm = Ollama(
                    model=self.model_name,
                    temperature=self.temperature
                )
                print(f"成功初始化 Ollama 模型: {self.model_name}")
                print(f"系統提示詞已載入，長度: {len(self.system_prompt)} 字符")
            except Exception as e:
                print(f"初始化 Ollama 模型失敗: {e}")
                # 可以在這裡提供一個備用的 LLM 或拋出異常
                raise ConnectionError("無法連接到 Ollama 服務。請確保 Ollama 正在運行。") from e
        return self.llm