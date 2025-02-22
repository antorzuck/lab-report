
from django.contrib import admin
from django.urls import path
from report import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.generate_lab_report_pdf),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


admin.site.site_header = "Reportlab Admin"
admin.site.site_title = "Reportlab Admin Portal"
admin.site.index_title = "Welcome to Reportlab Head Quarter"