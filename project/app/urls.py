from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('create_ad/', views.create_ad, name='create_ad'),
    path('edit_ad/<int:ad_id>/', views.edit_ad, name='edit_ad'),
    path('ad/<int:ad_id>/', views.ad_detail, name='ad_detail'),
    path('profile/', views.profile, name='profile'),
    path('responses/', views.responses, name='responses'),
    path('response_detail/<int:response_id>/', views.response_detail, name='response_detail'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registration_confirmation/<int:user_id>/', views.registration_confirmation, name='registration_confirmation'),
]
