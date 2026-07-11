# OpenBase + Traccia

**OpenBase** is the protocol for AI agent execution evidence.  
**Traccia** is the official developer SDK — add verifiable execution, replay, and evidence to any AI agent in minutes.

## 安装

```bash
pip install traccia traccia-guard traccia-eval
快速开始
bash
traccia intercept -- python your_agent.py
traccia diagnose traccia-*.evidence
三个核心命令
命令	功能
traccia intercept	拦截 Agent 执行，自动生成证据包
traccia diagnose	分析证据包，输出诊断报告
traccia guard	安全策略网关，阻止危险操作
Guard 规则
规则	检测	动作
dangerous_shell	rm -rf, sudo, chmod 777, mkfs, dd, fork bomb	BLOCK
token_spike	单次 > 100K tokens	WARN
internal_network	127.0.0.1, 192.168.x.x, 10.x.x.x, 172.16.x.x, localhost	BLOCK
项目结构
text
traccia/
├── cli/               ← CLI 入口
├── src/traccia/       ← 核心库
├── guard/             ← 安全策略网关
├── eval/              ← 评分与排行榜工具
├── dataset/           ← 基准数据集
├── tools/             ← 辅助工具
├── ARCHITECTURE.md    ← 架构定义
└── README.md
论文与数据集
论文: https://github.com/d87skg/traccia/releases/tag/v1.0.0

数据集: https://huggingface.co/datasets/vasdvae/traccia-benchmark

许可证
Apache 2.0
