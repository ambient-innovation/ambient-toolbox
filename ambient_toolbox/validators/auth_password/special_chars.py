import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class SpecialCharValidator:
    """
    The password must contain at least one special character (@#$%!^&*)
    """

    def validate(self, password, user=None):
        if not re.findall("[@#$%!^&*]", password):
            raise ValidationError(
                _('The password has to contain one of the following special characters: "@#$%!^&*"'),
                code="password_no_symbol",
            )

    def get_help_text(self):
        return _('The password has to contain one of the following special characters: "@#$%!^&*"')
