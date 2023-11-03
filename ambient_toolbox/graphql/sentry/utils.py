from sentry_sdk.integrations.logging import ignore_logger


def ignore_graphene_logger():
    """
    A utils function that can be called to ignore a graphene logger that logs errors as strings instead of errors.
    This leads to a loss of Sentry's features. Instead, you can report the original exception.

    Test for:
        * sentry_sdk >= 0.13.0
    """
    ignore_logger("graphql.execution.utils")
