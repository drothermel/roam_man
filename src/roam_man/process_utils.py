from roam_man import validation_utils as vu

# Note: Fxns used effectively but not covered by tests.


def page_node_list_to_title_sets(page_nodes, uid_to_title):
    title_sets = {
        "daily_pages": set(),
        "bars": set(),
        "backslashes": set(),
        "with_ref": {},
        "other": set(),
    }
    for title, node in page_nodes.items():
        if vu.is_valid_date(node.uid):
            title_sets["daily_pages"].add(title)
        elif "|" in title:
            title_sets["bars"].add(title)
            if len(node.refs) > 0:
                first_ref_title = uid_to_title[node.refs[0]]
                if first_ref_title not in title_sets["with_ref"]:
                    title_sets["with_ref"][first_ref_title] = set()
                title_sets["with_ref"][first_ref_title].add(title)
        elif "/" in title:
            title_sets["backslashes"].add(title)
        else:
            title_sets["other"].add(title)
    return title_sets


def map_items_with_input(input_dict):
    """
    Function to surface items from input_dict one at a time, allowing the user to provide keyboard input.
    The input will be used as the key to create a new dictionary where the value is a set containing
    all corresponding values from input_dict for the same user-provided key.

    Args:
        input_dict (dict): The input dictionary to be processed.

    Returns:
        dict: A new dictionary with user-provided keys and sets of values from input_dict.
    """
    output_dict = {}

    for key in input_dict:
        user_input = input(f"-> '{key}': ")

        # If the user input already exists in the dictionary, append the value to the set
        if user_input in output_dict:
            output_dict[user_input].add(key)
        else:
            # Create a new set for the new key
            output_dict[user_input] = {key}

    return output_dict
