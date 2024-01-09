import json
import secrets
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import User


@csrf_exempt
@require_POST
def signup(request):
    data = json.loads(request.body)
    required = ["email", "password"]
    for i in required:
        if i not in data.keys():
            return JsonResponse(
                {"message": "Please enter your email and password"}, status=400
            )

    try:
        user = User.objects.get(email=data["email"])
        return JsonResponse({"message": "User already exists"}, status=400)
    except User.DoesNotExist:
        api_key = secrets.token_urlsafe(20)
        user = User.objects.create_user(email=data["email"], password=data["password"])
        user.api_key = api_key
        user.save()
        return JsonResponse({"api_key": api_key})
