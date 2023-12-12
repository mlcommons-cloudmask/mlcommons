import os

from cloudmesh.common.console import Console
from cloudmesh.common.systeminfo import os_is_linux
from cloudmesh.common.systeminfo import os_is_mac
from cloudmesh.common.util import banner


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
    BASE="/scratch"
    DATA_DIR="/nfs/flash/mlcommons/data"
    PROJECT_SRC=f"{BASE}/mlcommons/src"
    PROJECT=f"{PROJECT_SRC}/mlcommons"
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

def print_var(v, n=15):
    name = get_var_name(v)
    print(f"{name.ljust(n)}: {v}")

banner("ENVIRONMENT")
for v in [target,BASE,DATA_DIR,PROJECT_SRC,PROJECT,ESAT]:
    print_var(v)
