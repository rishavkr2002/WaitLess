
from django.http import JsonResponse


def home(request):
    return JsonResponse({
        "project": "WaitLess",
        "message": "Smart Virtual Queue Manager API is running!",
        "status": "success",
    })
