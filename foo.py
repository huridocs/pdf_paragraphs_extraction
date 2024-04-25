from pathlib import Path

if __name__ == "__main__":
    path = Path("requirements.txt")
    dependency_links = [r for r in path.read_text().splitlines() if r.startswith("git+")]
    requirements = [r for r in path.read_text().splitlines() if not r.startswith("git+")]
    print(requirements)
