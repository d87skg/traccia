from setuptools import setup, find_packages

setup(
    name="traccia-guard",
    version="0.1.0",
    description="AI Agent 安全气囊 — 拦截危险命令、Token异常、内网访问",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Traccia Team",
    python_requires=">=3.10",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
