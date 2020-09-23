import pytest
from pathlib import Path
from freeway import Version


@pytest.fixture
def VerData():
    return Version


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

"""
@pytest.mark.parametrize('path, expected', [
    ('asset.v007.abc', 'asset.v001.abc'),
    ('asset.abc', 'asset.v001.abc'),
    (r'C:\projects\assets\asset.v007.abc', 'asset.v001.abc'),
    (r'C:\project\assets\asset.abc', 'asset.v001.abc'),
    ('C:/projects/assets/asset.v007.abc', 'asset.v001.abc'),
    ('C:/project/assets/asset.abc', 'asset.v001.abc')
])
def test_first(VerData, path, expected):
    assert VerData(path).first == expected

"""


"""
postfix = Version('').postfix

            
class Test_VersionFileSystem():
    def test_first(self):
        path = Path.cwd() / Path("tests/versionerExamples/test_mod.v001.txt")
        ver = Version("tests/versionerExamples/test_mod.v002.txt").fs
        assert str(ver.first) == str(path)
            
    def test_last(self):
        path = Path.cwd() / Path("tests/versionerExamples/test_mod.v003.txt")
        ver = Version("tests/versionerExamples/test_mod.v001.txt").fs
        assert str(ver.last) == str(path)
        
    def test_next(self):
        path = Path.cwd() / Path("tests/versionerExamples/test_mod.v003.txt")
        ver = Version("tests/versionerExamples/test_mod.v002.txt").fs
        assert str(ver.next) == str(path)
            
    def test_previous(self):
        path = Path.cwd() / Path("tests/versionerExamples/test_mod.v001.txt")
        ver = Version("tests/versionerExamples/test_mod.v002.txt").fs
        assert str(ver.previous) == str(path)

    def test_contains(self):
        assert 1 in Version("tests/versionerExamples/test_mod.v002.txt").fs


"""
