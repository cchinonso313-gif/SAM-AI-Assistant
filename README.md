# NOVA - Agentic AI Assistant

**NOVA** (formerly SAM) is a sophisticated, locally-running AI assistant that integrates Gemini and Groq APIs to provide autonomous task execution, voice recognition, code generation, and system monitoring. The name defaults to `NOVA` and can be overridden with the `NOVA_NAME` (or legacy `SAM_NAME`) environment variable.

## Features

✅ **Autonomous Agent** - Plan → act → observe → reflect loop over a modular tool registry  
✅ **Modular Tools** - File ops, project/website scaffolding, safe shell, web fetch + web search, system info  
✅ **Desktop Automation** - Mouse, keyboard, screenshots, window focus, clipboard  
✅ **Sandboxed Code Execution** - Run generated Python in an isolated subprocess  
✅ **Semantic Long-Term Memory** - Vector recall of relevant facts across sessions  
✅ **Multi-Brain Routing** - Pluggable LLM "brains" (Gemini, Groq, and more) with automatic failover  
✅ **Glowing Desktop Indicator** - Smooth pulsing, always-on-top status light (top-center) that changes color by state (idle/active/listening/thinking/speaking)  
✅ **Voice Recognition & Response** - Real-time voice input/output  
✅ **Code Generation** - AI-powered coding assistance  
✅ **Task Execution** - Execute commands and automate workflows (with safety filters)  
✅ **System Monitoring** - Monitor system resources and activities  
✅ **Local Storage** - Encrypted conversation history  
✅ **Cross-Platform** - Windows, Mac, Linux, and Android support  
✅ **Adaptive Responses** - Context-aware, mood-based interactions  

### Architecture (modular for future self-improvement)

```
backend/
  agent/        # autonomous agent loop, tool registry, safety
    tools/      # one module per capability (file, project, shell, web, gui, clipboard, code, system)
  brains/       # pluggable LLM backends + failover router
  apis/         # provider SDK handlers (Gemini, Groq)
  core/         # engine, memory, semantic memory, voice, task executor
  features/     # web dashboard, scheduler
desktop/        # glowing status indicator, system monitor
```

Add a new capability by dropping a `register(registry)` module in `backend/agent/tools/`. Add a new LLM by subclassing `Brain` and calling `router.register(...)`.

## Installation

### Prerequisites
- Python 3.10+
- Gemini API Key
- Groq API Key
- Microphone & Speakers

### Setup

1. **Clone Repository**
```bash
git clone https://github.com/cchinonso313-gif/SAM-AI-Assistant.git
cd SAM-AI-Assistant
```

2. **Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure API Keys**
```bash
cp .env.example .env
# Edit .env with your Gemini and Groq API keys
export GEMINI_API_KEY="your-key"
export GROQ_API_KEY="your-key"
```

5. **Run SAM**
```bash
python backend/main.py
```

## Quick Start

```bash
# Voice activation (say: "Hey SAM")
python backend/main.py

# Type commands
SAM> write a python function for factorial
SAM> generate a REST API in FastAPI
SAM> explain quantum computing
SAM> create a todo app in React
```

## Architecture

- **AI Engine** - Core orchestration (ai_engine.py)
- **Voice Processor** - Speech-to-text & Text-to-speech (voice_processor.py)
- **Task Executor** - Command execution (task_executor.py)
- **Memory Manager** - Conversation history & learning (memory_manager.py)
- **API Manager** - Gemini/Groq failover (api_manager.py)
- **Desktop Indicator** - Visual status (ui_indicator.py)
- **System Monitor** - Resource tracking (system_monitor.py)

## Configuration

Edit `.env` file:
```
GEMINI_API_KEY=your-key
GROQ_API_KEY=your-key
VOICE_ENABLED=True
INDICATOR_ENABLED=True
ENCRYPTION_ENABLED=True
```

## API Integration

### Gemini (Code & Complex Tasks)
```python
Model: gemini-2.0-flash
Best for: Code generation, detailed analysis
```

### Groq (General Tasks)
```python
Model: mixtral-8x7b-32768
Best for: General questions, quick responses
```

## Security Features

✅ End-to-end encryption for stored conversations  
✅ Local processing (minimal cloud data)  
✅ Secure API key storage  
✅ Blocked keywords for dangerous operations  
✅ Auto-cleanup of old history  

## Troubleshooting

| Issue | Solution |
|-------|----------|
| API Key Errors | Check .env file and verify API keys |
| Voice Not Working | Check microphone permissions |
| Indicator Not Showing | Run with display server (X11/Wayland) |
| Memory Issues | Clear cache: `python backend/core/memory_manager.py --clear` |

## What's Next?

- [ ] Android app integration
- [ ] Web dashboard
- [ ] Advanced task scheduling
- [ ] Multi-language support
- [ ] Custom training

## Contributing

Contributions welcome! Please fork and submit pull requests.

## License

MIT License - See LICENSE file

---

**Made with ❤️ by cchinonso313-gif**