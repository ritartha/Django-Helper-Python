"""Templates for generating HTML scaffold files."""


def generate_base_template(project_name: str = "My Project") -> str:
    """Generate a base.html template."""
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{% block title %}}{project_name}{{% endblock %}}</title>
    {{% block extra_css %}}{{% endblock %}}
</head>
<body>
    <nav>
        <!-- Navigation bar -->
    </nav>

    <main>
        {{% block content %}}
        {{% endblock %}}
    </main>

    <footer>
        <p>&copy; {project_name}</p>
    </footer>

    {{% block extra_js %}}{{% endblock %}}
</body>
</html>
'''


def generate_list_template(model_name: str) -> str:
    """Generate a list view template."""
    lower = model_name.lower()
    return f'''{{% extends 'base.html' %}}

{{% block title %}}{model_name} List{{% endblock %}}

{{% block content %}}
<h1>{model_name} List</h1>
<ul>
    {{% for item in {lower}_list %}}
    <li>
        <a href="{{% url '{lower}-detail' item.pk %}}">{{{{ item }}}}</a>
    </li>
    {{% empty %}}
    <li>No {lower}s found.</li>
    {{% endfor %}}
</ul>
{{% endblock %}}
'''


def generate_detail_template(model_name: str, fields: list[str] | None = None) -> str:
    """Generate a detail view template."""
    lower = model_name.lower()
    field_rows = ""
    if fields:
        for f in fields:
            field_rows += f"    <p><strong>{f}:</strong> {{{{ {lower}.{f} }}}}</p>\n"
    else:
        field_rows = f"    <p>{{{{ {lower} }}}}</p>\n"

    return f'''{{% extends 'base.html' %}}

{{% block title %}}{model_name} Detail{{% endblock %}}

{{% block content %}}
<h1>{model_name} Detail</h1>
<div>
{field_rows}</div>
<a href="{{% url '{lower}-list' %}}">Back to list</a>
{{% endblock %}}
'''


def generate_form_template(model_name: str) -> str:
    """Generate a form (create/update) template."""
    return f'''{{% extends 'base.html' %}}

{{% block title %}}{model_name} Form{{% endblock %}}

{{% block content %}}
<h1>{model_name} Form</h1>
<form method="post">
    {{% csrf_token %}}
    {{{{ form.as_p }}}}
    <button type="submit">Save</button>
</form>
{{% endblock %}}
'''