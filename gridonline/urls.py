from django.contrib import admin
from django.urls import path, include


from loadfile.views import show_uploads_page, show_about_page, calc_xy


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', show_uploads_page, name='upload'),  
    path('about/', show_about_page, name='about'),
    path('calc_xy/', calc_xy)
]
