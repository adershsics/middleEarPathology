# doctor/urls.py
from django.urls import path
from .views import doctor_list_create_view,login_api_view,view_doctors,delete_doctor

urlpatterns = [
    path('signup', doctor_list_create_view, name='doctor-list-create'),
    path('login', login_api_view, name='api-login'),
    path('view-all-doctors',view_doctors,name='view-all-doctors'),
    path('doctors/<int:doctor_id>', delete_doctor, name='delete_doctor'),
]
