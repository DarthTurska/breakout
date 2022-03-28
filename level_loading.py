import os

def load_levels():
    levels=[]
    with os.scandir(os.path.join("data", "levels")) as entries:
        for entry in entries:
            with open(entry, "r") as f:
                data = f.read()
                levels.append(data.split("\n"))
    return levels
