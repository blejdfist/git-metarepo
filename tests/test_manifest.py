import os
import tempfile
from pathlib import Path

import pytest
import yaml
from metarepo import manifest


def test_manifest_not_existant():
    with tempfile.TemporaryDirectory() as temp_dir:
        with pytest.raises(manifest.NotFound):
            manifest.load_manifest(os.path.join(temp_dir, "nonexistant.yml"))


def test_manifest_validate_failed():
    with pytest.raises(manifest.ValidationFailed):
        manifest.parse_manifest({})

    with pytest.raises(manifest.ValidationFailed):
        manifest.parse_manifest({"repos": []})

    with pytest.raises(manifest.ValidationFailed):
        manifest.parse_manifest({"repos": [{}]})

    with pytest.raises(manifest.ValidationFailed):
        manifest.parse_manifest({"repos": [{"uri": "OnlyURI"}]})

    with pytest.raises(manifest.ValidationFailed):
        manifest.parse_manifest({"repos": [{"path": "OnlyPath"}]})


def test_manifest_parse_successful():
    result = manifest.parse_manifest({"repos": [{"url": "git://localhost/repo", "path": "my/path"}]})
    repos = result.get_repos()
    assert len(repos) == 1
    assert repos[0].url == "git://localhost/repo"
    assert repos[0].path == Path("my/path")


def test_manifest_load_successful(tmpdir):
    test_manifest = {"repos": [{"url": "git://localhost/repo", "path": "my/path"}]}

    manifest_filename = tmpdir / "manifest.yml"
    with open(manifest_filename, "w") as fp:
        yaml.safe_dump(test_manifest, fp)

    result = manifest.load_manifest(manifest_filename)

    repos = result.get_repos()
    assert len(repos) == 1
    assert repos[0].url == "git://localhost/repo"
    assert repos[0].path == Path("my/path")


def test_manifest_save(tmpdir):
    repos = [
        manifest.Repository(url="http://localhost/repo1", path="path/to/repo1"),
        manifest.Repository(url="http://localhost/repo2", path="path/to/repo2", track="featureX"),
    ]
    manifest_to_save = manifest.Manifest(repos=repos)

    filename = tmpdir / "manifest.yml"
    assert not filename.exists()
    manifest.save_manifest(manifest_to_save, filename)
    assert filename.exists()
    loaded_manifest = manifest.load_manifest(filename)

    assert manifest_to_save == loaded_manifest
