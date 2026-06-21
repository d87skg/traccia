class BlockedActionError(Exception):
    pass

RULES = [
    {
        "name": "dangerous_shell",
        "pattern": ["rm -rf", "sudo", "chmod 777", ":(){ :|:& };:", "mkfs.", "dd if="],
        "action": "BLOCK",
        "message": "危险Shell命令已被阻止"
    },
    {
        "name": "token_spike",
        "condition": lambda e: e.get("token_count", 0) > 100000,
        "action": "WARN",
        "message": "Token消耗异常（>100K），请检查是否死循环"
    },
    {
        "name": "internal_network",
        "pattern": ["127.0.0.1", "192.168.", "10.", "172.16.", "localhost"],
        "action": "BLOCK",
        "message": "禁止访问内网地址"
    }
]

def evaluate(event: dict):
    event_str = str(event).lower()
    
    for rule in RULES:
        if "pattern" in rule:
            for p in rule["pattern"]:
                if p.lower() in event_str:
                    return rule["action"], rule["message"]
        
        if "condition" in rule:
            try:
                if rule["condition"](event):
                    return rule["action"], rule["message"]
            except:
                pass
    
    return "ALLOW", None
