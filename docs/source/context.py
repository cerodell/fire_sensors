# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     formats: ipynb,py:percent
#     notebook_metadata_filter: all,-language_info,-toc,-latex_envs
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.3.0
# ---

# %%
"""
define the path to important folders without having
 to install anything -- just do:

import contenxt

then the path for the data directory is

context.data_dir

"""
import sys
import site
from pathlib import Path

# %%
path = Path(__file__).resolve()  # this file
this_dir = path.parent  # this folder
notebooks_dir = this_dir
root_dir = notebooks_dir.parents[0]
data_dir = Path("/Users/rodell/Google Drive/Shared drives/Research/FireSmoke/FieldWork/OPC/data/")
save_dir = Path("/Users/rodell/Google Drive/Shared drives/Research/FireSmoke/FieldWork/OPC/images/")

# data_dir = root_dir / Path("data")
# save_dir = root_dir / Path("img")




 # %%
sys.path.insert(0, str(root_dir))
sep = "*" * 30
print(f"{sep}\ncontext imported. Front of path:\n{sys.path[0]}\n{sys.path[1]}\n{sep}\n")


# %%
print(f"through {__file__} -- pha")
