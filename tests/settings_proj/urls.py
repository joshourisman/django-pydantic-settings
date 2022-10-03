from django.http import JsonResponse
from django.urls import path


def test_view(request):
    return JsonResponse({"success": True})


urlpatterns = [
    path("", test_view),
]
