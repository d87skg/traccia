from setuptools import setup, find_packages

setup(
    name="traccia-eval",
    version="0.1.0",
    description="Traccia Agent Execution Benchmark — scoring and leaderboard",
    packages=find_packages(),
    install_requires=["datasets", "huggingface_hub"],
    entry_points={
        "console_scripts": [
            "traccia-eval=traccia_eval.cli:main",
        ],
    },
)
