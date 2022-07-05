from django.conf.urls import url
from .views import AccountView, SignView
from django.urls import path

urlpatterns = [
    path('',AccountView.as_view()),
    path('sign-up',AccountView.as_view()),
    path('sign-in',SignView.as_view()),
]