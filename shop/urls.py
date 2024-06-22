from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from store.views import index, stripe_webhook

from shop import settings
"""""""""
..._user pour différencier des fonctions Django
"""""""""
urlpatterns = [
    path('', index, name='index'),
    path('admin/', admin.site.urls),
    path('stripe-webhook/', stripe_webhook, name="stripe-webhook"),
    path('account/', include('accounts.urls')),
    path('boutique/', include('store.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + \
              static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)



# def trigger_error(request):
#     division_by_zero = 1 / 0
#
# urlpatterns = [
#     path('sentry-debug/', trigger_error),
#     # ...
# ]