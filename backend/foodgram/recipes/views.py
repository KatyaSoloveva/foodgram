from django.shortcuts import redirect, get_object_or_404
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes

from .models import URL


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def redirect_view(request, slug):
    """Редирект с короткой ссылки рецепта на обычную."""
    obj = get_object_or_404(URL, hash=slug)
    return redirect(obj.url)
