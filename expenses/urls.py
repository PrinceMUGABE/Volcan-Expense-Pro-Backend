from django.urls import path
from .views import (
    CreateExpenseView, GetAllExpensesView, GetExpenseByIdView,
    GetExpensesByCategoryView, GetExpensesByStatusView, 
    GetExpensesByLoggedInUserView, UpdateExpenseView, DeleteExpenseView
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
]
