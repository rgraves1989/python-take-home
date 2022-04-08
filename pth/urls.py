"""pth URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from rest_api_app import views as rest_api_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', rest_api_views.main),
    path('github_oauth_callback', rest_api_views.github_oauth_callback),
    path('google_login_callback', rest_api_views.google_login_callback),
    path('logout', rest_api_views.user_logout),
    path('save_user_repo', rest_api_views.save_user_repo)
    path('payload_receive', rest_api_views.github_payload_receive)
]

#made a change 7