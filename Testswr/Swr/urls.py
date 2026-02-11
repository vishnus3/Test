from django.urls import path
from .views import EmployeeListCreateAPI, EmployeeDetailAPI

urlpatterns = [
    path("employees/", EmployeeListCreateAPI.as_view()),
    path("employees/<int:id>/", EmployeeDetailAPI.as_view()),
]