from django.urls import path

from business_os.portals import views

urlpatterns = [
    path("", views.platform_overview, name="platform-overview"),
    path("modules/", views.platform_modules, name="platform-modules"),
    path("organizations/", views.platform_organizations, name="platform-organizations"),
]
