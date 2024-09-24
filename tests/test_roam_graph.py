import pytest
from unittest.mock import patch
from hypothesis import given
from hypothesis import strategies as st

from roam_man import roam_graph as gu


# ----- Hand crafted data examples ----- #


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


@pytest.fixture
def valid_json():
    return {
        "title": "Sample Page",
        "string": "This is a sample page",
        "uid": "1234567890",
        "create-time": 1694303705806,
        "edit-time": 1694303705807,
        "refs": [
            {"uid": "ref1"},
            {"uid": "KVGudD7AP"},
            {"uid": "ref2"},
        ],  # One blacklisted ref
        "children": [
            {
                "title": "Child Page",
                "string": "This is a child page",
                "uid": "child_uid",
                "create-time": 1694303705808,
                "edit-time": 1694303705809,
                "refs": [],
            }
        ],
    }


@pytest.fixture
def raw_data():
    return [
        {
            "title": "Page 1",
            "string": "This is the first page",
            "uid": "page1",
            "create-time": 1694303705806,
            "edit-time": 1694303705807,
        },
        {
            "title": "Page 2",
            "string": "This is the second page",
            "uid": "page2",
            "create-time": 1694303705808,
            "edit-time": 1694303705809,
        },
    ]


# ----- Setup Hypothesis Strategies and Functions ----- #


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


