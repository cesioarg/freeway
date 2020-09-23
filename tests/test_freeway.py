import pytest
from freeway import Freeway

@pytest.fixture
def obj_test():
    return Freeway(rules={"root": ["{asset}.v{version}.{ext}"]},
                   pattern="root")


@pytest.mark.parametrize('path, expected', [
    ('asset.v007.abc', {'asset': 'asset', 'version': '007', 'ext': 'abc'}),
    (r'Z:\projects\assets\asset.v007.abc', {}),
])
def test_parser(obj_test, path, expected):
    obj_test.filepath = path
    assert obj_test.data == expected
