from django.urls import path
from . import views

urlpatterns = [
    path('policies/', views.get_all_policies, name='get_all_policies'),
    path('user/', views.get_policies_by_user, name='get_policies_by_user'),
    path('<int:policy_id>/', views.get_policy_by_id, name='get_policy_by_id'),
    path('create/', views.create_policy, name='create_policy'),
    path('update/<int:policy_id>/', views.update_policy, name='update_policy'),
    path('delete/<int:policy_id>/', views.delete_policy, name='delete_policy'),
]
