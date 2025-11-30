from django.utils.deprecation import MiddlewareMixin

class DisableCSRFForAPIMiddleware(MiddlewareMixin):
    """
    Disable CSRF checks for API endpoints since we use JWT authentication.
    CSRF protection is not needed when using JWT in Authorization headers.
    """
    def process_request(self, request):
        if request.path.startswith('/api/'):
            setattr(request, '_dont_enforce_csrf_checks', True)
        return None
