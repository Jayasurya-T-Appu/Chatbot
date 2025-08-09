from setuptools import setup, find_packages
import os

# Read README.md for long description
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "A professional AI-powered RAG chatbot SaaS platform"

# Read requirements.txt for dependencies
try:
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
except FileNotFoundError:
    requirements = []

# Find all packages in the src directory
packages = find_packages(where="src")

setup(
    name="chatbot-saas",
    version="1.0.0",
    author="ChatBot SaaS Team",
    description="A professional AI-powered RAG chatbot SaaS platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/chatbot-saas",
    package_dir={"": "src"},
    packages=packages,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications :: Chat",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    include_package_data=True,
    package_data={
        "": ["*.json", "*.yaml", "*.yml"],
        "static": ["js/*", "css/*", "html/*", "images/*"],
    },
    # Additional metadata for deployment
    keywords="chatbot, ai, rag, saas, fastapi, chromadb",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/chatbot-saas/issues",
        "Source": "https://github.com/yourusername/chatbot-saas",
        "Documentation": "https://github.com/yourusername/chatbot-saas/docs",
    },
    # For AWS deployment
    zip_safe=False,  # Required for some AWS services
)
