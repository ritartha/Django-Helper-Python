"""Templates for generating Django URL configurations."""


def generate_app_urls(app_name: str, views: list[dict] | None = None) -> str:
    """
    Generate a urls.py file for an app.

    Each view dict can contain:
        - name: str          (view function/class name)
        - path: str          (URL path, e.g. '' or '<int:pk>/')
        - view_type: str     ('fbv' | 'cbv')
    """
    lines = [
        f"from django.urls import path",
        f"from . import views",
        "",
        f"app_name = '{app_name}'",
        "",
        "urlpatterns = [",
    ]

    if views:
        for v in views:
            name = v["name"]
            url_path = v.get("path", "")
            view_type = v.get("view_type", "fbv")

            if view_type == "cbv":
                lines.append(f"    path('{url_path}', views.{name}.as_view(), name='{name.lower()}'),")
            else:
                lines.append(f"    path('{url_path}', views.{name}, name='{name.lower()}'),")
    else:
        lines.append(f"    # Add your URL patterns here")

    lines.extend(["]", ""])
    return "\n".join(lines)


def generate_include_line(app_name: str, prefix: str = "") -> str:
    """Generate an include() line for the project-level urls.py."""
    url_prefix = prefix or f"{app_name}/"
    return f"path('{url_prefix}', include('{app_name}.urls')),"


def generate_project_urls(project_name: str, apps: list[str] | None = None) -> str:
    """Generate the project-level urls.py content."""
    lines = [
        "from django.contrib import admin",
        "from django.urls import path, include",
        "",
        "urlpatterns = [",
        "    path('admin/', admin.site.urls),",
    ]
    if apps:
        for app in apps:
            lines.append(f"    path('{app}/', include('{app}.urls')),")
    lines.extend(["]", ""])
    return "\n".join(lines)