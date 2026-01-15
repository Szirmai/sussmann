from .services import track_page_view


class PageViewMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        path = request.path.lower()

        # Admin kizárása
        if path.startswith('/admin/'):
            return response

        # Statikus és média útvonalak kizárása
        if path.startswith(('/static/', '/media/', '/assets/', '/dashboard/', '/cart/', '/admin/', '/analytics/', '/.well-known/', '/success/')):
            return response

        # Fájlkiterjesztések kizárása
        IGNORED_EXTENSIONS = (
            '.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg',
            '.css', '.js', '.ico', '.woff', '.woff2'
        )

        if path.endswith(IGNORED_EXTENSIONS):
            return response

        # Csak GET kérések
        if request.method != 'GET':
            return response

        # Itt történik a mentés
        track_page_view(request)

        return response
