# ComfyUI 中文提示词 → Ollama 英文翻译

将中文提示词通过本地 Ollama 模型翻译成英文，输出可接 CLIP Text Encode 等节点用于生图/生视频。

## 功能

- **输入**：中文提示词（多行）
- **模型**：从 Ollama 拉取的模型列表中选择（需先启动 [Ollama](https://ollama.com) 并拉取至少一个模型）
- **输出**：英文提示词（STRING），可连到「CLIP Text Encode」等节点

## 使用

1. 安装并启动 Ollama，拉取任意语言模型（如 `ollama pull qwen2.5:7b` 或 `llama3.2`）。
2. 在 ComfyUI 中搜索节点 **「中文提示词 → Ollama 英文翻译」**，添加到画布。
3. 在「chinese_prompt」输入框输入中文描述，选择「model」，执行队列。
4. 将输出的「english_prompt」连接到「CLIP Text Encode」的 text 输入。

## 模型列表刷新

- **添加节点时**或**刷新浏览器页面**会重新从 Ollama 拉取模型列表。
- 若使用自定义 Ollama 地址，在「ollama_base_url」中填写（如 `http://192.168.1.100:11434`）。

## API（可选）

- `GET /ollama_prompt_translate/models?base_url=http://127.0.0.1:11434`  
  返回 `{"models": ["model1", "model2", ...]}`，可供自定义前端实现「刷新」按钮。

## 依赖

- 仅使用 Python 标准库 `urllib.request`、`json`，无需额外 pip 包。
- 需本机或局域网内运行 Ollama 服务（默认 `http://127.0.0.1:11434`）。
