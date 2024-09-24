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

## IPynb

Kick off jupyterlab with rye:
```
# after having installed "jupyter-lab" and "jupyterlab_vim"
rye run jupyter-lab
```

## Example Usage

```
from roam_man.roam_graph import RoamGraph
import roam_man.process_utils as pu

rg = RoamGraph("/Users/daniellerothermel/Desktop/life_planning-2024-09-23-14-41-27.json")

title_sets = pu.page_node_list_to_title_sets(rg.roam_pages, rg.uid_to_title)
print("Title Set Sizes")
for k, v in title_sets.items():
    print(" - ", k, ":", len(v))
    if k == "with_ref":
        for kk, vv in v.items():
                print("   - ", kk, len(vv))

#  Title Set Sizes
#   -  daily_pages : 112
#   -  bars : 0
#   -  backslashes : 8
#   -  with_ref : 0
#   -  other : 211

rg.get_page_node_by_index(102)

#  Classification and Correction of Non-Representative News Headlines
#    uid='DNqgQM5vZ' refs=[]

rg.get_page_node_by_index(6).print_full()
# .....


#  Try: od_bars = map_items_with_input(title_sets['bars'])
```
