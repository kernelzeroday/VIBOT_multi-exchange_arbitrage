from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def stream(requests):
    return render(requests, 'stream.html')
