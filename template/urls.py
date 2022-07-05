from django.conf.urls import url
from .views import TemplateView, TemplateDetails, Terraform
from django.urls import path

urlpatterns = [
    path('*/', TemplateView.as_view(), name='template_CRD'),
    path('<id>/', TemplateDetails.as_view()),
    path('terraform/<id>/', Terraform.as_view()),
]
