from django.db import connection
from django.http import JsonResponse
from django.shortcuts import redirect

from business_os.apps.websites.models import Website


def root(request):
    if getattr(request, "website", None) is not None:
        from business_os.apps.websites.views import render_public_home

        return render_public_home(request, request.website)

    if getattr(request, "host_surface", "") == "platform_admin":
        from business_os.portals.views import platform_overview

        return platform_overview(request)

    if getattr(request, "host_surface", "") in {
        "marketing",
        "business_admin",
        "api",
        "docs",
        "status",
    }:
        return JsonResponse(
            {
                "status": "ok",
                "surface": request.host_surface,
                "message": "Business OS canonical host is running.",
            }
        )

    website = Website.objects.order_by("created_at").first()
    if website:
        return redirect("public-home", site_slug=website.slug)
    return JsonResponse(
        {
            "status": "ok",
            "message": "Business OS is running. Seed data has not been created yet.",
        }
    )


def health_live(request):
    return JsonResponse({"status": "ok"})


def health_ready(request):
    return JsonResponse({"status": "ok"})


def health_database(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        cursor.fetchone()
    return JsonResponse({"status": "ok", "database": "reachable"})
