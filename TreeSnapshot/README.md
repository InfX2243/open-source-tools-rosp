# TreeSnapshot

**TreeSnapshot** is a lightweight Python utility that converts an existing directory structure into a clean, Markdown-friendly tree representation.

It is designed to work alongside tools such as **ScaffoldTree**, which performs the reverse operation:

```text
TreeSnapshot
Filesystem → Tree

ScaffoldTree
Tree → Filesystem
```

Together, they provide a simple way to capture, share, recreate, and document project structures.

## Features

- Generate a directory tree from any existing directory.
- Automatically distinguish _files_ and _directories_.
- Directories are represented with a trailing `/`.
- No hardcoded file-extension list is required.
- Automatically ignore unwanted files and directories.
- Support wildcard ignore patterns such as `*.log` and `*.pyc`.
- Support a project-level `.treeignore` file.
- Add additional ignore patterns from the command line.
- Generate Markdown output.
- Preserve the generated tree in a format compatible with **ScaffoldTree**.
- Ignore common generated and system files by default.
- No external Python dependencies.

## Requirements

- Python **3.8+**
- No external dependencies

## Installation

TreeSnapshot does not require installation.

Clone or download the project and run:

```bash
python tree_snapshot.py ./my-project
```

## Basic Usage

Pass the directory you want to inspect:

```bash
python tree_snapshot.py ./my-project
```

By default, TreeSnapshot creates:

```text
directory_structure.md
```

The generated Markdown will look like:

````markdown
# Directory Structure for `/path/to/my-project`

```text
my-project/
├── src/
│   ├── components/
│   │   ├── Button.tsx
│   │   └── Modal.tsx
│   ├── pages/
│   │   └── Home.tsx
│   └── main.tsx
├── tests/
│   └── test_main.py
├── package.json
└── README.md
```
````

## Output File

You can specify a custom output file with `-o` or `--output`:

```bash
python tree_snapshot.py ./my-project --output structure.md
```

Or:

```bash
python tree_snapshot.py ./my-project -o structure.md
```

For example:

```text
my-project/
├── src/
├── tests/
├── package.json
└── README.md
```

can be written to:

```text
docs/project-structure.md
```

using:

```bash
python tree_snapshot.py ./my-project -o docs/project-structure.md
```

## Directory and File Detection

TreeSnapshot does not use file extensions to determine whether something is a file or directory.

It already knows this from the filesystem itself.

For example:

```text
src/
components/
utils/
```

are directories and are written with `/`.

Files such as:

```text
README
Dockerfile
Makefile
.env
package.json
main.py
App.tsx
config.yaml
```

are written without `/`.

This makes the generated format compatible with **ScaffoldTree**, where the rule is:

```text
name ending with /     → directory
name without /         → file
```

## Ignoring Files and Directories

Real-world projects often contain directories that are not useful when documenting or recreating a project structure.

Examples include:

```text
node_modules/
dist/
build/
coverage/
__pycache__/
.git/
```

TreeSnapshot allows these entries to be ignored.

## `.treeignore`

The recommended way to configure ignored files and directories is with a `.treeignore` file.

Create a file named:

```text
.treeignore
```

in the root of the project being scanned.

Example:

```text
# Version control
.git/

# Dependencies
node_modules/
vendor/

# Build output
dist/
build/
out/
target/

# Python
__pycache__/
*.pyc
.venv/
venv/

# Environment files
.env
.env.*

# IDEs
.vscode/
.idea/

# Operating system files
.DS_Store
Thumbs.db

# Logs
*.log

# Coverage
coverage/
htmlcov/
```

Then simply run:

```bash
python tree_snapshot.py ./my-project
```

TreeSnapshot automatically looks for:

```text
my-project/.treeignore
```

and loads the ignore patterns from it.

## `.treeignore` Syntax

Each line represents one ignore pattern.

### Ignore a directory

```text
node_modules/
dist/
build/
```

### Ignore a specific file

```text
.env
secret.json
```

### Ignore files by pattern

```text
*.log
*.tmp
*.pyc
```

### Ignore directories by name

```text
node_modules
dist
coverage
```

### Comments

Lines beginning with `#` are treated as comments:

```text
# Dependencies
node_modules/

# Build output
dist/
```

### Empty Lines

Empty lines are ignored:

```text
node_modules/


dist/

*.log
```

This is useful for keeping `.treeignore` organized.

## Built-in Ignore Patterns

TreeSnapshot comes with a small set of default ignore patterns:

```text
.git
__pycache__
.DS_Store
```

These are ignored automatically.

You do not need to add them to `.treeignore`.

You can still include them in `.treeignore` if you want the configuration to explicitly document them.

## Additional Ignore Patterns

You can add extra ignore patterns directly from the command line using `-i` or `--ignore`.

For example:

```bash
python tree_snapshot.py ./my-project \
    --ignore coverage/ \
    --ignore "*.tmp"
```

You can specify `--ignore` multiple times.

For example:

```bash
python tree_snapshot.py ./my-project \
    -i node_modules/ \
    -i dist/ \
    -i build/ \
    -i "*.log"
```

These patterns are added to the patterns loaded from `.treeignore`.

## Custom Ignore File

Although `.treeignore` is the default, you can provide another ignore file using:

```bash
--ignore-file
```

Example:

```bash
python tree_snapshot.py ./my-project --ignore-file custom.ignore
```

This is useful when you want to maintain different ignore configurations for different purposes.

For example:

```text
.treeignore
documentation.ignore
minimal.ignore
```

## `.treeignore` Is Included in the Tree

The `.treeignore` file itself is treated as a normal project file.

For example, if your project contains:

```text
my-project/
├── .treeignore
├── src/
├── node_modules/
├── dist/
└── README.md
```

