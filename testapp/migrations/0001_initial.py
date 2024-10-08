# Generated by Django 5.0.7 on 2024-09-24 03:59

import ambient_toolbox.mixins.bleacher
import ambient_toolbox.mixins.models
import ambient_toolbox.mixins.validation
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="MyPermissionModelMixin",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
            ],
            options={
                "managed": False,
            },
            bases=(ambient_toolbox.mixins.models.PermissionModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name="BleacherMixinModel",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("content", models.CharField(max_length=50)),
            ],
            bases=(ambient_toolbox.mixins.bleacher.BleacherMixin, models.Model),
        ),
        migrations.CreateModel(
            name="ModelNameTimeBasedFieldTest",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("wrongly_named_date_field", models.DateField()),
                ("wrongly_named_datetime_field", models.DateTimeField()),
                ("timestamp_date", models.DateField()),
                ("timestamped_at", models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name="ModelWithCleanMixin",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
            ],
            bases=(ambient_toolbox.mixins.validation.CleanOnSaveMixin, models.Model),
        ),
        migrations.CreateModel(
            name="ModelWithSaveWithoutSignalsMixin",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("value", models.PositiveIntegerField(default=0)),
            ],
            bases=(ambient_toolbox.mixins.models.SaveWithoutSignalsMixin, models.Model),
        ),
        migrations.CreateModel(
            name="ModelWithSelector",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("value", models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name="MyMultipleSignalModel",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("value", models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name="MySingleSignalModel",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("value", models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name="CommonInfoBasedModel",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        db_index=True,
                        default=django.utils.timezone.now,
                        verbose_name="Created at",
                    ),
                ),
                (
                    "lastmodified_at",
                    models.DateTimeField(
                        db_index=True,
                        default=django.utils.timezone.now,
                        verbose_name="Last modified at",
                    ),
                ),
                ("value", models.PositiveIntegerField(default=0)),
                ("value_b", models.PositiveIntegerField(default=0)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(app_label)s_%(class)s_created",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Created by",
                    ),
                ),
                (
                    "lastmodified_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="%(app_label)s_%(class)s_lastmodified",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Last modified by",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ModelWithFkToSelf",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="children",
                        to="testapp.modelwithfktoself",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ModelWithOneToOneToSelf",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "peer",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="related_peer",
                        to="testapp.modelwithonetoonetoself",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ForeignKeyRelatedModel",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "single_signal",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="foreign_key_related_models",
                        to="testapp.mysinglesignalmodel",
                    ),
                ),
            ],
        ),
    ]
