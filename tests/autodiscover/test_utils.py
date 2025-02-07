from ambient_toolbox.autodiscover.utils import unique_append_to_inner_list


def test_unique_append_to_inner_list_key_doesnt_exist():
    data = {}
    data = unique_append_to_inner_list(data=data, key="new_key", value=1)

    assert len(data) == 1
    assert "new_key" in data
    assert data["new_key"] == [1]


def test_unique_append_to_inner_list_key_exists():
    data = {"my_key": [1]}
    data = unique_append_to_inner_list(data=data, key="my_key", value=2)

    assert len(data) == 1
    assert "my_key" in data
    assert data["my_key"] == [1, 2]


def test_unique_append_to_inner_list_value_exists():
    data = {"my_key": [1]}
    data = unique_append_to_inner_list(data=data, key="my_key", value=1)

    assert len(data) == 1
    assert "my_key" in data
    assert data["my_key"] == [1]
