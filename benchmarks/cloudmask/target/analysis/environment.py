import os

from cloudmesh.common.console import Console
from cloudmesh.common.systeminfo import os_is_linux
from cloudmesh.common.systeminfo import os_is_mac
from cloudmesh.common.util import banner
from cloudmesh.common.util import path_expand


# adjust this accordingly
if os_is_mac():
    target = "gregor-mac"
elif os_is_linux():
    target = "gregor-linux"
else:
    Console.error("specify a target and define it")

if target == "os":
    BASE=os.environ["BASE"]
    DATA_DIR=os.environ["DATA_DIR"]
    PROJECT_SRC=os.environ["PROJECT_SRC"]
    PROJECT=os.environ["PROJECT"]
    ESAT=os.environ["ESAT"]
    EDITOR=os.environ["EDITOR"]
elif target == "rivanna":
    USER = os.environ["USER"]
    BASE=f"/scratch/{USER}"
    DATA_DIR="/nfs/flash/mlcommons/data"
    PROJECT_SRC=f"{BASE}/mlcommons/src"
    PROJECT=f"{PROJECT_SRC}/mlcommons"
    ESAT="~/.esat"
    EDITOR="emacs"
elif target == "ruoshen":
    BASE="C:/Users/bill_/scratch"
    DATA_DIR=f"{BASE}/mlcommons/data"
    PROJECT_SRC=f"{BASE}/mlcommons/src"
    PROJECT=f"{PROJECT_SRC}/mlcommons"
    ESAT="C:/Users/bill_/esat"
    EDITOR="???"
elif target == "gregor-linux":
    BASE="/nfs/flash/mlcommons"
    DATA_DIR=f"{BASE}/data"
    PROJECT_SRC=f"{BASE}/mlcommons/benchmarks/cloudmask/"
    PROJECT = f"{PROJECT_SRC}/target/greene_v0.5/project"
    ESAT="~/.esat"
    EDITOR="emacs"
elif target == "gregor-mac":
    BASE="/scratch"
    DATA_DIR="/Volumes/flash/mlcommons/data"
    PROJECT_SRC=f"{BASE}/mlcommons/src"
    PROJECT=f"{PROJECT_SRC}/mlcommons"
    ESAT="~/.esat"
    EDITOR="open -a aquamacs"

def get_var_name(var):
    """
    Get the name of a variable as a string.
    """
    for name, value in globals().items():
        if value is var:
            return name
    return None

def print_var(v, n=15, exists=""):
    name = get_var_name(v)
    print(f"{name.ljust(n)}: {v} {exists}")

banner("ENVIRONMENT")
for v in [target,BASE,DATA_DIR,PROJECT_SRC,PROJECT,ESAT]:
    exists = ""
    if v not in [target]:
        if not os.path.exists(path_expand(v)):
            exists = ". does not exist."
    print_var(v, exists=exists)

from cloudmesh.common.Shell import Shell
count = Shell.count_files(PROJECT, recursive=False)
print(f"Files in PROJECT: {count}")

count = Shell.count_files(DATA_DIR, recursive=True)
print(f"Files in DATA_DIR (recursive): {count}")