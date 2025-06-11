from setuptools import setup, find_packages

setup(
    name="sales_rag_app",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "python-dotenv",
        "jinja2",
    ],
) 