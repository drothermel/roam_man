import io


def roam_node_tree_to_str(roam_node):
    buffer = io.StringIO()
    nodes = [roam_node]
    i = 0

    while i < len(nodes):
        if i > 0:
            buffer.write("\n")

        node = nodes[i]
        buffer.write(str(node))
        # Safely add children to the end of the list
        nodes.extend(node.children)

        # Move to the next node
        i += 1

    result = buffer.getvalue()
    buffer.close()
    return result
