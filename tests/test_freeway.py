import os
import pytest
from freeway import Freeway


@pytest.fixture
def obj_test():
    path = os.path.abspath(os.path.relpath('./examples/rules.json'))
    return Freeway(rulesfile=path)


@pytest.mark.parametrize('path, expected', [
    ("example_Character_Roberto_MOD_v001.abc", 
     {'assetType': 'Character', 'asset': 'Roberto',
      'task': 'MOD', 'version': '001', 'ext': 'abc'}),
    ("C:/example/assets/Characters/Roberto/MOD/Work/example_CH_Roberto_MOD.v001.abc",
     {'assetType': 'Characters', 'asset': 'Roberto', 'step': 'MOD', 'stage': 'Work',
      'assetPrefix': 'CH', 'task': 'MOD', 'version': '001', 'ext': 'abc'}),
])
def test_parser(obj_test, path, expected):
    obj_test.filepath = path
    assert obj_test.data == expected


@pytest.mark.parametrize('data, pattern, expected', [
    ({'assetType': 'Character', 'asset': 'Roberto',
      'task': 'MOD', 'version': '001', 'ext': 'abc'}, 'assetFile',
     "example_Character_Roberto_MOD_v001.abc"),
    ({'assetType': 'Characters', 'asset': 'Roberto', 'step': 'MOD',
      'stage': 'Work', 'assetPrefix': 'CH', 'task': 'MOD',
      'version': '001', 'ext': 'abc'}, 'assetWorkspacePath',
     "C:/example/assets/Characters/Roberto/MOD/Work/example_CH_Roberto_MOD.v001.abc"
     ),
])
def test_resolver_from_update(obj_test, data, pattern, expected):
    obj_test.update(data)
    assert obj_test.get(pattern) == expected


@pytest.mark.parametrize('path, pattern, expected', [
    ("example_Character_Roberto_MOD_v001.abc", "assetFile",
     "example_Character_Roberto_MOD_v001.abc"),
    ("C:/example/assets/Characters/Roberto/MOD/Work/example_CH_Roberto_MOD.v001.abc", "assetWorkspacePath",
     "C:/example/assets/Characters/Roberto/MOD/Work/example_CH_Roberto_MOD.v001.abc"
     ),
])
def test_resolver_filepath_only(obj_test, path, pattern, expected):
    obj_test.filepath = path
    assert obj_test.get(pattern) == expected

def main():
    # Parse data from path
    filepath = r"C:/example/assets/Characters/Roberto/MOD/Work/example_CH_Roberto_MOD.v001.abc"
    myPath = Freeway(filepath)
    # Show all parsed data
    print(myPath)

    # Use parsed data
    print("%s_%s_%s_example" % (myPath.asset, myPath.assetType, myPath.task))

    # Use parsed data for make new paths
    print(myPath.assetDir)

    # Make a path from data
    data = {'assetType': 'Prop',
            'asset': 'Table',
            'process': 'MOD',
            'stage': 'Work',
            'assetPrefix': 'PR',
            'task': 'MOD',
            'version': '001',
            'ext': 'abc'}

    myPath = Freeway(pattern="assetWorkspacePath", **data)

    print(myPath.assetWorkspacePath)
    print(myPath.assetFile)
    print(myPath.assetDir)

    # Modify parsed data to make new paths
    other = myPath.copy()
    myPath.stage = "Publish"
    myPath.ext = "usd"
    myPath.asset = "Chair"
    print(myPath.assetWorkspacePath)

    # Or also
    other.update({"process": "SHD",
                  "ext": "mb",
                  "version": "123"})

    print(other.assetWorkspacePath)
