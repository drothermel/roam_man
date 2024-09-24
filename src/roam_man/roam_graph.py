import io

from dr_util import file_utils as fu

# ---------------- Representation & Printing Utils ---------------- #

# To use: print(buffer.getvalue()); buffer.close()
def add_roam_elem_str_to_buffer(
    uid, refs=[], title=None, string=None, buffer=None, depth=0
):
    if buffer is None:
        buffer = io.StringIO()

    indent = "  " * depth
    if title is not None:
        assert depth == 0  # only pages (depth 0 nodes) have titles
        buffer.write(f"{title}\n {indent} {uid=} {refs=}\n")
    else:
        assert string is not None  # no title means yes string
        buffer.write(f"{indent} - {string}")
        if len(refs) > 0:
            buffer.write(f"\n{indent} ==> {uid=} {refs=}\n")
    return buffer

# Works for anything where the __dict__ method returns a dict
#   with the expected keys
def roam_data_to_full_str(roam_data_elem):
    buffer = io.StringIO()
    nodes = [roam_data_elem]
    i = 0

    while i < len(nodes):
        if i > 0:
            buffer.write("\n")

        node = nodes[i]
        if not isinstance(node, dict):
            node = node.__dict__

        refs = [r if isinstance(r, str) else r['uid'] for r in node.get("refs", [])]
        add_roam_elem_str_to_buffer(
            uid=node["uid"],
            refs=refs,
            title=node.get("title", None),
            string=node.get("string", None),
            buffer=buffer,
        )

        # Safely add children to the end of the list
        nodes.extend(node.get("children", []))

        # Move to the next node
        i += 1

    result = buffer.getvalue()
    buffer.close()
    return result
    
# ---------------- Roam Node & Graph ---------------- #


class RoamNode:
    def __init__(self, json, parent=None, start_depth=0):
        if not isinstance(json, dict) or json is None:
            raise Exception("RoamNode expects a non-null dict as input")

        # [[DONE]] and [[TODO]]
        uid_blacklist = {'KVGudD7AP', 'e2rS3SVH7'}  
        basic_keys = ['title', 'string', 'uid', 'create-time', 'edit-time']

        self.depth = start_depth
        self.parent = parent
        self.raw_data = json
        for k in basic_keys:
            setattr(self, k.replace("-", "_"), json.get(k, None))

        # Initialize refs
        self.refs = [
            r['uid'] for r in json.get('refs', []) if r['uid'] not in uid_blacklist
        ]
        self.recursive_refs = set(self.refs)

        # Recursively build tree of children
        self.children = [
            RoamNode(ch, parent=self, start_depth=self.depth+1) for ch in self.raw_data.get('children', [])
        ]
            
        # Update recursive refs for the node and propagate to parent
        if self.parent:
            self.parent.recursive_refs.update(self.recursive_refs)

    def __repr__(self):
        buffer = add_roam_elem_str_to_buffer(
            uid=self.uid,
            refs=self.refs,
            title=self.title,
            string=self.string,
            depth=self.depth,
        )
        rep = buffer.getvalue()
        buffer.close()
        return rep

    def print_full(self):
        print(roam_data_to_full_str(self))
    
# Uses validation_utils
# Uses viz_utils
class RoamGraph:
    def __init__(self, input_path, checkpoint_path=None):
        self.input_path = input_path
        self.checkpoint_path = checkpoint_path

        self.raw_data = None
        self.roam_pages = None
        self.uid_to_title = None
        self.extra_data = {}

        # Initialize
        self.parse_raw_data()
        
    def parse_raw_data(self):
        self.raw_data = fu.load_file(self.input_path)
        self.roam_pages = {rd['title']: RoamNode(rd) for rd in self.raw_data}
        self.uid_to_title = {v.uid: k for k, v in self.roam_pages.items()}

        if self.checkpoint_path is not None:
            fu.dump_file(self, self.checkpoint_path, force_suffix=True)

    def get_raw_elem(self, idx):
        return self.raw_data[idx]

    def get_page_node(self, title):
        return self.roam_pages[title]

    def get_page_node_by_index(self, idx):
        title = self.get_raw_elem(idx)['title']
        return self.get_page_node(title)
