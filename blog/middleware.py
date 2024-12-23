class CurrentURLMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.current_url_name = request.resolver_match.url_name if request.resolver_match else None
        return self.get_response(request)