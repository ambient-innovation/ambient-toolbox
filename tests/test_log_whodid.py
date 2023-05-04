from ambient_toolbox.utils import log_whodid


def test_log_who_did_new_object(mocker):
    """
    Tests if a new object that doesn't have a value for the ``created_by`` and ``lastmodified_by`` fields, is handled
    properly.
    """
    user = mocker.MagicMock()
    obj = mocker.MagicMock()
    obj.created_by = None
    log_whodid(obj, user)
    assert obj.created_by == user
    assert obj.lastmodified_by == user


def test_log_who_did_existing_values(mocker):
    """
    Tests if, for an object that already has a value for ``created_by``, only the ``lastmodified_by`` field is updated.
    """
    user = mocker.MagicMock()
    obj = mocker.MagicMock()
    old_user = obj.created_by
    log_whodid(obj, user)
    assert obj.created_by == old_user
    assert obj.lastmodified_by == user
