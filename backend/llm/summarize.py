import json, requests
from pathlib import Path
LOG = Path(__file__).resolve().parents[1] / "training_log.jsonl"
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
rounds = [json.loads(l) for l in LOG.read_text().splitlines()] if LOG.exists() else []
prompt = "Summarize these FL rounds and on-chain proofs:\n\n"+json.dumps(rounds, indent=2)
try:
    r = requests.post(OLLAMA_URL, json={"model":"llama3","prompt":prompt}); print("\n=== OLLAMA SUMMARY ===\n", r.json().get("response","(no response)"))
except Exception as e: print("Ollama request failed:", e)
