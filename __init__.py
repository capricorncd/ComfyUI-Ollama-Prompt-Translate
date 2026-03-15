# -*- coding: utf-8 -*-
from .nodes import (
    NODE_CLASS_MAPPINGS,
    NODE_DISPLAY_NAME_MAPPINGS,
    get_ollama_models,
)

WEB_DIRECTORY = "./web"
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]


def add_ollama_routes():
    """注册供前端「刷新模型列表」使用的 API。"""
    try:
        from server import PromptServer
        from aiohttp import web

        routes = PromptServer.instance.routes

        @routes.get("/ollama_prompt_translate/models")
        async def list_ollama_models(request):
            base = request.query.get("base_url", "http://127.0.0.1:11434")
            models = get_ollama_models(base)
            return web.json_response({"models": models})
    except Exception:
        pass


try:
    from server import PromptServer
    _old_start = PromptServer.start

    def _patched_start(*args, **kwargs):
        result = _old_start(*args, **kwargs)
        add_ollama_routes()
        return result

    PromptServer.start = _patched_start
except Exception:
    pass
