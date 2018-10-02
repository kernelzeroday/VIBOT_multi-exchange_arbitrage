import hashlib
import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.models import User
from .handlers import start_handler, stop_handler, pause_handler, update_config_handler
from django.views.decorators.csrf import csrf_exempt
from arbitrage_interface.settings import DEFAULT_CONFIG, ALLOWS_CONFIG_ELEMENTS


@login_required
def index(request):
    new_messages = messages.get_messages(request)
    context = {
        'default': DEFAULT_CONFIG,
        'allows': ALLOWS_CONFIG_ELEMENTS,
        'messages': new_messages
    }
    return render(request, 'index.html', context)


@login_required
def start(request):
    result = start_handler()
    messages.add_message(request, messages.INFO, result)
    return redirect('main_app:index')


@login_required
def stop(request):
    result = stop_handler()
    messages.add_message(request, messages.INFO, result)
    return redirect('main_app:index')


@login_required
def pause(request):
    result = pause_handler()
    messages.add_message(request, messages.INFO, result)
    return redirect('main_app:index')


@csrf_exempt
def update_config(request):
    if request.method != 'POST':
        return redirect('arbitrage_app:index')  # todo: add error
    data = json.loads(request.body.decode('utf8'))
    if 'type' in data:
        return json.dumps(
            {'success': False, 'error': "Expected 'type' and 'data, instead %s" % data})
    if data['type'] is not 'config':
        return json.dumps(
            {'success': False, 'error': 'Unexpected request type %s' % data['type']})
    result = update_config_handler(data['data'])
    messages.add_message(request, messages.INFO, result)
    return redirect('main_app:index')
