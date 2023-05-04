from django.views import generic

from ambient_toolbox.view_layer.views import UserInFormKwargsMixin
from testapp.forms import CommonInfoBasedModelTestForm


class UserInFormKwargsMixinView(UserInFormKwargsMixin, generic.FormView):
    """
    Generic view for updating an object without any user data being sent. Therefore, we don't need a form to validate
    user input.
    Most common use-case is toggling a flag inside an object.
    """

    form_class = CommonInfoBasedModelTestForm
