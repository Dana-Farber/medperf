from django.db import models
from django.contrib.auth.models import User


class Dataset(models.Model):
    DATASET_STATE = (
        ("DEVELOPMENT", "DEVELOPMENT"),
        ("OPERATION", "OPERATION"),
    )

    name = models.CharField(max_length=20)
    description = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=100, blank=True)
    owner = models.ForeignKey(User, on_delete=models.PROTECT)
    input_data_hash = models.CharField(max_length=128)
    generated_uid = models.CharField(max_length=128, unique=True)
    split_seed = models.IntegerField()
    data_preparation_mlcube = models.ForeignKey(
        "mlcube.MlCube",
        on_delete=models.PROTECT,
        related_name="benchmark_preprocessor_mlcube",
    )
    is_valid = models.BooleanField(default=True)
    state = models.CharField(choices=DATASET_STATE, max_length=100, default="DEVELOPMENT")
    generated_metadata = models.JSONField(default=dict, blank=True, null=True)
    user_metadata = models.JSONField(default=dict, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["modified_at"]
