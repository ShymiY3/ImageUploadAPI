from django.http import HttpResponseForbidden

class MediaAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.user.is_staff:
            return self.get_response(request)
        
        if request.path.startswith('/media/'):
            return HttpResponseForbidden("Access denied to media files.")

        return self.get_response(request)
