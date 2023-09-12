from setuptools import setup

with open("requirements.txt") as f:
    requirements = f.read().splitlines()
    requirements = [r for r in requirements if not r.startswith("git+")]

PROJECT_NAME = "pdf_paragraphs_extraction"

setup(
    name=PROJECT_NAME,
    packages=["paragraph_extraction_trainer"],
    package_dir={"": "src"},
    version="0.14",
    url="https://github.com/huridocs/pdf_paragraphs_extraction",
    author="HURIDOCS",
    description="Service for extracting paragraphs from PDFs.",
    install_requires=requirements,
    dependency_links=["git+https://github.com/huridocs/pdf-tokens-type-labeler@8376eb243f85fa389242585e6559d518ea936a3f"],
)
