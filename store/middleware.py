class EnsureSessionMiddleware:
    # makes sure every request has a session key, even ones that don't render
    # a template (the cart_summary context processor already covers template
    # requests). cart merging itself happens in views.py on login/register.

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.session.session_key:
            request.session.create()
        return self.get_response(request)