def build_roam_page(
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
    base_node = build_roam_node(
        uid,
        create_time,
        edit_time,
        string,
        user_create,
        user_edit,
        title,
        children,
        refs,
    )
    base_node["title"] = string
    return base_node


def make_strategy_from_children(children):
    page_only = True
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

    fxn = build_roam_page if page_only else build_roam_node

    return st.builds(
        fxn,
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
def nested_roam_dict_st():
    first_node_dict = make_strategy_from_children(children=None)
    return st.recursive(
        first_node_dict,
        make_strategy_from_children,
        max_leaves=5,
    )


# ----- Test representation utils ----- #


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
        gu.roam_data_to_full_str(static_data),
    )


# Test using dynamic test data with Hypothesis, main goal is to look for crashes
@given(data=st.lists(nested_roam_dict_st(), min_size=1, max_size=10))
def test_raw_roam_data_to_str_dynamic(data):
    check_expected_output(
        data[0],
        gu.roam_data_to_full_str(data[0]),
    )


# ----- Test RoamNode ----- #


def test_roam_node_initialization(valid_json):
    # Test basic initialization and recursive child creation
    node = gu.RoamNode(valid_json)
    assert node.title == "Sample Page"
    assert node.uid == "1234567890"
    assert node.refs == ["ref1", "ref2"]  # Blacklisted ref should not be included
    assert len(node.children) == 1
    assert node.children[0].title == "Child Page"


def test_roam_node_invalid_json():
    # Test that it raises an exception for invalid input
    with pytest.raises(Exception, match="RoamNode expects a non-null dict as input"):
        gu.RoamNode(None)

    with pytest.raises(Exception, match="RoamNode expects a non-null dict as input"):
        gu.RoamNode("This is not a dict")


def test_roam_node_recursive_refs(valid_json):
    node = gu.RoamNode(valid_json)
    assert "ref1" in node.recursive_refs
    assert "ref2" in node.recursive_refs
    assert (
        "child_uid" not in node.recursive_refs
    )  # Ensure child uid doesn't pollute recursive refs
    assert len(node.children) == 1
    assert node.children[0].parent == node  # Ensure parent relationship is correct
    assert "ref1" in node.recursive_refs  # Child refs added to parent


def test_roam_node_repr(valid_json):
    node = gu.RoamNode(valid_json)
    repr_str = repr(node)
    assert "Sample Page" in repr_str
    assert "1234567890" in repr_str
    assert "ref1" in repr_str


@given(
    data=st.lists(
        nested_roam_dict_st(), min_size=1, max_size=10, unique_by=lambda x: x["title"]
    )
)
def test_roam_node_initialization_hypothesis(data):
    node = gu.RoamNode(data[0])
    assert node.uid is not None
    assert isinstance(node.refs, list)


@given(
    data=st.lists(
        nested_roam_dict_st(), min_size=1, max_size=10, unique_by=lambda x: x["title"]
    )
)
def test_roam_node_recursive_refs_hypothesis(data):
    node = gu.RoamNode(data[0])
    assert isinstance(node.recursive_refs, set)
    assert all(isinstance(ref, str) for ref in node.recursive_refs)


@given(
    data=st.lists(
        nested_roam_dict_st(), min_size=1, max_size=10, unique_by=lambda x: x["title"]
    )
)
def test_roam_node_repr_hypothesis(data):
    node = gu.RoamNode(data[0])
    repr_str = repr(node)
    if node.title is not None:
        assert node.uid in repr_str
    else:
        assert node.string is not None
        assert node.string in repr_str
    assert isinstance(repr_str, str)


# ----- Test gu.RoamGraph ----- #


@patch("dr_util.file_utils.load_file")
def test_roam_graph_initialization(mock_load_file, raw_data):
    # Mock file loading and ensure that the graph initializes properly
    mock_load_file.return_value = raw_data
    graph = gu.RoamGraph("fake_path")

    assert len(graph.roam_pages) == 2
    assert "Page 1" in graph.roam_pages
    assert "Page 2" in graph.roam_pages
    assert graph.uid_to_title["page1"] == "Page 1"
    assert graph.uid_to_title["page2"] == "Page 2"


@patch("dr_util.file_utils.load_file")
@patch("dr_util.file_utils.dump_file")
def test_roam_graph_checkpoint(mock_dump_file, mock_load_file, raw_data):
    # Mock file loading and checkpoint saving
    mock_load_file.return_value = raw_data
    graph = gu.RoamGraph("fake_path", checkpoint_path="fake_checkpoint")  # noqa: F841

    # Check that dump_file was called to save a checkpoint
    mock_dump_file.assert_called_once()


def test_roam_graph_get_page_node_by_index(raw_data):
    with patch("dr_util.file_utils.load_file", return_value=raw_data):
        graph = gu.RoamGraph("fake_path")

        page_node = graph.get_page_node_by_index(0)
        assert page_node.uid == "page1"
        assert page_node.title == "Page 1"

        page_node = graph.get_page_node_by_index(1)
        assert page_node.uid == "page2"
        assert page_node.title == "Page 2"


@given(
    data=st.lists(
        nested_roam_dict_st(), min_size=1, max_size=10, unique_by=lambda x: x["title"]
    )
)
@patch("dr_util.file_utils.load_file")
def test_roam_graph_initialization_hypothesis(mock_load_file, data):
    # Mock file loading
    mock_load_file.return_value = data
    graph = gu.RoamGraph("fake_path")

    assert len(graph.roam_pages) == len(data)
    assert all(isinstance(k, str) for k in graph.roam_pages.keys())
    assert all(isinstance(v, gu.RoamNode) for v in graph.roam_pages.values())


@given(
    data=st.lists(
        nested_roam_dict_st(), min_size=1, max_size=10, unique_by=lambda x: x["title"]
    )
)
@patch("dr_util.file_utils.load_file")
@patch("dr_util.file_utils.dump_file")
def test_roam_graph_checkpoint_hypothesis(mock_dump_file, mock_load_file, data):
    # Mock file loading and checkpoint saving
    mock_load_file.return_value = data

    graph = gu.RoamGraph("fake_path", checkpoint_path="fake_checkpoint")  # noqa: F841

    # Check that dump_file was called to save a checkpoint
    mock_dump_file.assert_called_once()


@given(
    data=st.lists(
        nested_roam_dict_st(), min_size=1, max_size=10, unique_by=lambda x: x["title"]
    )
)
@patch("dr_util.file_utils.load_file")
def test_roam_graph_get_page_node_by_index_hypothesis(mock_load_file, data):
    mock_load_file.return_value = data
    graph = gu.RoamGraph("fake_path")

    for idx, page in enumerate(data):
        page_node = graph.get_page_node_by_index(idx)
        assert page_node.uid == page["uid"]
        assert page_node.title == page["title"]
