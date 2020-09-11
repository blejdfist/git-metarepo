# Metarepo: A tool for managing git repo dependencies

## Installation


```bash
# Install from git using PIP
pip3 install --upgrade git+https://github.com/blejdfist/git-metarepo
```


## Usage

You can run `metarepo` in two ways, standalone or using git. Both methods work the same and it is only a matter of personal taste.

```bash
git meta -h
metarepo -h
```

### Configuration

Initial configuration can be created using the init command

```bash
git meta init
```

This will create the initial `manifest.yml` file.

```yml
repos:
  - url: https://github.com/blejdfist/pycodegen
    path: tools/pycodegen
    track: master
```