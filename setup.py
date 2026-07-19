from setuptools import setup, find_packages

setup(
    name="traccia-sdk",
    version="0.3.2",
    description="Official OpenBase Developer SDK - add verifiable execution, replay, and evidence to any AI agent",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="OpenBase Project",
    url="https://github.com/d87skg/traccia",
    packages=["traccia_sdk"] + find_packages(where="traccia/sdk/python"),
    package_dir={"traccia_sdk": "traccia/sdk/python/traccia_sdk"},
    scripts=["cli/traccia.py"],
    install_requires=["requests"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.10",
)
