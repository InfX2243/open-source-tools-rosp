from pathlib import Path
import argparse
import fnmatch


DEFAULT_IGNORES = {
    ".git",
    "__pycache__",
    ".DS_Store",
}


def should_ignore(path: Path, ignore_patterns: set[str]) -> bool:
    """
    Return True if the given file or directory should be ignored.

    Matching supports:
        node_modules
        node_modules/
        *.pyc
        .env
        dist
        build/
    """

    name = path.name

    for pattern in ignore_patterns:
        pattern = pattern.strip()

        if not pattern:
            continue

        # Remove trailing slash because Path.name does not contain it.
        pattern = pattern.rstrip("/")

        # Match the filename/directory name.
        if fnmatch.fnmatch(name, pattern):
            return True

        # Also allow matching the complete path.
        if fnmatch.fnmatch(str(path), pattern):
            return True

    return False


def generate_tree(
    directory: Path,
    prefix: str = "",
    ignore_patterns: set[str] | None = None,
):
    """
    Recursively generate a tree representation of a directory.

    Directories are automatically written with a trailing '/' so
    the generated tree can be consumed by ScaffoldTree.
    """

    if ignore_patterns is None:
        ignore_patterns = set()

    # Get entries while applying ignore rules.
    entries = [
        entry
        for entry in directory.iterdir()
        if not should_ignore(entry, ignore_patterns)
    ]

    # Directories first, then files.
    entries.sort(
        key=lambda x: (
            x.is_file(),
            x.name.lower(),
        )
    )

    tree_lines = []

    for index, entry in enumerate(entries):

        is_last = index == len(entries) - 1

        connector = "└── " if is_last else "├── "

        # ---------------------------------------------------------
        # Directory
        # ---------------------------------------------------------
        if entry.is_dir():
            display_name = entry.name + "/"

        # ---------------------------------------------------------
        # File
        # ---------------------------------------------------------
        else:
            display_name = entry.name

        tree_lines.append(
            prefix + connector + display_name
        )

        # ---------------------------------------------------------
        # Recurse into directories
        # ---------------------------------------------------------
        if entry.is_dir():

            extension = (
                "    "
                if is_last
                else "│   "
            )

            tree_lines.extend(
                generate_tree(
                    entry,
                    prefix + extension,
                    ignore_patterns,
                )
            )

    return tree_lines


def load_ignore_file(ignore_file: Path) -> set[str]:
    """
    Load ignore patterns from a text file.

    Empty lines and comments beginning with '#' are ignored.
    """

    if not ignore_file.exists():
        raise FileNotFoundError(
            f"Ignore file does not exist: {ignore_file}"
        )

    patterns = set()

    for line in ignore_file.read_text(
        encoding="utf-8"
    ).splitlines():

        line = line.strip()

        if not line:
            continue

        if line.startswith("#"):
            continue

        patterns.add(line)

    return patterns


def create_markdown_tree(
    target_directory: str,
    output_file: str = "directory_structure.md",
    ignore_patterns: set[str] | None = None,
):
    """
    Create a Markdown file containing the directory tree.
    """

    path = Path(target_directory).expanduser().resolve()

    if not path.exists():
        raise ValueError(
            f"Directory does not exist: {path}"
        )

    if not path.is_dir():
        raise ValueError(
            f"Path is not a directory: {path}"
        )

    if ignore_patterns is None:
        ignore_patterns = set()

    # Add built-in ignores.
    ignore_patterns = (
        DEFAULT_IGNORES | ignore_patterns
    )

    # -------------------------------------------------------------
    # Generate tree
    # -------------------------------------------------------------

    tree = [
        f"# Directory Structure for `{path}`",
        "",
        "```text",
    ]

    # Root directory also follows the ScaffoldTree convention.
    tree.append(path.name + "/")

    tree.extend(
        generate_tree(
            path,
            ignore_patterns=ignore_patterns,
        )
    )

    tree.append("```")
    tree.append("")

    # -------------------------------------------------------------
    # Write Markdown
    # -------------------------------------------------------------

    output_path = Path(output_file).expanduser()

    # If the output file is inside the target directory,
    # prevent it from appearing in the generated tree.
    output_path_resolved = output_path.resolve()

    if output_path_resolved.parent == path:
        ignore_patterns.add(output_path.name)

    # Regenerate after adding the output file to ignores.
    tree = [
        f"# Directory Structure for `{path}`",
        "",
        "```text",
        path.name + "/",
    ]

    tree.extend(
        generate_tree(
            path,
            ignore_patterns=ignore_patterns,
        )
    )

    tree.extend([
        "```",
        "",
    ])

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        "\n".join(tree),
        encoding="utf-8",
    )

    print(
        f"Markdown file created: {output_path}"
    )


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Generate a Markdown directory tree "
            "from an existing directory."
        )
    )

    parser.add_argument(
        "directory",
        help="Directory to scan.",
    )

    parser.add_argument(
        "-o",
        "--output",
        default="directory_structure.md",
        help=(
            "Output Markdown file. "
            "Defaults to directory_structure.md."
        ),
    )

    parser.add_argument(
        "-i",
        "--ignore",
        action="append",
        default=[],
        help=(
            "File or directory pattern to ignore. "
            "Can be specified multiple times."
        ),
    )

    parser.add_argument(
        "--ignore-file",
        help=(
            "Path to a file containing ignore patterns, "
            "one pattern per line."
        ),
    )

    args = parser.parse_args()

    # -------------------------------------------------------------
    # Build ignore patterns
    # -------------------------------------------------------------

    ignore_patterns = set(args.ignore)

    # Load patterns from ignore file if provided.
    if args.ignore_file:
        ignore_file = Path(
            args.ignore_file
        ).expanduser()

        ignore_patterns.update(
            load_ignore_file(ignore_file)
        )

    # -------------------------------------------------------------
    # Create Markdown tree
    # -------------------------------------------------------------

    try:
        create_markdown_tree(
            target_directory=args.directory,
            output_file=args.output,
            ignore_patterns=ignore_patterns,
        )

    except (ValueError, FileNotFoundError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()