from setuptools import setup, find_packages

setup(
    name="traccia",
    version="0.2.0",
    description="AI Agent 行为闭环控制 CLI",
    packages=find_packages(where="src/traccia") + find_packages(where="."),
    package_dir={"": "src/traccia"},
    py_modules=["cli.traccia"],
    install_requires=[
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "traccia=cli.traccia:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
)
