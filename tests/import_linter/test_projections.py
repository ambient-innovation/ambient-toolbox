from ambient_toolbox.import_linter.projections import ImportLinterContract


def test_generate_contract_creates_expected_instance():
    contract = ImportLinterContract.generate_contract("my_app", ["other_app1", "other_app2"])

    assert isinstance(contract, ImportLinterContract)
    assert contract.name == "[GENERATED] Independent app 'my_app' not allowed"
    assert contract.type == "forbidden"
    assert contract.source_modules == "my_app"
    assert contract.forbidden_modules == ["other_app1", "other_app2"]


def test_to_dict_returns_expected_structure():
    contract = ImportLinterContract(
        name="custom name",
        type="forbidden",
        source_modules="app_a",
        forbidden_modules=["app_b", "app_c"],
    )

    result = contract.to_dict()

    assert result == {
        "name": "[GENERATED] Independent app 'app_a' not allowed to know about other apps",
        "type": "forbidden",
        "source_modules": "app_a",
        "forbidden_modules": ["app_b", "app_c"],
    }


def test_manual_init_is_possible():
    contract = ImportLinterContract(
        name="manual",
        type="forbidden",
        source_modules="src",
        forbidden_modules=[],
    )

    assert contract.name == "manual"
    assert contract.forbidden_modules == []
