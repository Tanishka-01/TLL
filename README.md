# TLL — Tight-Lipped Layer

A privacy-aware routing middleware that sits between a user and cloud AI services. Before sending a query to any cloud provider, TLL evaluates its sensitivity relative to the user's professional profile and decides whether it should stay local or be forwarded to the cloud.

---

## How It Works

Every query passes through two layers:

1. **Sensitivity scorer** — a local LLM (Ollama) evaluates the query against the user's profile and assigns a routing decision: LOCAL, Claude, OpenAI, or Gemini.
2. **Correlation engine** — if the query is headed to cloud, TLL checks the session history to see whether this query combined with what the cloud has already seen would create a dangerous pattern. If so, it overrides to LOCAL.

Queries are only sent to a cloud service when they are genuinely non-sensitive *and* their combination with prior session queries does not reveal anything protected.

---

## Supported Profiles

| Profile | What TLL Protects |
|---|---|
| Lawyer | Client identity, case strategy, privileged communications |
| Journalist | Source identity, source meeting details, investigation targets |
| Healthcare | Patient identity combined with medical information (HIPAA) |
| Researcher | Unpublished results, proprietary methods, competitive benchmarks |

---

## Quick Start

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com) running locally with `capybarahermes-2.5-mistral-7b.Q4_0` pulled

```bash
pip install -r requirements.txt
ollama pull capybarahermes-2.5-mistral-7b.Q4_0
```

### Route a single query

```bash
python3 tll.py --profile Lawyer --query "My client is suing PharmaCorp"
python3 tll.py --profile Journalist --query "Good restaurants in Georgetown DC"
python3 tll.py --profile Healthcare --query "Jamie Chen, 16, active suicidal ideation"
python3 tll.py --profile Researcher --query "Our model outperforms AlphaFold by 23%"
```

### Use sessions (enables correlation tracking)

```bash
python3 tll.py --profile Journalist --query "Senator Williams committee assignments" --session my_session
python3 tll.py --profile Journalist --query "Good restaurants in Georgetown" --session my_session
# Second query gets blocked — location + senator in same session
```

### Run as an HTTP server

```bash
python3 server.py --host 0.0.0.0 --port 8080
```

```bash
curl -X POST http://localhost:8080/route \
  -H "Content-Type: application/json" \
  -d '{"query": "My client is being investigated", "profile": "Lawyer", "session": "my_session"}'
```

---

## Options

### `tll.py`

| Flag | Default | Description |
|---|---|---|
| `--profile` | required | User profile (Lawyer, Journalist, Healthcare, Researcher) |
| `--query` | required | The query to route |
| `--session` | `default` | Session ID for correlation tracking |
| `--model` | `capybarahermes-2.5-mistral-7b.Q4_0:latest` | Ollama model |
| `--url` | `http://localhost:11434` | Ollama API URL |
| `--no-correlation` | off | Skip the correlation check |
| `--verbose` | off | Print full metadata to stderr |

### `server.py`

| Flag | Default | Description |
|---|---|---|
| `--host` | `0.0.0.0` | Bind host |
| `--port` | `8080` | Listen port |
| `--model` | same as tll.py | Ollama model |
| `--url` | same as tll.py | Ollama API URL |

---

## Evaluation

Run adversary simulation across all scenarios and routing methods:

```bash
# All scenarios, all methods
python3 -m evaluation.runner

# Single scenario
python3 -m evaluation.runner --scenario journalist_source_meeting

# Single method
python3 -m evaluation.runner --method tll

# Verbose output
python3 -m evaluation.runner --verbose
```

Results are saved to `evaluation/results/` as JSON and Markdown.

---

## Project Structure

```
TLL/
├── tll.py                   # Core routing engine
├── correlation.py           # Session-aware correlation checker
├── server.py                # HTTP server wrapper
├── config.toml              # Configuration
├── requirements.txt
├── logs/
│   ├── routing.log          # JSONL log of all routing decisions
│   └── sessions/            # Per-session correlation history
└── evaluation/
    ├── runner.py             # Adversary simulation runner
    ├── adversary.py          # Adversary reconstruction model
    ├── scorer.py             # Reconstruction scoring
    ├── routers.py            # Routing method implementations
    ├── models.py             # Data models
    ├── scenarios/            # Scenario definitions (JSON)
    └── results/              # Evaluation outputs
```

---

## Configuration

`config.toml` holds model and service defaults. Override at runtime with CLI flags.
