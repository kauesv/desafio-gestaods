from django.contrib import admin
from django.urls import path, include
from core.views_autocomplete import StateAutocompleteView, CityAutocompleteView
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = "Aluguel de Carros LTDA."
admin.site.site_title = "Aluguel de Carros LTDA."

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('v1/', include('car_rental.routers.v1')),

    #admin
    path('admin/', admin.site.urls),

    #Aucomplete
    path(
        'estados-autocomplete/',
        StateAutocompleteView.as_view(),
        name='estados-autocomplete',
    ),
    path(
        'municipios-autocomplete/',
        CityAutocompleteView.as_view(),
        name='municipios-autocomplete',
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)