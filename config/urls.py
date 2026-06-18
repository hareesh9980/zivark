from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/',     admin.site.urls),
    path('accounts/',  include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('clients/',   include('clients.urls')),
    path('materials/', include('materials.urls')),
    path('rfq/',       include('rfq.urls')),
    path('',           RedirectView.as_view(url='/dashboard/', permanent=False)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)