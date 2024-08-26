# roam_man

A repo to enable interacting with roam research programatically.

## Setup Steps

After being on a local mac environment where rye was installed (see dr_setup repo for more info), then clone, init and sync rye:
```shell
cd ~/repos/
git clone ...this repo...
rye init roam_man
cd roam_man
rye sync
rye pin 3.12 # pin python version for this repo

# Verify things worked as expected
rye show
# ... much info

python -c "import sys; print(sys.prefix)"
# a path to rye venv
```



