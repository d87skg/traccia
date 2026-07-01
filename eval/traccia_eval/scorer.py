def traccia_score(entry):
    ev = entry["evaluation"]
    res = entry["residual"]
    return (
        0.3 * ev["correctness"] +
        0.2 * ev["stability_score"] +
        0.2 * ev["recoverability"] +
        0.2 * (1 - res["entropy"]) +
        0.1 * (1 - res["structural_residual"])
    )
