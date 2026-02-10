import time
from django.shortcuts import redirect
from django.conf import settings

class SessionTimeoutMiddleware:
    """
    Middleware para cerrar sesión tras X segundos de inactividad.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        timeout = getattr(settings, "SESSION_IDLE_TIMEOUT", None)

        if request.user.is_authenticated and timeout:

            last_activity = request.session.get("last_activity")

            current_time = time.time()

            # Si hay inactividad mayor al tiempo permitido → logout
            if last_activity and (current_time - last_activity > timeout):
                for key in list(request.session.keys()):
                    del request.session[key]
                return redirect(settings.SESSION_IDLE_TIMEOUT_REDIRECT)

            # Actualizar timestamp
            request.session["last_activity"] = current_time

        response = self.get_response(request)
        return response
