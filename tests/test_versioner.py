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



"""
postfix = Version('').postfix

case_vars = ['asset.v007.abc',
             'asset.abc',
             r'C:\projects\assets\asset.v007.abc',
             r'C:\project\assets\asset.abc',
             'C:/projects/assets/asset.v007.abc',
             'C:/project/assets/asset.abc']

Cases = {'isVersionless': [False, True, False, True, False, True],
         'versionless': ['asset.abc',
                         'asset.abc',
                         'C:/projects/assets/asset.abc',
                         'c:/project/assets/asset.abc',
                         'C:/projects/assets/asset.abc',
                         'c:/project/assets/asset.abc'],
         'to_version': ['asset%s015.abc' % postfix,
                        'asset%s015.abc' % postfix,
                        'C:/projects/assets/asset%s015.abc' % postfix,
                        'c:/project/assets/asset%s015.abc' % postfix,
                        'C:/projects/assets/asset%s015.abc' % postfix,
                        'c:/project/assets/asset%s015.abc' % postfix],
         'first': ['asset%s001.abc' % postfix,
                   'asset%s001.abc' % postfix,
                   'C:/projects/assets/asset%s001.abc' % postfix,
                   'C:/project/assets/asset%s001.abc' % postfix,
                   'C:/projects/assets/asset%s001.abc' % postfix,
                   'C:/project/assets/asset%s001.abc' % postfix],
         'current': [7,
                     None,
                     7,
                     None,
                     7,
                     None],
         'next': ['asset%s008.abc' % postfix,
                  None,
                  'C:/projects/assets/asset%s008.abc' % postfix,
                  None,
                  'C:/projects/assets/asset%s008.abc' % postfix,
                  None],
         'previous': ['asset%s006.abc' % postfix,
                      None,
                      'C:/projects/assets/asset%s006.abc' % postfix,
                      None,
                      'C:/projects/assets/asset%s006.abc' % postfix,
                      None],
         'last': ['asset%s001.abc' % postfix,
                  'asset%s001.abc' % postfix,
                  'C:/projects/assets/asset%s001.abc' % postfix,
                  'c:/project/assets/asset%s001.abc' % postfix,
                  'C:/projects/assets/asset%s001.abc' % postfix,
                  'c:/project/assets/asset%s001.abc' % postfix],
         }



class Test_Version():
    def test_isVersionless(self):
        for index, solution in enumerate(Cases['isVersionless']):
            case = Version(case_vars[index]).isVersionless
            assert case == solution

    def test_versionless(self):
        for index, solution in enumerate(Cases['versionless']):
            solution = str(Path(solution).resolve())
            case = str(Version(case_vars[index]).versionless)
            assert case == solution

    def test_to(self):
        for index, solution in enumerate(Cases['to_version']):
            case = str(Version(case_vars[index]).to(15))
            solution = str(Path(solution).resolve())
            assert case == solution
            
    def test_current(self):
        for index, solution in enumerate(Cases['current']):
            case = Version(case_vars[index]).current
            assert case == solution
            
    def test_next(self):
        for index, solution in enumerate(Cases['next']):
            case = Version(case_vars[index]).next
            assert case == solution
            
    def test_previous(self):
        for index, solution in enumerate(Cases['previous']):
            case = Version(case_vars[index]).previous
            assert case == solution
            
            
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
