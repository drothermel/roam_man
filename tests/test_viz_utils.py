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


# Hypothesis strategy to generate nested roam-like dictionaries
def nested_roam_dict():
    # Strategy for refs: {'uid': str}
    refs_strategy = st.fixed_dictionaries({"uid": st.text(min_size=5, max_size=10)})

    # Strategy to create roam nodes where some keys can be completely omitted
    optional_dict = st.builds(
        build_roam_node,
        uid=st.text(min_size=5, max_size=10),
        create_time=st.integers(min_value=1, max_value=1726763135105),
        edit_time=st.integers(min_value=1, max_value=1726763135105),
        user_create=st.fixed_dictionaries(
            {":user/uid": st.text(min_size=5, max_size=30)}
        ),
        user_edit=st.fixed_dictionaries(
            {":user/uid": st.text(min_size=5, max_size=30)}
        ),
        title=st.one_of(st.none(), st.text(min_size=1, max_size=50)),  # Optional title
        children=st.one_of(
            st.none(), st.lists(st.just({}), max_size=0)
        ),  # Optional children
        refs=st.one_of(st.none(), refs_strategy),  # Optional refs
    )

    # Recursive strategy for nested roam nodes with optional fields
    nested_roam_dict = st.recursive(
        optional_dict,
        lambda children: st.builds(
            build_roam_node,
            uid=st.text(min_size=5, max_size=10),
            create_time=st.integers(min_value=1, max_value=1726763135105),
            edit_time=st.integers(min_value=1, max_value=1726763135105),
            user_create=st.fixed_dictionaries(
                {":user/uid": st.text(min_size=5, max_size=30)}
            ),
            user_edit=st.fixed_dictionaries(
                {":user/uid": st.text(min_size=5, max_size=30)}
            ),
            title=st.one_of(st.none(), st.text(min_size=1, max_size=50)),
            children=st.one_of(
                st.none(), st.lists(children, max_size=3)
            ),  # Optional children
            refs=st.one_of(st.none(), refs_strategy),  # Optional refs
        ),
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
            "title": "Danielle Rothermel",
            ":create/user": {":user/uid": "XRlk7Tpv53UEosC4qi7bcFHhVPx1"},
            ":edit/user": {":user/uid": "XRlk7Tpv53UEosC4qi7bcFHhVPx1"},
        },
        # Nested but empty children
        {
            "create-time": 1694303843654,
            "title": "September 10th, 2023",
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
        assert data["uid"] in out_lines[1], "Uid not in second line"
        if "refs" in data:
            assert data["refs"][0]["uid"] in out_lines[1], "Refs incorrect"
    if "children" not in data:
        assert len(out_lines) <= 2, "Too many lines for one node tree"
    else:
        assert len(out_lines) > 1, "Too few lines for multi-node tree"


# Test using static test data
@pytest.mark.parametrize("idx", [0, 1, 2])
def test_print_roam_node_static(idx):
    stdata = static_test_data()
    check_expected_output(
        stdata[idx],
        zu.roam_node_tree_to_str(static_test_data),
    )


# Test using dynamic test data with Hypothesis
@given(data=st.lists(nested_roam_dict(), min_size=1, max_size=10))
def test_print_roam_node_dynamic(data):
    check_expected_output(
        data,
        zu.roam_node_tree_to_str(data),
    )
