# Metarepo: An alternative to git submodules

Metarepo is used to manage dependencies on other git repositories when git submodules is not sufficient.
It was inspired by the [repo](https://gerrit.googlesource.com/git-repo/) tool by Google but instead of requiring the
manifest to be stored in its own repository, it is stored in the same repository.

![Demo](assets/demo.gif)

## Installation

```bash
# Install from PyPI
pip3 install --upgrade metarepo

# Install from git using PIP
pip3 install --upgrade git+https://github.com/blejdfist/git-metarepo
```

## Usage

You can run `metarepo` in two ways, standalone or using git. Both methods work the same and it is only a matter of personal taste.

```bash
git meta
metarepo
```

Create an initial `manifest.yml` configuration using the init command
```bash
git meta init
```

Synchronize the repositories
```bash
git meta sync
```

## Manifest structure

```yml
repos:
  - url: https://github.com/blejdfist/pycodegen
    path: tools/pycodegen
    track: master
```

| Field     | Explanation              | Required             |
| --------- | ------------------------ | :------------------: |
| url       | Git URL to clone         | Yes                  |
| path      | Where to clone the repo  | Yes                  |
| track     | What branch/tag to track | No (default: master) |
