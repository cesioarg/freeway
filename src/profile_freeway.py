from __future__ import print_function
from cProfile import run
from freeway import Freeway


def test1(cycles=10000):
    filepath = (
        r"C:/example/assets/Characters/Roberto/MOD/Work/example_CH_Roberto_MOD.v001.abc"
    )
    # Parse data from path
    for cycle in range(cycles):
        myPath = Freeway(filepath)
        myPath.asset = "Tito"
    # Use parsed data for make new paths
    print("Result:", myPath.assetDir)


def test2(cycles=50000):
    # Parse data from path
    filepath = (
        r"C:/example/assets/Characters/Roberto/MOD/Work/example_CH_Roberto_MOD.v001.abc"
    )
    myPath = Freeway(filepath)
    for cycle in range(cycles):
        myPath.asset = "Tito"
        data = myPath.assetDir

    # Use parsed data for make new paths
    print("Result:", myPath.assetDir)


if __name__ == "__main__":
    run("test2()", sort="time")
