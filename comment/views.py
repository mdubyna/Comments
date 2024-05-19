from django.shortcuts import render

from captcha.image import ImageCaptcha
from django.http import HttpResponse, HttpRequest
import random
import string


def index(request: HttpRequest) -> HttpResponse:
    """View function for index page"""
    return render(request, "comments/index.html")


def generate_captcha(request: HttpRequest) -> HttpResponse:
    """View function for generating captcha image"""
    image = ImageCaptcha(width=280, height=90)
    captcha_text = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    data = image.generate(captcha_text)
    request.session["captcha_text"] = captcha_text
    request.session.modified = True
    return HttpResponse(data.read(), content_type="image/png")
