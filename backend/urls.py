from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static  # Import for serving static and media files in development

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('userApp.urls')),
    path('expense/', include('expenses.urls')),
    path('reimbursement/', include('reimbursements.urls')),
    path('policy/', include('policies.urls')),
]

# Add media file serving during development
if settings.DEBUG:  # Serve media files only in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
