# costpilot

Lightweight LLM cost tracking SDK. Three lines of code to track all your AI spending.

CostPilot wraps your OpenAI or Anthropic client and records every call — model,
tokens, cost, latency and any tags you attach — then ships the data to your
CostPilot dashboard in the background. It never blocks your LLM call and never
crashes your application: if the backend is unreachable, events are dropped
silently.

## Install

```bash
pip install costpilot
```

## Usage

```python
import costpilot
import openai

costpilot.init(
    api_key="cp_proj_abc123def456",
    endpoint="http://localhost:8787",
    default_tags={"service": "chatbot"},
)

client = costpilot.wrap_openai(openai.OpenAI())

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello"}],
)
```

### Per-call tags

Attach feature or user level tags through the `x-costpilot-tags` header. The
format is a comma separated list of `key:value` pairs:

```python
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Summarize this document"}],
    extra_headers={"x-costpilot-tags": "feature:doc-summary,user:alice"},
)
```

### Anthropic

```python
import anthropic

client = costpilot.wrap_anthropic(anthropic.Anthropic())

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
)
```

### Short-lived scripts

Events flush every few seconds in the background. For a script that exits
quickly, flush explicitly before you leave:

```python
costpilot.flush()
```

## How it works

- `init()` starts a single background client with a daemon flush thread.
- Each wrapped call enqueues an `Event`; the queue flushes on a timer or once it
  fills a batch.
- Sending happens on throwaway threads, so your request path is never blocked.

## License

MIT
