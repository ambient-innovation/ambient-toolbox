from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory
from django.test import TestCase

from ambient_toolbox.view_layer.formset_mixins import CountChildrenFormsetMixin
from testapp.models import ForeignKeyRelatedModel, MySingleSignalModel


class ForeignKeyRelatedModelForm(forms.ModelForm):
    class Meta:
        model = ForeignKeyRelatedModel
        fields = ("single_signal",)


class MySingleSignalModelFormset(CountChildrenFormsetMixin, BaseInlineFormSet):
    pass


class CountChildrenFormsetMixinTest(TestCase):
    def test_simple_no_data(self):
        formset_class = inlineformset_factory(
            MySingleSignalModel,
            ForeignKeyRelatedModel,
            form=ForeignKeyRelatedModelForm,
            formset=MySingleSignalModelFormset,
            extra=3,
            can_delete=True,
            max_num=3,
        )

        formset = formset_class()
        self.assertEqual(formset.get_number_of_children(), 0)

    def test_regular_with_data(self):
        mssm = MySingleSignalModel.objects.create(value=27)
        ForeignKeyRelatedModel.objects.create(single_signal=mssm)
        ForeignKeyRelatedModel.objects.create(single_signal=mssm)

        formset_class = inlineformset_factory(
            MySingleSignalModel,
            ForeignKeyRelatedModel,
            form=ForeignKeyRelatedModelForm,
            formset=MySingleSignalModelFormset,
            extra=3,
            can_delete=True,
            max_num=3,
        )

        formset = formset_class(
            {"fkrm-INITIAL_FORMS": "2", "fkrm-MIN_NUM_FORMS": "2", "fkrm-MAX_NUM_FORMS": "3", "fkrm-TOTAL_FORMS": "2"},
            None,
            instance=mssm,
            prefix="fkrm",
        )

        formset.is_valid()
        self.assertEqual(formset.get_number_of_children(), 2)
