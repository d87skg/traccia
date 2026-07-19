"""Golden Demo: broken agent with missing retry policy."""
import random

def call_payment_api(amount):
    """Simulate a payment API that sometimes fails."""
    if random.random() < 0.5:
        raise RuntimeError("Payment API timeout")
    return {"status": "ok", "amount": amount}

def agent_run():
    total = 0
    for i in range(3):
        try:
            result = call_payment_api(100)
            total += result["amount"]
            print(f"Payment {i+1}: success")
        except RuntimeError:
            print(f"Payment {i+1}: FAILED - no retry policy!")
    print(f"Total: {total} (should be 300)")
    return total

if __name__ == "__main__":
    agent_run()
