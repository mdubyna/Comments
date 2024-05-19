from django.urls import path

from comment import views


urlpatterns = [
    path("", views.index, name="index"),
    path("generate_captcha/", views.generate_captcha, name='generate_captcha'),
]
