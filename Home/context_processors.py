from django.conf import settings

def analytics(request):
    return {"GA_MEASUREMENT_ID": getattr(settings, "GA_MEASUREMENT_ID", "")}

from .forms import SubscribeForm

def subscribe_form(request):
    return {
        "subscribe_form": SubscribeForm()
    }
