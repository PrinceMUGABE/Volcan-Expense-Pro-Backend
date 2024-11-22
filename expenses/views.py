from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Expense
from .serializers import ExpenseSerializer
from rest_framework.permissions import IsAuthenticated


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Expense

class CreateExpenseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Extract data manually from request
        category = request.data.get('category')
        amount = request.data.get('amount')
        receipt = request.FILES.get('receipt')
        video = request.FILES.get('video')
        description = request.data.get('description', '')
        date = request.data.get('date')
        status_value = request.data.get('status', 'pending')

        # Validate the required fields
        if not category or not amount or not date:
            return Response(
                {"error": "Category, amount, and date are required fields."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check category validity
        valid_categories = [choice[0] for choice in Expense.CATEGORY_CHOICES]
        if category not in valid_categories:
            return Response(
                {"error": f"Invalid category. Valid options are: {', '.join(valid_categories)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check status validity
        valid_statuses = [choice[0] for choice in Expense.STATUS_CHOICES]
        if status_value not in valid_statuses:
            return Response(
                {"error": f"Invalid status. Valid options are: {', '.join(valid_statuses)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check for duplicates
        if Expense.objects.filter(user=request.user, category=category, amount=amount, date=date).exists():
            return Response(
                {"error": "An expense with the same category, amount, and date already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create the expense
        expense = Expense.objects.create(
            user=request.user,
            category=category,
            amount=amount,
            receipt=receipt,
            video=video,
            description=description,
            date=date,
            status=status_value
        )

        # Prepare a response
        response_data = {
            "id": expense.id,
            "user": {
                "id": expense.user.id,
                "phone_number": expense.user.phone_number,
                "email": expense.user.email,
                "role": expense.user.role,
                "created_by": expense.user.created_by__phone_number,
                "created_at": expense.user.created_at,
            },
            "category": expense.category,
            "amount": str(expense.amount),
            "receipt": expense.receipt.url if expense.receipt else None,
            "video": expense.video.url if expense.video else None,
            "description": expense.description,
            "date": expense.date,
            "status": expense.status,
            "created_at": expense.created_at,
        }

        return Response(response_data, status=status.HTTP_201_CREATED)




class GetAllExpensesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            expenses = Expense.objects.all().order_by('-created_at')
            serializer = ExpenseSerializer(expenses, many=True)

            return Response({
                'message': 'Expenses retrieved successfully',
                'expenses': serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error retrieving expenses: {str(e)}")
            return Response({
                'message': 'Error retrieving expenses',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)          
            


class GetExpenseByIdView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, expense_id):
        try:
            expense = Expense.objects.get(id=expense_id)
            serializer = ExpenseSerializer(expense)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Expense.DoesNotExist:
            return Response({'error': 'Expense not found'}, status=status.HTTP_404_NOT_FOUND)




class GetExpensesByCategoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, category):
        expenses = Expense.objects.filter(category=category)
        serializer = ExpenseSerializer(expenses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)






class GetExpensesByStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, status_value):
        expenses = Expense.objects.filter(status=status_value)
        serializer = ExpenseSerializer(expenses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)





class GetExpensesByLoggedInUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        expenses = Expense.objects.filter(user=request.user)
        serializer = ExpenseSerializer(expenses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)





class UpdateExpenseView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, expense_id):
        try:
            expense = Expense.objects.get(id=expense_id)
            if expense.user != request.user:
                return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
            serializer = ExpenseSerializer(expense, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Expense.DoesNotExist:
            return Response({'error': 'Expense not found'}, status=status.HTTP_404_NOT_FOUND)






class DeleteExpenseView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, expense_id):
        try:
            expense = Expense.objects.get(id=expense_id)
            if expense.user != request.user:
                return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
            expense.delete()
            return Response({'message': 'Expense deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Expense.DoesNotExist:
            return Response({'error': 'Expense not found'}, status=status.HTTP_404_NOT_FOUND)







