"""Templates for generating Django REST Framework serializers."""


def generate_model_serializer(model_name: str, fields: list[str] | None = None) -> str:
    """Generate a DRF ModelSerializer."""
    fields_val = fields if fields else "'__all__'"
    if isinstance(fields_val, list):
        fields_val = str(fields_val)
    return f'''from rest_framework import serializers
from .models import {model_name}


class {model_name}Serializer(serializers.ModelSerializer):
    """Serializer for the {model_name} model."""

    class Meta:
        model = {model_name}
        fields = {fields_val}
'''