from pathlib import Path
import argparse
import re


def parse_tree_line(line: str):
    """
    Parse a single tree-style line.

    Tree decoration-only lines are ignored.

    Examples:

        docs/
        │
        ├── src/
        │   │
        │   ├── main.py
        │   └── utils.py
        └── README.md

    Returns:
        (depth, name)

    Or:
        (None, None) for blank/decorative lines.
    """

    line = line.rstrip()

    if not line.strip():
        return None, None

    # -------------------------------------------------------------
    # Ignore lines that contain only tree decoration characters.
    #
    # Examples:
    #
    #     │
    #     │   │
    #     │       │
    #     ───
    #
    # These are formatting characters, not files/directories.
    # -------------------------------------------------------------
    decoration_only = re.fullmatch(
        r"[\s│├└─—]+",
        line
    )

    if decoration_only:
        return None, None

    # -------------------------------------------------------------
    # Root-level entry
    #
    # Example:
    #
    #     docs/
    #
    # or:
    #
    #     README.md
    # -------------------------------------------------------------
    if not re.search(r"[├└]", line):
        name = line.strip()

        # A line containing only "|" or similar decoration
        # should never become a file.
        if not name or all(char in "│├└─— \t" for char in name):
            return None, None

        return 0, name

    # -------------------------------------------------------------
    # Tree entry
    #
    # Examples:
    #
    #     ├── src/
    #     └── README.md
    #     │   ├── main.py
    # -------------------------------------------------------------
    match = re.match(
        r"^(.*?)((?:├──)|(?:└──))\s*(.*)$",
        line
    )

    if not match:
        return None, None

    prefix = match.group(1)
    name = match.group(3).strip()

    # Empty names are not valid entries.
    if not name:
        return None, None

    # Calculate nesting depth.
    depth = len(prefix) // 4 + 1

    return depth, name

def is_directory(name: str) -> bool:
    """
    A directory is identified ONLY by the trailing '/'.
    """
    return name.endswith("/")


def create_structure(tree: str, output_dir: str = "."):
    """
    Create the directory/file structure described by a tree string.
    """

    output_root = Path(output_dir).resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    # Maps depth to the directory path at that depth.
    #
    # Example:
    #
    # depth 0 -> /project/docs
    # depth 1 -> /project/docs/01-product
    #
    directory_stack = {}

    lines = tree.splitlines()

    for line_number, line in enumerate(lines, start=1):

        depth, name = parse_tree_line(line)

        # Ignore blank / unsupported lines.
        if name is None:
            continue

        # ---------------------------------------------------------
        # ROOT ENTRY
        # ---------------------------------------------------------
        if depth == 0 and not directory_stack:

            if not is_directory(name):
                raise ValueError(
                    f"Line {line_number}: "
                    f"The root entry must be a directory ending with '/'. "
                    f"Got: {name}"
                )

            directory_name = name.rstrip("/")

            root_path = output_root / directory_name

            root_path.mkdir(
                parents=True,
                exist_ok=True
            )

            directory_stack[0] = root_path

            print(f"[DIR ] {root_path}")

            continue

        # ---------------------------------------------------------
        # FIND PARENT DIRECTORY
        # ---------------------------------------------------------
        parent_depth = depth - 1

        # A depth of 0 means the item belongs directly
        # inside the root directory.
        if depth == 0:
            parent = directory_stack[0]
        else:
            if parent_depth not in directory_stack:
                raise ValueError(
                    f"Line {line_number}: "
                    f"Could not determine parent directory for '{name}'."
                )

            parent = directory_stack[parent_depth]

        # ---------------------------------------------------------
        # DIRECTORY
        # ---------------------------------------------------------
        if is_directory(name):

            directory_name = name.rstrip("/")

            path = parent / directory_name

            path.mkdir(
                parents=True,
                exist_ok=True
            )

            directory_stack[depth] = path

            # Remove deeper paths from the stack.
            #
            # Example:
            #
            # docs/
            # ├── src/
            # │   ├── components/
            # │   └── utils/
            # └── tests/
            #
            # When we reach tests/, components/ and utils/
            # should no longer be considered active parents.
            for d in list(directory_stack):
                if d > depth:
                    del directory_stack[d]

            print(f"[DIR ] {path}")

        # ---------------------------------------------------------
        # FILE
        # ---------------------------------------------------------
        else:

            path = parent / name

            # Make sure the parent exists.
            path.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            # Create an empty file.
            #
            # touch(exist_ok=True) means:
            # - create it if it doesn't exist
            # - leave an existing file untouched
            path.touch(exist_ok=True)

            print(f"[FILE] {path}")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Create directories and files from a tree-style "
            "directory structure."
        )
    )

    parser.add_argument(
        "tree_file",
        help=(
            "Path to a text file containing the directory tree. "
            "Use '-' to read from stdin."
        )
    )

    parser.add_argument(
        "-o",
        "--output",
        default=".",
        help=(
            "Directory where the structure should be created. "
            "Defaults to the current directory."
        )
    )

    args = parser.parse_args()

    # -------------------------------------------------------------
    # Read input
    # -------------------------------------------------------------
    if args.tree_file == "-":
        import sys

        tree = sys.stdin.read()

    else:
        tree_path = Path(args.tree_file)

        if not tree_path.exists():
            raise FileNotFoundError(
                f"Tree file does not exist: {tree_path}"
            )

        if not tree_path.is_file():
            raise ValueError(
                f"Expected a file containing the tree: {tree_path}"
            )

        tree = tree_path.read_text(
            encoding="utf-8"
        )

    # -------------------------------------------------------------
    # Create structure
    # -------------------------------------------------------------
    create_structure(
        tree=tree,
        output_dir=args.output
    )


if __name__ == "__main__":
    main()
