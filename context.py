"""
define the path to important folders without having
to install anything -- just do:

import context

then the path for the data directory is

context.data_dir

"""
import sys
import site
from pathlib import Path

path = Path(__file__).resolve()  # this file
this_dir = path.parent  # this folder
if this_dir.name == "python":
    notebooks_dir = this_dir.parent
else:
    notebooks_dir = this_dir
root_dir = notebooks_dir.parent
data_dir = root_dir / Path("data")
save_dir = root_dir / Path("data/img")
img_dir = root_dir / Path("img")


sys.path.insert(0, str(root_dir))
sep = "*" * 30
print(f"{sep}\ncontext imported. Front of path:\n{sys.path[0]}\n{sys.path[1]}\n{sep}\n")


print(f"through {__file__} -- pha")
