from freeway import Freeway


if __name__ == '__main__':
    myPath = Freeway(rules={"root": ["{asset}.v{version}.{ext}"]}, pattern="root")
    myPath.filepath = r"Z:/projects/assets/asset.v007.abc"
    print(myPath.data)
