import yaml
import pytest
import tempfile
import os
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
    result = manifest.parse_manifest({"repos": [{"uri": "git://localhost/repo", "path": "my/path"}]})
    repos = result.get_repos()
    assert len(repos) == 1
    assert repos[0].uri == "git://localhost/repo"
    assert str(repos[0].path) == "my/path"


def test_manifest_load_successful():
    test_manifest = {"repos": [{"uri": "git://localhost/repo", "path": "my/path"}]}

    with tempfile.TemporaryDirectory() as temp_dir:
        manifest_filename = os.path.join(temp_dir, "manifest.yml")
        with open(manifest_filename, "w") as fp:
            yaml.safe_dump(test_manifest, fp)

        result = manifest.load_manifest(manifest_filename)

        repos = result.get_repos()
        assert len(repos) == 1
        assert repos[0].uri == "git://localhost/repo"
        assert str(repos[0].path) == "my/path"
