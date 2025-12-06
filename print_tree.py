import os
from pathlib import Path

# Root of the project = where this script sits
ROOT = Path(__file__).resolve().parent

# Folders we don't want to spam the output with
EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".idea",
    ".mypy_cache",
    ".pytest_cache",
    ".streamlit",
}

def print_tree(root: Path, max_depth: int = 6):
    """
    Print a simple tree of the project structure.
    - root: starting folder
    - max_depth: how deep to go (to avoid super noisy output)
    """
    root = root.resolve()
    root_name = root.name

    lines = []

    for current_path, dirnames, filenames in os.walk(root):
        current_path = Path(current_path)
        rel = current_path.relative_to(root)

        depth = len(rel.parts)
        if depth > max_depth:
            # Don't go too deep
            dirnames[:] = []
            continue

        # Filter out excluded directories
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]

        indent = "    " * depth
        folder_label = root_name if rel == Path(".") else rel.name
        lines.append(f"{indent}{folder_label}/")

        # Show only key file types (you can add more)
        for f in sorted(filenames):
            if f.endswith((".py", ".toml", ".yaml", ".yml", ".ini", ".cfg", ".json", ".db")):
                lines.append(f"{indent}    {f}")

    tree_text = "\n".join(lines)

    # Print to console
    print(tree_text)

    # Also save to a file for easier copy-paste
    output_file = root / "project_tree.txt"
    output_file.write_text(tree_text, encoding="utf-8")
    print(f"\n\n📄 Project tree saved to: {output_file}")

if __name__ == "__main__":
    print(f"🔍 Scanning project structure under: {ROOT}")
    print_tree(ROOT, max_depth=6)
