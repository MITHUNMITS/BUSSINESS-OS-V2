from django.urls import path

from business_os.apps.websites import views

urlpatterns = [
    path("p/<slug:page_slug>/", views.public_current_site_page, name="public-current-page"),
    path("sites/<slug:site_slug>/", views.public_home, name="public-home"),
    path("sites/<slug:site_slug>/p/<slug:page_slug>/", views.public_page, name="public-page"),
]
