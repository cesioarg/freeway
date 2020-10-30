from __future__ import print_function
from freeway import Freeway


if __name__ == '__main__':
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
            #'assetPrefix': 'PR',
            'task': 'MOD',
            'version': '001',
            'ext': 'abc'}

    myPath = Freeway(**data)

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
