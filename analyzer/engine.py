import sys, json
from pathlib import Path
from .classifier import extract_errors_from_package

sys.path.insert(0, str(Path(__file__).parent.parent / "traccia" / "sdk" / "python"))
from traccia.reference.python.validator import verify

class DiagnosisEngine:
    def analyze(self, package_path: str):
        result = verify(package_path)
        errors = extract_errors_from_package(package_path)
        categories = {}
        for err in errors:
            for m in err.get("matches", []):
                cat = m["category"]
                categories[cat] = categories.get(cat, 0) + 1
        root_causes = []
        for cat, count in categories.items():
            root_causes.append({"category": cat, "count": count, "confidence": min(0.5 + count * 0.15, 0.95)})
        root_causes.sort(key=lambda x: x["confidence"], reverse=True)
        cat_names = {"tool_error": "工具调用错误", "prompt_error": "Prompt参数错误", "model_error": "模型响应异常", "environment_error": "环境/网络错误"}
        summary = "未发现明显错误模式" if not root_causes else f"最可能原因：{cat_names.get(root_causes[0]['category'], root_causes[0]['category'])}（置信度 {root_causes[0]['confidence']}）"
        return {"valid": result.is_valid, "errors_found": len(errors), "root_causes": root_causes, "summary": summary}

def analyze(package_path: str):
    return DiagnosisEngine().analyze(package_path)
