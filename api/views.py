from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse


@require_http_methods(['POST'])
def login(request):
    username = request.POST.get('username')
    password = request.POST.get('password')

    user = authenticate(request, username=username, password=password)

    if user is not None:
        # Authentication successful
        django_login(request, user)
        return HttpResponse(("Welcome ", user.first_name), status=200, content_type='text/plain')
    else:
        # Authentication failed
        return HttpResponse("Authentication failed, username or password incorrect.", status=401, content_type='text/plain')


@require_http_methods(['POST'])
def logout(request):
    print(django_logout(request))
    if request.user.is_authenticated:
        return HttpResponse("Goodbye.", status=200, content_type='text/plain')
    else:
        return HttpResponse("Method not allowed", status=405, content_type='text/plain')






