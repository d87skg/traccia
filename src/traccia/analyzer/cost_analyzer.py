"""Simple cost estimator for agent execution traces."""

# Approximate pricing per 1K tokens (USD, 2026 estimates)
MODEL_PRICING = {
    "gpt-5.5": {"input": 0.003, "output": 0.006},
    "gpt-4.1": {"input": 0.002, "output": 0.004},
    "claude-4": {"input": 0.003, "output": 0.006},
    "claude-3.5": {"input": 0.002, "output": 0.004},
    "kimi-k2.7": {"input": 0.001, "output": 0.002},
    "llama-4": {"input": 0.0005, "output": 0.001},
    "default": {"input": 0.002, "output": 0.004},
}

def estimate_cost(model: str, input_tokens: int, output_tokens: int = 0) -> float:
    """Estimate cost in USD for a single LLM call."""
    pricing = MODEL_PRICING.get(model, MODEL_PRICING["default"])
    return (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1000

def analyze_costs(events: list) -> dict:
    """Analyze costs across all events in an execution trace."""
    cost_by_model = {}
    total_cost = 0.0

    for event in events:
        model = event.get("payload", {}).get("model", "default")
        input_tokens = event.get("payload", {}).get("token_count", 0)
        output_tokens = event.get("payload", {}).get("output_tokens", 0)

        cost = estimate_cost(model, input_tokens, output_tokens)
        total_cost += cost

        if model not in cost_by_model:
            cost_by_model[model] = {"cost": 0.0, "calls": 0, "tokens": 0}
        cost_by_model[model]["cost"] += cost
        cost_by_model[model]["calls"] += 1
        cost_by_model[model]["tokens"] += input_tokens + output_tokens

    return {
        "total_cost": round(total_cost, 4),
        "cost_by_model": {k: {**v, "cost": round(v["cost"], 4)} for k, v in cost_by_model.items()},
        "primary_cost_driver": max(cost_by_model, key=lambda x: cost_by_model[x]["cost"]) if cost_by_model else None,
    }
