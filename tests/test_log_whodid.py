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


def test_log_who_did_no_created_by_attribute(mocker):
    """
    Tests if an object without a ``created_by`` attribute is handled properly.
    Only the ``lastmodified_by`` field should be updated.
    """
    user = mocker.MagicMock()
    obj = mocker.MagicMock()
    # Remove the created_by attribute
    del obj.created_by
    log_whodid(obj, user)
    # created_by should not exist
    assert not hasattr(obj, "created_by")
    # lastmodified_by should be set
    assert obj.lastmodified_by == user


def test_log_who_did_no_lastmodified_by_attribute(mocker):
    """
    Tests if an object without a ``lastmodified_by`` attribute is handled properly.
    Only the ``created_by`` field should be updated (if it's None).
    """
    user = mocker.MagicMock()
    obj = mocker.MagicMock()
    obj.created_by = None
    # Remove the lastmodified_by attribute
    del obj.lastmodified_by
    log_whodid(obj, user)
    # created_by should be set
    assert obj.created_by == user
    # lastmodified_by should not exist
    assert not hasattr(obj, "lastmodified_by")


def test_log_who_did_no_attributes(mocker):
    """
    Tests if an object without both ``created_by`` and ``lastmodified_by`` attributes is handled properly.
    Function should complete without error and not add any attributes.
    """
    user = mocker.MagicMock()
    obj = mocker.MagicMock()
    # Remove both attributes
    del obj.created_by
    del obj.lastmodified_by
    log_whodid(obj, user)
    # Neither attribute should exist
    assert not hasattr(obj, "created_by")
    assert not hasattr(obj, "lastmodified_by")


def test_log_who_did_with_created_by_but_no_lastmodified_by(mocker):
    """
    Tests if an object with ``created_by`` but without ``lastmodified_by`` is handled properly.
    The ``created_by`` should not be changed if already set.
    """
    user = mocker.MagicMock()
    old_user = mocker.MagicMock()
    obj = mocker.MagicMock()
    obj.created_by = old_user
    # Remove the lastmodified_by attribute
    del obj.lastmodified_by
    log_whodid(obj, user)
    # created_by should remain unchanged
    assert obj.created_by == old_user
    # lastmodified_by should not exist
    assert not hasattr(obj, "lastmodified_by")
