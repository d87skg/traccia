# Traccia

AI Agent 行为闭环控制与执行评测基础设施

## 安装

```bash
pip install traccia-guard    # 安全气囊
pip install traccia-eval     # 基准测试评分工具
核心能力
模块	功能	命令 / 用法
Guard	拦截危险命令、Token 异常、内网访问	pip install traccia-guard
CLI	行为闭环控制 (loop)、诊断 (diagnose)、拦截 (intercept)	traccia loop run --iterations 10
SDK	可嵌入 Agent 的残差反馈引擎	from traccia import ResidualLoop
数据集	跨运行时 Agent 执行轨迹基准（27 条, 含残差标注）	datasets.load_dataset("vasdvae/traccia-benchmark")
eval	标准化执行质量评分函数 + 排行榜生成	traccia-eval dataset.jsonl
Guard（安全气囊）
给你的 AI Agent 装个安全带。

使用
python
from traccia_guard import GuardSession, BlockedActionError

session = GuardSession("部署新版本")
session.record("read_file", {"path": "/tmp/config.yaml"})

try:
    session.record("shell_exec", {"command": "rm -rf /"})
except BlockedActionError as e:
    print(f"已拦截: {e}")

session.record("llm_call", {"token_count": 150000})
print(session.warnings)
规则
规则	检测	动作
dangerous_shell	rm -rf, sudo, chmod 777, mkfs, dd, fork bomb	BLOCK
token_spike	单次 > 100K tokens	WARN
internal_network	127.0.0.1, 192.168.x.x, 10.x.x.x, 172.16.x.x, localhost	BLOCK
CLI 快速开始
bash
# 拦截并自动生成证据包
traccia intercept -- python my_agent.py

# 分析证据包，输出诊断报告
traccia diagnose task.evidence

# 运行残差反馈闭环（自动生成训练数据）
traccia loop run --iterations 5
SDK 快速集成
python
from traccia import ResidualLoop

loop = ResidualLoop("我的 Agent 会话")
history = loop.run(iterations=3)
print(loop.state)          # 查看最新残差状态
loop.export("history.json")# 导出历史记录
数据集与基准
python
from datasets import load_dataset

dataset = load_dataset("vasdvae/traccia-benchmark")
print(dataset["train"][0])
格式：遵循 Traccia Canonical Schema v1，包含 task、execution、trajectory、residual、evaluation 六层结构。

用途：Agent 执行质量评估、运行时对比、故障模式分析、训练数据生成。

项目结构
text
traccia/
├── cli/            ← CLI 入口
├── src/traccia/    ← 核心库（recorder, residual, loop, entropy）
├── guard/          ← 安全气囊独立包
├── eval/           ← traccia-eval 评分与排行榜工具
├── dataset/        ← 基准数据集与 HF 加载器
└── tools/          ← 辅助工具（数据集构建器等）
许可证
Apache 2.0