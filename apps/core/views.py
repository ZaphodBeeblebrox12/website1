"""
Core views for community platform.
"""
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET"])
def health_check(request):
    """Health check endpoint."""
    return JsonResponse({"status": "ok", "service": "community-platform"})


@require_http_methods(["GET"])
def index(request):
    """Landing page."""
    return render(request, "index.html")