and `.treeignore` contains:

```text
node_modules/
dist/
```

the generated tree will be:

```text
my-project/
├── .treeignore
├── src/
└── README.md
```

The ignore configuration remains visible so anyone looking at the generated structure knows that the project uses a `.treeignore` file.

## Example Project

Suppose the project looks like this:

```text
my-web-app/
├── src/
│   ├── components/
│   │   ├── Button.tsx
│   │   └── Modal.tsx
│   ├── pages/
│   │   ├── Home.tsx
│   │   └── About.tsx
│   └── main.tsx
├── public/
│   └── images/
│       └── logo.svg
├── tests/
│   └── components/
│       └── Button.test.tsx
├── node_modules/
├── dist/
├── .git/
├── .treeignore
├── package.json
├── tsconfig.json
└── README.md
```

With a `.treeignore` containing:

```text
node_modules/
dist/
.git/
```

running:

```bash
python tree_snapshot.py ./my-web-app
```

produces:

````markdown
# Directory Structure for `/path/to/my-web-app`

```text
my-web-app/
├── src/
│   ├── components/
│   │   ├── Button.tsx
│   │   └── Modal.tsx
│   ├── pages/
│   │   ├── About.tsx
│   │   └── Home.tsx
│   └── main.tsx
├── public/
│   └── images/
│       └── logo.svg
├── tests/
│   └── components/
│       └── Button.test.tsx
├── .treeignore
├── package.json
├── tsconfig.json
└── README.md
```
````

The generated structure contains only the meaningful project files.

## Command Reference

### Generate a tree

```bash
python tree_snapshot.py ./my-project
```

### Specify output file

```bash
python tree_snapshot.py ./my-project -o structure.md
```

### Add an ignore pattern

```bash
python tree_snapshot.py ./my-project -i node_modules/
```

### Add multiple ignore patterns

```bash
python tree_snapshot.py ./my-project \
    -i node_modules/ \
    -i dist/ \
    -i "*.log"
```

### Use a custom ignore file

```bash
python tree_snapshot.py ./my-project --ignore-file custom.ignore
```

### Combine `.treeignore` with command-line patterns

```bash
python tree_snapshot.py ./my-project \
    --ignore coverage/ \
    --ignore "*.tmp"
```

## Project Structure

A typical TreeSnapshot project can look like:

```text
tree-snapshot/
├── tree_snapshot.py
├── .treeignore
├── README.md
└── examples/
    └── example.txt
```

## Example Input

The `examples/example.txt` file can contain a representative project structure:

```text
my-web-app/
│
├── src/
│   ├── components/
│   │   ├── Button.tsx
│   │   ├── Modal.tsx
│   │   └── index.ts
│   │
│   ├── pages/
│   │   ├── Home.tsx
│   │   ├── About.tsx
│   │   └── NotFound.tsx
│   │
│   ├── styles/
│   │   ├── globals.css
│   │   └── variables.css
│   │
│   └── main.tsx
│
├── public/
│   ├── images/
│   │   └── logo.svg
│   └── favicon.ico
│
├── tests/
│   ├── components/
│   │   └── Button.test.tsx
│   └── utils/
│       └── format.test.ts
│
├── docs/
│   ├── README.md
│   └── architecture.md
│
├── config/
│   ├── development.yaml
│   └── production.yaml
│
├── .env
├── .gitignore
├── Dockerfile
├── Makefile
├── package.json
├── tsconfig.json
└── README
```

## Working With ScaffoldTree

TreeSnapshot is designed to work particularly well with **ScaffoldTree**.

### TreeSnapshot

Converts an existing project into a tree:

```text
Filesystem
    ↓
TreeSnapshot
    ↓
Markdown Tree
```

### ScaffoldTree

Converts a tree back into files and directories:

```text
Markdown Tree
    ↓
ScaffoldTree
    ↓
Filesystem
```

This creates a useful workflow:

```text
Existing Project
       │
       ▼
  TreeSnapshot
       │
       ▼
directory_structure.md
       │
       ▼
  ScaffoldTree
       │
       ▼
New Project Structure
```

This can be useful for:

- _Documenting project architecture_
- _Sharing project structures_
- _Creating project templates_
- _Recreating directory structures_
- _Providing project context to AI tools_
- _Creating reproducible scaffolds_
- _Inspecting unfamiliar repositories_

## Design Philosophy

TreeSnapshot intentionally keeps the format simple.

There is no dependency on a predefined list of extensions.

The filesystem already knows whether an entry is a file or directory, so TreeSnapshot simply preserves that information in the generated representation.

The convention is:

```text
directory/     → directory
file.ext       → file
README         → file
Dockerfile     → file
.env           → file
```

This makes the output predictable and easy for both humans and other tools to understand.

## Limitations

TreeSnapshot is intended to capture **directory structure**, not file contents.

It does not:

- Read or modify file contents.
- Copy files.
- Generate source code.
- Analyze project dependencies.
- Determine whether a file is important.
- Automatically infer which project files should be ignored beyond the configured defaults.

It simply creates a structured representation of the filesystem.

## License

Add your preferred license here.

For example:

```text
MIT License
```

or replace this section with the full license text if the project is distributed publicly.

## Contributing

Contributions are welcome.

If you find a bug or have an idea for improving TreeSnapshot, consider opening an issue or submitting a pull request.

Before submitting changes, make sure the existing functionality continues to work and that new behavior is documented in the README.

## Summary

**TreeSnapshot** converts:

```text
Filesystem
    ↓
Directory Tree
    ↓
Markdown
```

while **ScaffoldTree** performs the reverse:

```text
Markdown Tree
    ↓
Directory Tree
    ↓
Filesystem
```

Together, they provide a simple and portable way to **capture and recreate project structures**.
