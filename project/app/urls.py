from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('create_ad/', views.create_ad, name='create_ad'),
    path('edit_ad/<int:ad_id>/', views.edit_ad, name='edit_ad'),
    path('ad/<int:ad_id>/', views.ad_detail, name='ad_detail'),
    path('delete_ad/<int:ad_id>/', views.delete_ad, name='delete_ad'),
    path('profile/', views.profile, name='profile'),
    path('user_responses/', views.user_responses, name='user_responses'),
    path('send_response/<int:ad_id>/', views.send_response, name='send_response'),
    path('accept_response/<int:response_id>/', views.accept_response, name='accept_response'),
    path('delete_response/<int:response_id>/', views.delete_response, name='delete_response'),
    path('response_detail/<int:response_id>/', views.response_detail, name='response_detail'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registration_confirmation/<int:user_id>/', views.registration_confirmation, name='registration_confirmation'),
]

#маршруты URL для обслуживания медиафайлов только в режиме отладки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)