from django.urls import path

from .views import (
    obtain_password_token, password_reset_confirm, password_reset_change
)

urlpatterns = [
    path('password/reset', obtain_password_token, name='password_reset'),
    path('password/reset/confirm', password_reset_confirm, name='password_reset_confirm'),
    path('password/change', password_reset_change, name='password_reset_change'),
]
