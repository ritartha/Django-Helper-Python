"""Templates for generating Django views."""


def generate_fbv(view_name: str, template_name: str = "") -> str:
    """Generate a function-based view."""
    tmpl = template_name or f"{view_name.lower()}.html"
    return f'''from django.shortcuts import render


def {view_name}(request):
    """Handle requests for the {view_name} page."""
    context = {{}}
    return render(request, '{tmpl}', context)
'''


def generate_cbv(view_name: str, model_name: str = "", view_type: str = "TemplateView") -> str:
    """Generate a class-based view."""
    templates = {
        "TemplateView": _template_view,
        "ListView": _list_view,
        "DetailView": _detail_view,
        "CreateView": _create_view,
        "UpdateView": _update_view,
        "DeleteView": _delete_view,
    }
    generator = templates.get(view_type, _template_view)
    return generator(view_name, model_name)


def _template_view(view_name: str, _model: str = "") -> str:
    return f'''from django.views.generic import TemplateView


class {view_name}(TemplateView):
    """Render a static template."""
    template_name = '{view_name.lower()}.html'
'''


def _list_view(view_name: str, model_name: str = "") -> str:
    model_import = f"from .models import {model_name}" if model_name else "# from .models import YourModel"
    model_ref = model_name or "YourModel"
    return f'''from django.views.generic import ListView
{model_import}


class {view_name}(ListView):
    """List all {model_ref} objects."""
    model = {model_ref}
    template_name = '{view_name.lower()}.html'
    context_object_name = '{model_ref.lower()}_list'
    paginate_by = 10
'''


def _detail_view(view_name: str, model_name: str = "") -> str:
    model_import = f"from .models import {model_name}" if model_name else "# from .models import YourModel"
    model_ref = model_name or "YourModel"
    return f'''from django.views.generic import DetailView
{model_import}


class {view_name}(DetailView):
    """Display a single {model_ref} instance."""
    model = {model_ref}
    template_name = '{view_name.lower()}.html'
    context_object_name = '{model_ref.lower()}'
'''


def _create_view(view_name: str, model_name: str = "") -> str:
    model_import = f"from .models import {model_name}" if model_name else "# from .models import YourModel"
    model_ref = model_name or "YourModel"
    return f'''from django.views.generic import CreateView
from django.urls import reverse_lazy
{model_import}


class {view_name}(CreateView):
    """Create a new {model_ref} instance."""
    model = {model_ref}
    fields = '__all__'
    template_name = '{view_name.lower()}_form.html'
    success_url = reverse_lazy('{model_ref.lower()}-list')
'''


def _update_view(view_name: str, model_name: str = "") -> str:
    model_import = f"from .models import {model_name}" if model_name else "# from .models import YourModel"
    model_ref = model_name or "YourModel"
    return f'''from django.views.generic import UpdateView
from django.urls import reverse_lazy
{model_import}


class {view_name}(UpdateView):
    """Update an existing {model_ref} instance."""
    model = {model_ref}
    fields = '__all__'
    template_name = '{view_name.lower()}_form.html'
    success_url = reverse_lazy('{model_ref.lower()}-list')
'''


def _delete_view(view_name: str, model_name: str = "") -> str:
    model_import = f"from .models import {model_name}" if model_name else "# from .models import YourModel"
    model_ref = model_name or "YourModel"
    return f'''from django.views.generic import DeleteView
from django.urls import reverse_lazy
{model_import}


class {view_name}(DeleteView):
    """Delete a {model_ref} instance."""
    model = {model_ref}
    template_name = '{view_name.lower()}_confirm_delete.html'
    success_url = reverse_lazy('{model_ref.lower()}-list')
'''


def generate_drf_apiview(view_name: str, model_name: str = "", serializer_name: str = "") -> str:
    """Generate a DRF API view with list and create capabilities."""
    model_ref = model_name or "YourModel"
    serializer_ref = serializer_name or f"{model_ref}Serializer"
    return f'''from rest_framework import generics
from .models import {model_ref}
from .serializers import {serializer_ref}


class {view_name}List(generics.ListCreateAPIView):
    """API endpoint: list all {model_ref}s or create a new one."""
    queryset = {model_ref}.objects.all()
    serializer_class = {serializer_ref}


class {view_name}Detail(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint: retrieve, update, or delete a {model_ref}."""
    queryset = {model_ref}.objects.all()
    serializer_class = {serializer_ref}
'''


def generate_drf_viewset(view_name: str, model_name: str = "", serializer_name: str = "") -> str:
    """Generate a DRF ModelViewSet."""
    model_ref = model_name or "YourModel"
    serializer_ref = serializer_name or f"{model_ref}Serializer"
    return f'''from rest_framework import viewsets
from .models import {model_ref}
from .serializers import {serializer_ref}


class {view_name}ViewSet(viewsets.ModelViewSet):
    """CRUD API for {model_ref} using a ModelViewSet."""
    queryset = {model_ref}.objects.all()
    serializer_class = {serializer_ref}
'''