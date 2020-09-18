import pytest
from freeway import Freeway


@pytest.fixture
def FreewayTest():
    return Freeway


assetRule = {"rules": {"root": ["{asset}.v{version}.{ext}"]}}


@pytest.mark.parametrize('path, rules, expected', [
    ('asset.v007.abc', assetRule, False),
    ('asset.abc', assetRule, True),
    (r'C:\projects\assets\asset.v007.abc', assetRule, False),
    (r'C:\project\assets\asset.abc', assetRule, True),
    ('C:/projects/assets/asset.v007.abc', assetRule, False),
    ('C:/project/assets/asset.abc', assetRule, True)
])
def test_data(VerData, path, expected):
    assert FreewayTest(path).data == expected



"""
class Test_RuleParser():
    def test___getitem__(self, item):
        pass
    
    def test___contains__(self, item):
        pass
    
    def test_lenFields(self):
        pass
    
    def test_fields(self):
        pass
    
    def test_regex(self):
        pass


class Test_Freeway():
    def Test_parseFilepath(self, filepath, patterns=['auto']):
        pass
    
    def Test_info_from_path(path, rules, patterns=['auto']):
        pass
    
    def Test_match(self):
        pass
    
    def Test_getter_pattern(self):
        pass
    
    def Test_setter_pattern(self, value):
        pass
    
    def Test_data(self):
        pass
    
    def Test_get_rules(allrules):
        pass
    
    def Test_expandRules(attr, rules):
        pass
    
    def Test___getattribute__(self, attr):
        pass
    
    def Test___contains__(self, item):
        pass
    
    def Test___getitem__(self, item):
        pass
    
    def Test_get(self, item, default=None):
        pass
    
    def Test_update(self, data):
        pass
    
    def Test_clean(self):
        pass
    
    def Test_version(self, attr):
        pass

"""
