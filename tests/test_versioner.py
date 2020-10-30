import os
import pytest
from freeway import Version


@pytest.fixture
def VerData():
    return Version

root = os.getcwd()


@pytest.mark.parametrize('path, expected', [
    ('asset.v007.abc', False),
    ('asset.abc', True),
    (r'C:\projects\assets\asset.v007.abc', False),
    (r'C:\project\assets\asset.abc', True),
    ('C:/projects/assets/asset.v007.abc', False),
    ('C:/project/assets/asset.abc', True)
])
def test_isVersionless(VerData, path, expected):
    assert VerData(path).isVersionless == expected
    

@pytest.mark.parametrize('path, expected', [
    ('asset.v007.abc', 'asset.abc'),
    ('asset.abc', 'asset.abc'),
    (r'C:\projects\assets\asset.v007.abc', 'C:/projects/assets/asset.abc'),
    (r'C:\project\assets\asset.abc', 'c:/project/assets/asset.abc'),
    ('C:/projects/assets/asset.v007.abc', 'C:/projects/assets/asset.abc'),
    ('C:/project/assets/asset.abc', 'c:/project/assets/asset.abc')
])
def test_versionless(VerData, path, expected):
    assert VerData(path).versionless == expected


@pytest.mark.parametrize('path, expected', [
    ('asset.v007.abc', 'asset.v123.abc'),
    ('asset.abc', 'asset.v123.abc'),
    (r'C:\projects\assets\asset.v007.abc', 'C:/projects/assets/asset.v123.abc'),
    (r'C:\project\assets\asset.abc', 'c:/project/assets/asset.v123.abc'),
    ('C:/projects/assets/asset.v007.abc', 'C:/projects/assets/asset.v123.abc'),
    ('C:/project/assets/asset.abc', 'c:/project/assets/asset.v123.abc')
])
def test_to(VerData, path, expected):
    assert VerData(path).to(123) == expected


@pytest.mark.parametrize('path, expected', [
    ('asset.v007.abc', 7),
    ('asset.abc', None),
    (r'C:\projects\assets\asset.v007.abc', 7),
    (r'C:\project\assets\asset.abc', None),
    ('C:/projects/assets/asset.v007.abc', 7),
    ('C:/project/assets/asset.abc', None)
])
def test_current(VerData, path, expected):
    assert VerData(path).current == expected


@pytest.mark.parametrize('path, expected', [
    ('asset.v007.abc', 'asset.v008.abc'),
    ('asset.abc', None),
    (r'C:\projects\assets\asset.v007.abc', 'asset.v008.abc'),
    (r'C:\project\assets\asset.abc', None),
    ('C:/projects/assets/asset.v007.abc', 'asset.v008.abc'),
    ('C:/project/assets/asset.abc', None)
])
def test_next(VerData, path, expected):
    assert VerData(path).next == expected


@pytest.mark.parametrize('path, expected', [
    ('asset.v007.abc', 'asset.v006.abc'),
    ('asset.abc', None),
    (r'C:\projects\assets\asset.v007.abc', 'asset.v006.abc'),
    (r'C:\project\assets\asset.abc', None),
    ('C:/projects/assets/asset.v007.abc', 'asset.v006.abc'),
    ('C:/project/assets/asset.abc', None)
])
def test_previous(VerData, path, expected):
    assert VerData(path).previous == expected

# Real Filesystem Tests!

@pytest.mark.parametrize('path, expected', [
    ('tests/versionerExamples/test_mod.v002.txt', '%s/test_mod.v001.txt' % root),
    ('tests/versionerExamples/test_mod.v001.txt', None),
    ('tests/versionerExamples/test_mod.v005.txt', None),
    ('tests/versionerExamples/test_mod.v010.txt', None)
])
def test_fs_previous(VerData, path, expected):
    assert VerData(path).fs.previous == expected


@pytest.mark.parametrize('path, expected', [
    ('tests/versionerExamples/test_mod.v002.txt', '%s/test_mod.v003.txt' % root),
    ('tests/versionerExamples/test_mod.v001.txt', '%s/test_mod.v002.txt' % root),
    ('tests/versionerExamples/test_mod.v005.txt', None),
    ('tests/versionerExamples/test_mod.v010.txt', None)
])
def test_fs_next(VerData, path, expected):
    assert VerData(path).fs.next == expected


@pytest.mark.parametrize('path, expected', [
    ('tests/versionerExamples/test_mod.v002.txt', '%s/test_mod.v001.txt' % root),
    ('tests/versionerExamples/test_mod.v001.txt', '%s/test_mod.v001.txt' % root),
    ('tests/versionerExamples/test_mod.v005.txt', '%s/test_mod.v001.txt' % root),
    ('tests/versionerExamples/test_mod.v010.txt', '%s/test_mod.v001.txt' % root),
])
def test_fs_first(VerData, path, expected):
    assert VerData(path).fs.first == expected


@pytest.mark.parametrize('path, expected', [
    ('tests/versionerExamples/test_mod.v002.txt', '%s/test_mod.v004.txt' % root),
    ('tests/versionerExamples/test_mod.v001.txt', '%s/test_mod.v004.txt' % root),
    ('tests/versionerExamples/test_mod.v005.txt', '%s/test_mod.v004.txt' % root),
    ('tests/versionerExamples/test_mod.v010.txt', '%s/test_mod.v004.txt' % root),
])
def test_fs_last(VerData, path, expected):
    assert VerData(path).fs.last == expected


@pytest.mark.parametrize('path, expected', [
    ('tests/versionerExamples/test_mod.v002.txt', True),
    ('tests/versionerExamples/test_mod.v001.txt', True),
    ('tests/versionerExamples/test_mod.v005.txt', False),
    ('tests/versionerExamples/test_mod.v010.txt', False),
])
def test_fs_exists(VerData, path, expected):
    assert VerData(path).fs.exists == expected


@pytest.mark.parametrize('path, version, expected', [
    ('tests/versionerExamples/test_mod.v002.txt', 1, True),
    ('tests/versionerExamples/test_mod.v001.txt', 2, True),
    ('tests/versionerExamples/test_anm.v005.txt', 3, False),
    ('tests/versionerExamples/test_lay.v010.txt', 4, False),
])
def test_fs_contains(VerData, path, version, expected):
    assert (version in VerData(path).fs) == expected

