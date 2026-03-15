# -*- coding: utf-8 -*-
"""
ComfyUI 中文提示词 → 英文（通过 Ollama 翻译）
输入中文提示词，使用可选 Ollama 模型翻译为英文，供后续生图/生视频节点使用。
"""

import json
import logging
import os
import urllib.request
import urllib.error
from typing import List

# 默认 Ollama 地址
DEFAULT_OLLAMA_BASE = "http://127.0.0.1:11434"

# 扩展目录，用于保存上次选择的模型
_EXTRA_DIR = os.path.dirname(os.path.abspath(__file__))
_CONFIG_PATH = os.path.join(_EXTRA_DIR, "ollama_translate_config.json")


def _load_last_model() -> str:
    """读取上次使用的模型名，不存在或无效则返回空字符串。"""
    try:
        if os.path.isfile(_CONFIG_PATH):
            with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            return (data.get("last_model") or "").strip()
    except Exception:
        pass
    return ""


def _save_last_model(model: str) -> None:
    """保存本次使用的模型名（仅有效模型名会写入）。"""
    if not model or model.startswith("(") or "(无" in model or "(请" in model:
        return
    try:
        with open(_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump({"last_model": model}, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

# TRANSLATE_SYSTEM = (
#     "You are a professional translator for AI image and video generation. "
#     "Translate the user's prompt into a single, concise English prompt "
#     "suitable for image or video generation. Output ONLY the English prompt, "
#     "no explanations or extra text."
# )
TRANSLATE_SYSTEM = """
You are a professional prompt translator specializing in AI image and video generation. 
Translate the user's input into a single, clear, and detailed English prompt optimized 
for text-to-image/video models. Preserve all creative elements, style references, and 
technical specifications from the original. Output ONLY the translated English prompt 
with no explanations, notes, or additional text.
"""


def get_ollama_models(base_url: str = DEFAULT_OLLAMA_BASE) -> List[str]:
    """从 Ollama 获取可用模型列表。失败时返回占位项。"""
    try:
        req = urllib.request.Request(
            f"{base_url.rstrip('/')}/api/tags",
            headers={"Content-Type": "application/json"},
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
        models = data.get("models") or []
        names = []
        for m in models:
            name = m.get("name") or m.get("model") or ""
            if name:
                names.append(name)
        return names if names else ["(无可用模型，请先启动 Ollama 并拉取模型)"]
    except Exception as e:
        logging.warning("[Ollama Prompt Translate] 获取模型列表失败: %s", e)
        return ["(请先启动 Ollama 并拉取模型)"]


def translate_with_ollama(
    chinese_prompt: str,
    model: str,
    base_url: str = DEFAULT_OLLAMA_BASE,
    system_prompt: str = TRANSLATE_SYSTEM,
) -> str:
    """使用 Ollama /api/generate 将中文提示词翻译成英文。"""
    if not (chinese_prompt or "").strip():
        return ""

    # 若选择的是占位项，不请求 Ollama
    if model.startswith("(") or "(无" in model or "(请" in model:
        logging.warning("[Ollama Prompt Translate] 未选择有效模型，返回原文。")
        return chinese_prompt.strip()

    url = f"{base_url.rstrip('/')}/api/generate"
    payload = {
        "model": model,
        "prompt": chinese_prompt.strip(),
        "stream": False,
        "system": system_prompt,
    }
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            out = json.loads(resp.read().decode())
        response = (out.get("response") or "").strip()
        return response if response else chinese_prompt.strip()
    except urllib.error.HTTPError as e:
        body = (e.read() or b"").decode("utf-8", errors="ignore")
        logging.error("[Ollama Prompt Translate] HTTP 错误: %s %s", e.code, body)
        return chinese_prompt.strip()
    except Exception as e:
        logging.error("[Ollama Prompt Translate] 翻译失败: %s", e)
        return chinese_prompt.strip()


class OllamaPromptTranslate:
    """输入中文提示词，用 Ollama 翻译成英文后输出，供生图/生视频节点使用。"""

    @classmethod
    def INPUT_TYPES(cls):
        models = get_ollama_models()
        last = _load_last_model()
        default_model = last if last and last in models else (models[0] if models else "")
        return {
            "required": {
                "raw_prompt": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "",
                        "placeholder": "输入提示词，例如：一只在夕阳下奔跑的橘猫",
                    },
                ),
                "model": (models, {"default": default_model}),
            },
            "optional": {
                "ollama_base_url": (
                    "STRING",
                    {
                        "default": DEFAULT_OLLAMA_BASE,
                        "placeholder": "例如 http://127.0.0.1:11434",
                    },
                ),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("english_prompt",)
    FUNCTION = "translate"
    CATEGORY = "prompt"
    OUTPUT_NODE = True

    def translate(
        self,
        raw_prompt: str,
        model: str,
        ollama_base_url: str = DEFAULT_OLLAMA_BASE,
    ):
        base = (ollama_base_url or "").strip() or DEFAULT_OLLAMA_BASE
        english_prompt = translate_with_ollama(raw_prompt, model, base)
        _save_last_model(model)
        return {"ui": {"text": (english_prompt,)}, "result": (english_prompt,)}


# 供前端刷新模型列表时使用：每次取最新列表
def get_ollama_models_for_input(base_url: str = DEFAULT_OLLAMA_BASE) -> List[str]:
    return get_ollama_models(base_url)


NODE_CLASS_MAPPINGS = {
    "OllamaPromptTranslate": OllamaPromptTranslate,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "OllamaPromptTranslate": "提示词 → Ollama 英文翻译",
}
