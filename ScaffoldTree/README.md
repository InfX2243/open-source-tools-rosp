# Directory Structure Generator

A small Python utility that creates a complete directory and file structure from a tree-style text description.

## How It Works

The program uses one simple rule to distinguish directories from files:

- **Ends with `/` → Directory**
- **Does not end with `/` → File**

The program does **not** require you to specify or maintain a list of file extensions.

For example:

```text
my-project/
├── src/
│   ├── main.py
│   ├── README
│   └── config.yaml
├── .gitignore
├── Dockerfile
└── package.json
```

The program understands:

```text
my-project/  → directory
src/         → directory
main.py      → file
README       → file
config.yaml  → file
.gitignore   → file
Dockerfile   → file
package.json → file
```

## Requirements

- Python 3.8+
- No external dependencies

## Usage

### 1. Create the tree definition

Create a text file, for example:

```text
structure.txt
```

Add your desired directory structure:

```text
docs/
│
├── 00-project/
│   ├── project-overview.md
│   ├── product-vision.md
│   └── terminology.md
│
├── 01-product/
│   ├── users-and-personas.md
│   └── requirements.md
│
├── 02-ux/
│   ├── navigation.md
│   └── user-flows.md
│
└── README.md
```

### 2. Run the program

```bash
python structure_generator.py structure.txt
```

The program will create the structure in the current directory.

### 3. Specify an output directory

You can choose where the structure should be created:

```bash
python structure_generator.py structure.txt --output ./my-project
```

Or:

```bash
python structure_generator.py structure.txt -o ./my-project
```

## Reading From Standard Input

You can also pipe a tree directly into the program:

```bash
cat structure.txt | python structure_generator.py -
```

On Windows PowerShell:

```powershell
Get-Content structure.txt | python structure_generator.py -
```

## Existing Files and Directories

The program uses `exist_ok=True` when creating directories and files.

This means running the program multiple times is safe.

Existing directories are kept, and existing files are **not overwritten**.

## Tree Formatting

The program understands the common tree format:

```text
project/
├── src/
│   ├── main.py
│   └── utils.py
├── tests/
│   └── test_main.py
└── README.md
```

The characters:

```text
├──
└──
│
```

are only used to describe the hierarchy. They are not created as part of the filenames.

## Important Rule

Always put `/` after directory names.

Correct:

```text
src/
components/
utils/
```

Incorrect:

```text
src
components
utils
```

Without the trailing `/`, the program will interpret the entry as a file.

## Example

Given:

```text
my-app/
├── backend/
│   ├── main.py
│   └── config.yaml
├── frontend/
│   ├── src/
│   │   └── App.tsx
│   └── package.json
├── .gitignore
└── Dockerfile
```

Run:

```bash
python structure_generator.py structure.txt
```

The resulting structure will be:

```text
my-app/
├── backend/
│   ├── main.py
│   └── config.yaml
├── frontend/
│   ├── src/
│   │   └── App.tsx
│   └── package.json
├── .gitignore
└── Dockerfile
```

All files are created as empty files. The program only creates the structure; it does not generate file contents.
