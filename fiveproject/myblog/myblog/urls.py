"""
URL configuration for myblog project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include
from django.contrib.auth import views as auth_views
from articles import views as articles_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', articles_views.article_list, name='home'),
    path('articles/<int:pk>/', articles_views.article_detail, name='article_detail'),
    path('articles/new/', articles_views.article_create, name='article_create'),
    path('register/', articles_views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='articles/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]