import io


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


def raw_roam_data_to_str(roam_data_elem):
    buffer = io.StringIO()
    nodes = [roam_data_elem]
    i = 0

    while i < len(nodes):
        if i > 0:
            buffer.write("\n")

        node = nodes[i]

        add_roam_elem_str_to_buffer(
            uid=node["uid"],
            refs=[r["uid"] for r in node.get("refs", [])],
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


# def roam_node_tree_to_str(roam_node):
#    buffer = io.StringIO()
#    nodes = [roam_node]
#    i = 0
#
#    while i < len(nodes):
#        if i > 0:
#            buffer.write("\n")
#
#        node = nodes[i]
#        buffer.write(str(node))
#        # Safely add children to the end of the list
#        nodes.extend(node.children)
#
#        # Move to the next node
#        i += 1
#
#    result = buffer.getvalue()
#    buffer.close()
#    return result
