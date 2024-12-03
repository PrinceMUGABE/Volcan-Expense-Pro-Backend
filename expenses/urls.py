from django.urls import path
from .views import (
    CreateExpenseView, GetAllExpensesView, GetExpenseByIdView,
    GetExpensesByCategoryView, GetExpensesByStatusView, 
    GetExpensesByLoggedInUserView, UpdateExpenseView, DeleteExpenseView, AcceptExpenseView,
    RejectExpenseView, MarkExpenseAsPaidView,ManagerGetExpensesView
)

urlpatterns = [
    path('create/', CreateExpenseView.as_view(), name='create-expense'),
    path('expenses/', GetAllExpensesView.as_view(), name='get-all-expenses'),
    path('<int:expense_id>/', GetExpenseByIdView.as_view(), name='get-expense-by-id'),
    path('category/<str:category>/', GetExpensesByCategoryView.as_view(), name='get-expenses-by-category'),
    path('status/<str:status_value>/', GetExpensesByStatusView.as_view(), name='get-expenses-by-status'),
    path('user/', GetExpensesByLoggedInUserView.as_view(), name='get-expenses-by-user'),
    path('update/<int:expense_id>/', UpdateExpenseView.as_view(), name='update-expense'),
    path('delete/<int:expense_id>/', DeleteExpenseView.as_view(), name='delete-expense'),
    path('accept/<int:expense_id>/', AcceptExpenseView.as_view(), name='accept-expense'),
    path('reject/<int:expense_id>/', RejectExpenseView.as_view(), name='reject-expense'),
    path('mark-paid/<int:expense_id>/', MarkExpenseAsPaidView.as_view(), name='mark_expense_as_paid'),
    path('manager/', ManagerGetExpensesView.as_view(), name='manager_get-all-expenses'),
]
