from django.utils import timezone
from .models import PageView
from .utils import get_client_ip

def track_page_view(request):
    ip = get_client_ip(request)
    path = request.path
    today = timezone.now().date()

    PageView.objects.get_or_create(
        path=path,
        ip_address=ip,
        date=today
    )
