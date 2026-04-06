"""Templates for generating Django model code."""

# Maps GUI-friendly field names to Django field classes + default kwargs
FIELD_TYPE_MAP = {
    "CharField": ("models.CharField", {"max_length": 255}),
    "TextField": ("models.TextField", {}),
    "IntegerField": ("models.IntegerField", {}),
    "FloatField": ("models.FloatField", {}),
    "DecimalField": ("models.DecimalField", {"max_digits": 10, "decimal_places": 2}),
    "BooleanField": ("models.BooleanField", {"default": False}),
    "DateField": ("models.DateField", {}),
    "DateTimeField": ("models.DateTimeField", {}),
    "EmailField": ("models.EmailField", {}),
    "URLField": ("models.URLField", {}),
    "SlugField": ("models.SlugField", {"unique": True}),
    "ImageField": ("models.ImageField", {"upload_to": "'images/'"}),
    "FileField": ("models.FileField", {"upload_to": "'files/'"}),
    "ForeignKey": ("models.ForeignKey", {"on_delete": "models.CASCADE"}),
    "OneToOneField": ("models.OneToOneField", {"on_delete": "models.CASCADE"}),
    "ManyToManyField": ("models.ManyToManyField", {}),
    "AutoField": ("models.AutoField", {"primary_key": True}),
    "UUIDField": ("models.UUIDField", {"default": "uuid.uuid4", "editable": False}),
    "JSONField": ("models.JSONField", {"default": "dict"}),
    "PositiveIntegerField": ("models.PositiveIntegerField", {}),
}

COMMON_FIELD_TYPES = list(FIELD_TYPE_MAP.keys())


def generate_model_code(model_name: str, fields: list[dict]) -> str:
    """
    Generate a complete Django model class.

    Each field dict should contain:
        - name: str          (field name)
        - type: str          (key in FIELD_TYPE_MAP)
        - options: dict      (extra kwargs, overrides defaults)

    Returns a string of Python source code.
    """
    lines = [
        "from django.db import models",
        "",
        "",
        f"class {model_name}(models.Model):",
    ]

    if not fields:
        lines.append("    pass")
    else:
        for field in fields:
            field_name = field["name"]
            field_type = field["type"]
            extra_options = field.get("options", {})

            if field_type not in FIELD_TYPE_MAP:
                field_class = f"models.{field_type}"
                kwargs = extra_options
            else:
                field_class, default_kwargs = FIELD_TYPE_MAP[field_type]
                kwargs = {**default_kwargs, **extra_options}

            kwargs_str = ", ".join(
                f"{k}={v}" if not isinstance(v, str) or v.startswith(("'", '"', "models.", "uuid.", "dict", "list"))
                else f"{k}='{v}'"
                for k, v in kwargs.items()
            )
            lines.append(f"    {field_name} = {field_class}({kwargs_str})")

        # Add __str__ and Meta
        lines.extend([
            "",
            f"    class Meta:",
            f"        verbose_name = '{model_name}'",
            f"        verbose_name_plural = '{model_name}s'",
            f"        ordering = ['-id']",
            "",
            f"    def __str__(self):",
        ])

        # Use the first CharField or the first field for __str__
        str_field = fields[0]["name"]
        for f in fields:
            if f["type"] == "CharField":
                str_field = f["name"]
                break
        lines.append(f"        return str(self.{str_field})")

    lines.append("")
    return "\n".join(lines)


def generate_admin_registration(model_name: str, fields: list[dict]) -> str:
    """Generate admin.py registration code for a model."""
    char_fields = [f["name"] for f in fields if f["type"] in ("CharField", "EmailField", "SlugField")]
    list_display = [f["name"] for f in fields[:5]]  # Show first 5 fields
    search_fields = char_fields[:3] if char_fields else [fields[0]["name"]] if fields else []

    lines = [
        "from django.contrib import admin",
        f"from .models import {model_name}",
        "",
        "",
        f"@admin.register({model_name})",
        f"class {model_name}Admin(admin.ModelAdmin):",
    ]

    if list_display:
        lines.append(f"    list_display = {list_display}")
    if search_fields:
        lines.append(f"    search_fields = {search_fields}")

    lines.append("")
    return "\n".join(lines)