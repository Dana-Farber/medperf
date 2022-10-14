# Generated by Django 3.2.10 on 2022-03-07 09:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("mlcube", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Dataset",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=20)),
                ("description", models.CharField(blank=True, max_length=20)),
                ("location", models.CharField(blank=True, max_length=100)),
                ("input_data_hash", models.CharField(max_length=128)),
                ("generated_uid", models.CharField(max_length=128, unique=True)),
                ("split_seed", models.IntegerField()),
                ("is_valid", models.BooleanField(default=True)),
                (
                    "state",
                    models.CharField(
                        choices=[
                            ("DEVELOPMENT", "DEVELOPMENT"),
                            ("OPERATION", "OPERATION"),
                        ],
                        default="DEVELOPMENT",
                        max_length=100,
                    ),
                ),
                (
                    "generated_metadata",
                    models.JSONField(blank=True, default=dict, null=True),
                ),
                (
                    "user_metadata",
                    models.JSONField(blank=True, default=dict, null=True),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "data_preparation_mlcube",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="benchmark_preprocessor_mlcube",
                        to="mlcube.mlcube",
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"ordering": ["modified_at"],},
        ),
    ]
