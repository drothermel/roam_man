import pytest
from hypothesis import given
from hypothesis import strategies as st

from roam_man import viz_utils as zu

# # Setup Hypothesis Strategies and Functions # #


# Function to construct the base roam node
def build_roam_node(
    uid,
    create_time,
    edit_time,
    string,
    user_create,
    user_edit,
    title=None,
    children=None,
    refs=None,
):
    base_node = {
        "uid": uid,
        "create-time": create_time,
        "edit-time": edit_time,
        "string": string,
        ":create/user": user_create,
        ":edit/user": user_edit,
    }
    if title is not None:
        base_node["title"] = title
    if children is not None:
        base_node["children"] = children
    if refs is not None:
        base_node["refs"] = refs
    return base_node


def make_strategy_from_children(children=None):
    # Strategy to generate text without backslashes
    allowed_characters = st.characters(
        whitelist_categories=("Ll", "Lu", "Nd"), whitelist_characters=" "
    )
    nice_text = st.text(alphabet=allowed_characters, min_size=5, max_size=10)

    # Strategy for refs: {'uid': str}
    refs_strategy = st.lists(
        st.fixed_dictionaries({"uid": nice_text}),
        min_size=1,
        max_size=10,
    )

    if children is None:
        children_st = st.none()
    else:
        children_st = st.one_of(
            st.none(),
            st.lists(children, min_size=1, max_size=3),
        )

    return st.builds(
        build_roam_node,
        uid=nice_text,
        create_time=st.integers(min_value=1, max_value=1726763135105),
        edit_time=st.integers(min_value=1, max_value=1726763135105),
        string=nice_text,
        user_create=st.fixed_dictionaries({":user/uid": nice_text}),
        user_edit=st.fixed_dictionaries({":user/uid": nice_text}),
        title=st.one_of(st.none(), nice_text),
        children=children_st,  # Optional children
        refs=st.one_of(st.none(), refs_strategy),  # Optional refs
    )


# Hypothesis strategy to generate nested roam-like dictionaries
def nested_roam_dict():
    first_node_dict = make_strategy_from_children()
    nested_roam_dict = st.recursive(
        first_node_dict,
        make_strategy_from_children,
        max_leaves=5,
    )
    return nested_roam_dict


# Sample test data generated for static testing
@pytest.fixture
def static_test_data():
    return [
        # Single level
        {
            "uid": "tx0S2zj5t",
            "create-time": 1694303705806,
            "edit-time": 1694303705806,
            "string": "nothing",
            "title": "Danielle Rothermel",
            ":create/user": {":user/uid": "XRlk7Tpv53UEosC4qi7bcFHhVPx1"},
            ":edit/user": {":user/uid": "XRlk7Tpv53UEosC4qi7bcFHhVPx1"},
        },
        # Nested but empty children
        {
            "create-time": 1694303843654,
            "title": "September 10th, 2023",
            "string": "nothing",
            ":create/user": {":user/uid": "XRlk7Tpv53UEosC4qi7bcFHhVPx1"},
            ":log/id": 1694304000000,
            "children": [],
            "uid": "09-10-2023",
            "edit-time": 1694303843654,
            ":edit/user": {":user/uid": "XRlk7Tpv53UEosC4qi7bcFHhVPx1"},
        },
        # Nested with content
        {
            "create-time": 1699907527267,
            "title": "Classification and Correction of Non-Representative News Headlines",
            "string": "nothing",
            ":create/user": {":user/uid": "XRlk7Tpv53UEosC4qi7bcFHhVPx1"},
            "children": [
                {
                    "string": "#todo.to_process.move",
                    "create-time": 1726760509745,
                    ":block/refs": [{":block/uid": "pUoYhPB6m"}],
                    "refs": [{"uid": "pUoYhPB6m"}],
                    ":create/user": {":user/uid": "XRlk7Tpv53UEosC4qi7bcFHhVPx1"},
                    "uid": "SbngKbqIX",
                    "edit-time": 1726760513278,
                    ":edit/user": {":user/uid": "XRlk7Tpv53UEosC4qi7bcFHhVPx1"},
                },
            ],
            "uid": "DNqgQM5vZ",
            "edit-time": 1699907527267,
            ":edit/user": {":user/uid": "XRlk7Tpv53UEosC4qi7bcFHhVPx1"},
        },
    ]


def check_expected_output(data, output):
    out_lines = output.split("\n")
    if "title" in data:
        assert data["title"] == out_lines[0], "Title not in first line"
        assert data["uid"] in out_lines[1], "uid not in second line"
        if "refs" in data:
            assert data["refs"][0]["uid"] in out_lines[1], "Refs incorrect"
    if "children" not in data:
        assert len(out_lines) <= 3, "Too many lines for one node tree"
    else:
        assert len(out_lines) > 1, "Too few lines for multi-node tree"


# Test using static test data
@pytest.mark.parametrize("static_idx", [0, 1, 2])
def test_raw_roam_data_to_str_static(static_idx, static_test_data):
    static_data = static_test_data[static_idx]
    check_expected_output(
        static_data,
        zu.raw_roam_data_to_str(static_data),
    )


# Test using dynamic test data with Hypothesis, main goal is to look for crashes
@given(data=st.lists(nested_roam_dict(), min_size=1, max_size=10))
def test_raw_roam_data_to_str_dynamic(data):
    check_expected_output(
        data[0],
        zu.raw_roam_data_to_str(data[0]),
    )
