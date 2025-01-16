from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from ambient_toolbox.managers import GloballyVisibleQuerySet
from ambient_toolbox.mixins.bleacher import BleacherMixin
from ambient_toolbox.mixins.models import PermissionModelMixin, SaveWithoutSignalsMixin
from ambient_toolbox.mixins.validation import CleanOnSaveMixin
from ambient_toolbox.models import CommonInfo
from testapp.managers import ModelWithGetOrNoneManager, ModelWithSelectorQuerySet
from testapp.selectors import ModelWithSelectorGloballyVisibleSelector


class MySingleSignalModel(models.Model):
    value = models.PositiveIntegerField(default=0)

    objects = GloballyVisibleQuerySet.as_manager()

    def __str__(self):
        return str(self.value)


class ForeignKeyRelatedModel(models.Model):
    single_signal = models.ForeignKey(
        MySingleSignalModel, on_delete=models.CASCADE, related_name="foreign_key_related_models"
    )

    objects = GloballyVisibleQuerySet.as_manager()

    def __str__(self):
        return str(self.id)


@receiver(pre_save, sender=MySingleSignalModel)
def increase_value_no_dispatch_uid(sender, instance, **kwargs):
    instance.value += 1


class MyMultipleSignalModel(models.Model):
    value = models.PositiveIntegerField(default=0)

    def __str__(self):
        return str(self.value)


@receiver(pre_save, sender=MyMultipleSignalModel, dispatch_uid="test.mysinglesignalmodel.increase_value_with_uuid")
def increase_value_with_dispatch_uid(sender, instance, **kwargs):
    instance.value += 1


@receiver(post_save, sender=MyMultipleSignalModel)
def send_email(sender, instance, **kwargs):
    msg = EmailMultiAlternatives(
        "Test Mail", "I am content", from_email="test@example.com", to=["random.dude@example.com"]
    )
    msg.send()


class CommonInfoBasedModel(CommonInfo):
    value = models.PositiveIntegerField(default=0)
    value_b = models.PositiveIntegerField(default=0)

    def __str__(self):
        return str(self.value)


class ModelWithSelector(models.Model):
    value = models.PositiveIntegerField(default=0)

    objects = ModelWithSelectorQuerySet.as_manager()
    selectors = ModelWithSelectorGloballyVisibleSelector()

    def __str__(self):
        return str(self.value)


class ModelWithFkToSelf(models.Model):
    parent = models.ForeignKey("self", blank=True, null=True, related_name="children", on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)


class ModelWithOneToOneToSelf(models.Model):
    peer = models.OneToOneField("self", blank=True, null=True, related_name="related_peer", on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)


class ModelWithCleanMixin(CleanOnSaveMixin, models.Model):
    def __str__(self):
        return str(self.id)

    def clean(self):
        return True


class MyPermissionModelMixin(PermissionModelMixin, models.Model):
    def __str__(self):
        return str(self.id)


class BleacherMixinModel(BleacherMixin, models.Model):
    BLEACH_FIELD_LIST = ["content"]

    content = models.CharField(max_length=50)

    def __str__(self):
        return self.content


class ModelWithSaveWithoutSignalsMixin(SaveWithoutSignalsMixin, models.Model):
    value = models.PositiveIntegerField(default=0)

    def __str__(self):
        return str(self.value)


@receiver(pre_save, sender=ModelWithSaveWithoutSignalsMixin)
def increase_value_on_pre_save(sender, instance, **kwargs):
    instance.value += 1


class ModelNameTimeBasedFieldTest(models.Model):
    wrongly_named_date_field = models.DateField()
    wrongly_named_datetime_field = models.DateTimeField()
    timestamp_date = models.DateField()
    timestamped_at = models.DateTimeField()

    def __str__(self):
        return self.id


class ModelWithoutRelatedNameOnFieldAndMeta(models.Model):
    relation_field = models.ForeignKey("auth.User", related_name=None, on_delete=models.CASCADE)

    def __str__(self):
        return self.id


class ModelWithoutRelatedNameOnFieldButWithMeta(models.Model):
    relation_field = models.ForeignKey("auth.User", related_name=None, on_delete=models.CASCADE)

    class Meta:
        default_related_name = "model_without_related_name_on_field_but_with_metas"

    def __str__(self):
        return self.id


class ModelWithGetOrNoneManagerModel(models.Model):
    my_field = models.BooleanField(default=False)

    objects = ModelWithGetOrNoneManager()

    def __str__(self):
        return self.id
