from ambient_toolbox.import_linter.services import ImportLinterContractService


def validate_import_linter_contracts(*args, **kwargs):
    service = ImportLinterContractService()
    service.process()
