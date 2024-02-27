"""Generate the code reference pages and navigation."""
from pathlib import Path

import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()

root = Path(__file__).parent.parent
src = root / "dynaconf"  # (1)!

for path in sorted(src.rglob("*.py")):  # (2)!
    module_path = path.relative_to(root).with_suffix("")
    doc_path = path.relative_to(root).with_suffix(".md")  # (3)!
    full_doc_path = Path("reference", doc_path).resolve()  # (4)!

    parts = tuple(module_path.parts)

    if parts[-1] == "__init__":
        parts = parts[:-1]
        doc_path = doc_path.with_name("index.md")
        full_doc_path = full_doc_path.with_name("index.md")
    elif parts[-1] == "__main__":
        continue

    nav[parts] = doc_path.as_posix()

    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
        identifier = ".".join(parts)
        print("::: " + identifier, file=fd)

    mkdocs_gen_files.set_edit_path(full_doc_path, path)

with mkdocs_gen_files.open(
    Path("reference/SUMMARY.md").resolve(),  # (5)!
    "w",
) as nav_file:
    nav_file.writelines(nav.build_literate_nav())
