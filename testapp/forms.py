from django import forms

from testapp.models import CommonInfoBasedModel


class CommonInfoBasedModelTestForm(forms.ModelForm):
    class Meta:
        model = CommonInfoBasedModel
        fields = ("value",)
