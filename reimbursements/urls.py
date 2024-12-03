# urls.py
from django.urls import path
from . import views
from .views import (
    ReimbursementListView, 
    ReimbursementDetailView,
    UserReimbursementListView,
    ReimbursementDeleteView,
    ReimbursementPaidView,
    ManagerGetReimbursementView) 

urlpatterns = [
    path('reimbursements-check/', views.trigger_reimbursement_checks, name='trigger-reimbursement-checks'),
    path('reimbursements/', ReimbursementListView.as_view(), name='reimbursement-list'),
    path('<int:pk>/', ReimbursementDetailView.as_view(), name='reimbursement-detail'),
    path('user/', UserReimbursementListView.as_view(), name='user-reimbursement-list'),
    path('delete/<int:pk>/', ReimbursementDeleteView.as_view(), name='reimbursement-delete'),
    path('paid/<int:reimbursement_id>/', ReimbursementPaidView.as_view(), name='reimbursement-paid'),
    path('manager/', ManagerGetReimbursementView.as_view(), name='manager_reimbursement-list'),
]