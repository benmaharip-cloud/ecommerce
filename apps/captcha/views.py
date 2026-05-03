from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .captcha import generate_captcha
import json

def get_captcha(request):
    """API: retourne un nouveau captcha."""
    ctype = request.GET.get("type")
    data, answer = generate_captcha(ctype)
    request.session["captcha_answer"] = answer
    request.session["captcha_type"] = data["type"]
    return JsonResponse(data)

@require_POST
def verify_captcha(request):
    """API: vérifie la réponse."""
    body = json.loads(request.body)
    user_answer = str(body.get("answer", "")).strip()
    correct = str(request.session.get("captcha_answer", "")).strip()
    ctype = request.session.get("captcha_type", "")

    if ctype == "image_click":
        import json as j
        try:
            ua = sorted(j.loads(user_answer))
            ca = sorted(j.loads(correct))
            ok = ua == ca
        except:
            ok = False
    else:
        ok = user_answer == correct

    if ok:
        request.session["captcha_verified"] = True
        request.session.pop("captcha_answer", None)
    return JsonResponse({"success": ok})
