from setuptools import setup

with open("requirements.txt") as f:
    dependency_links = [r for r in f.read().splitlines() if r.startswith("git+")]
    requirements = [r for r in f.read().splitlines() if not r.startswith("git+")]

PROJECT_NAME = "pdf_paragraphs_extraction"

setup(
    name=PROJECT_NAME,
    packages=["paragraph_extraction_trainer"],
    package_dir={"": "src"},
    version="0.28",
    url="https://github.com/huridocs/pdf_paragraphs_extraction",
    author="HURIDOCS",
    description="Service for extracting paragraphs from PDFs.",
    install_requires=requirements,
    setup_requieres=requirements,
    dependency_links=dependency_links,
)
