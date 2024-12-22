from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Expense
from .serializers import ExpenseSerializer
from rest_framework.permissions import IsAuthenticated
from pdf2image import convert_from_path


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Expense

import pytesseract
from PIL import Image
import os
from django.conf import settings

import pytesseract
from PIL import Image
import os
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status


from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import os
import re
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from pytesseract import pytesseract
from userApp.models import CustomUser
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from datetime import datetime
import os
from django.conf import settings
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import re





class CreateExpenseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        category = request.data.get('category')
        receipt = request.FILES.get('receipt')
        video = request.FILES.get('video')
        submitted_date = request.data.get('date')
        submitted_amount = request.data.get('amount')
        
        user = request.user
        # Set status based on user role
        status_value = 'approved' if user.role in ['admin', 'manager'] else 'pending'

        # Validate common required fields
        if not category:
            return Response({"error": "Expense category is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not submitted_date:
            return Response({"error": "Date is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not submitted_amount:
            return Response({"error": "Amount is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            submitted_amount = float(submitted_amount)
        except ValueError:
            return Response({"error": "Invalid amount format."}, status=status.HTTP_400_BAD_REQUEST)

        # Role-based validation for receipt and video
        if user.role not in ['admin', 'manager']:
            if not video or not receipt:
                return Response({
                    "error": "Both video and receipt are required for non-admin/manager users."
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Process receipt only if it's provided
            if receipt:
                receipt_path = os.path.join(settings.MEDIA_ROOT, 'receipts')
                os.makedirs(receipt_path, exist_ok=True)
                receipt_full_path = os.path.join(receipt_path, receipt.name)
                
                with open(receipt_full_path, 'wb+') as destination:
                    for chunk in receipt.chunks():
                        destination.write(chunk)

                try:
                    extracted_text = self.extract_text_from_file(receipt_full_path)
                    extracted_date, extracted_amount = self.extract_date_and_amount(extracted_text)

                    if not extracted_date or not extracted_amount:
                        return Response({
                            "error": "Failed to extract valid date or amount from the receipt."
                        }, status=status.HTTP_400_BAD_REQUEST)

                    # Date validation
                    try:
                        if '-' in extracted_date:
                            extracted_date_obj = datetime.strptime(extracted_date, '%Y-%m-%d')
                        elif '/' in extracted_date:
                            extracted_date_obj = datetime.strptime(extracted_date, '%d/%m/%Y')
                        
                        submitted_date_obj = datetime.strptime(submitted_date, '%Y-%m-%d')

                        if extracted_date_obj.date() != submitted_date_obj.date():
                            return Response({
                                "error": "Submitted date does not match the date on the receipt.",
                                "submitted_date": submitted_date,
                                "receipt_date": extracted_date
                            }, status=status.HTTP_400_BAD_REQUEST)

                    except ValueError as e:
                        return Response({
                            "error": f"Error processing dates: {str(e)}"
                        }, status=status.HTTP_400_BAD_REQUEST)

                    # Amount validation
                    tolerance = 0.01
                    if abs(extracted_amount - submitted_amount) > tolerance:
                        return Response({
                            "error": "Submitted amount does not match the amount on the receipt.",
                            "submitted_amount": submitted_amount,
                            "receipt_amount": extracted_amount
                        }, status=status.HTTP_400_BAD_REQUEST)

                except Exception as e:
                    return Response({
                        "error": f"Failed to process the receipt: {str(e)}"
                    }, status=status.HTTP_400_BAD_REQUEST)

        # Create expense record
        try:
            expense = Expense.objects.create(
                user=user,
                category=category,
                amount=submitted_amount,
                receipt=receipt,
                video=video,
                date=submitted_date,
                status=status_value,  # Using the role-based status
            )

            response_data = {
                "id": expense.id,
                "category": expense.category,
                "amount": str(expense.amount),
                "receipt": expense.receipt.url if expense.receipt else None,
                "video": expense.video.url if expense.video else None,
                "date": expense.date,
                "reimbursement_status": expense.reimbursement_status,
                "status": expense.status,
            }
            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                "error": f"Failed to create expense record: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)



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
        # Ensure that only drivers can access this view
        if request.user.role != 'driver':
            return Response({"error": "You are not authorized to view this resource."}, status=403)

        try:
            # Fetch expenses for the logged-in user (driver)
            expenses = Expense.objects.filter(user=request.user)

            # Serialize the expenses data
            serializer = ExpenseSerializer(expenses, many=True)

            return Response({"expenses": serializer.data}, status=200)

        except ObjectDoesNotExist:
            return Response({"error": "No expenses found for this user."}, status=404)




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






from reimbursements.models import Reimbursement

class AcceptExpenseView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, expense_id):
        try:
            # Fetch the expense
            expense = Expense.objects.get(id=expense_id)

            # Only allow authorized users to update the status (e.g., admin or expense owner)
            if not request.user.is_staff and expense.user != request.user:
                return Response(
                    {'error': 'Unauthorized. Only admins or the expense owner can accept expenses.'},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Update the status to 'approved'
            expense.status = 'approved'
            expense.save()

            # Automatically create a Reimbursement instance for this approved expense
            Reimbursement.objects.create(expense=expense)

            return Response(
                {'message': 'Expense approved successfully and reimbursement created.', 'status': expense.status},
                status=status.HTTP_200_OK
            )
        except Expense.DoesNotExist:
            return Response({'error': 'Expense not found.'}, status=status.HTTP_404_NOT_FOUND)




class RejectExpenseView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, expense_id):
        try:
            # Fetch the expense
            expense = Expense.objects.get(id=expense_id)

            # Only allow authorized users to update the status (e.g., admin or expense owner)
            if not request.user.is_staff and expense.user != request.user:
                return Response(
                    {'error': 'Unauthorized. Only admins or the expense owner can reject expenses.'},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Update the status to 'rejected'
            expense.status = 'rejected'
            expense.reimbursement_status = 'rejected'
            expense.save()

            return Response(
                {'message': 'Expense rejected successfully.', 'status': expense.status},
                status=status.HTTP_200_OK
            )
        except Expense.DoesNotExist:
            return Response({'error': 'Expense not found.'}, status=status.HTTP_404_NOT_FOUND)











from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Expense
from reimbursements.models import Reimbursement
from django.utils.timezone import now

# View to mark expense as paid
class MarkExpenseAsPaidView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, expense_id):
        try:
            # Fetch the expense
            expense = Expense.objects.get(id=expense_id)

            # Ensure the current user is authorized to mark the expense as paid
            if not request.user.is_staff and expense.user != request.user:
                return Response(
                    {'error': 'Unauthorized. Only admins or the expense owner can mark expenses as paid.'},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Update the expense status to 'paid'
            expense.status = 'approved'  # Ensure the expense is approved first before marking as paid
            expense.reimbursement_status = 'paid'  # Mark reimbursement status as paid
            expense.save()

            # Fetch the associated reimbursement model
            reimbursement = Reimbursement.objects.get(expense=expense)

            # Mark reimbursement as paid and set the paid date
            reimbursement.is_paid = True
            reimbursement.paid_at = now()  # Set the current time as the paid date
            reimbursement.save()  # Save the reimbursement model

            # Return a response confirming the change
            return Response(
                {'message': 'Expense marked as paid successfully.'},
                status=status.HTTP_200_OK
            )

        except Expense.DoesNotExist:
            return Response({'error': 'Expense not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Reimbursement.DoesNotExist:
            return Response({'error': 'Reimbursement not found for this expense.'}, status=status.HTTP_404_NOT_FOUND)






# View to get reimbursement status for a specific expense
class GetReimbursementStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, expense_id):
        try:
            expense = Expense.objects.get(id=expense_id)
            reimbursement = Reimbursement.objects.get(expense=expense)

            return Response({
                'expense_id': expense.id,
                'is_paid': reimbursement.is_paid,
                'paid_at': reimbursement.paid_at,
            }, status=status.HTTP_200_OK)

        except Expense.DoesNotExist:
            return Response({'error': 'Expense not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Reimbursement.DoesNotExist:
            return Response({'error': 'Reimbursement not found for this expense.'}, status=status.HTTP_404_NOT_FOUND)



from django.db import models
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Expense
from userApp.models import CustomUser
from expenses.serializers import ExpenseSerializer


# View to for a manager to get expenses for the driver users he has created
class ManagerGetExpensesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Ensure that only users with the 'manager' role can access this view
        if request.user.role != 'manager':
            return Response({"error": "You are not authorized to view this resource."}, status=403)

        # Fetch drivers created by the manager
        drivers_created_by_manager = CustomUser.objects.filter(created_by=request.user)

        # Fetch expenses:
        # - Expenses submitted by drivers under this manager
        # - Expenses directly created by the manager
        expenses = Expense.objects.filter(models.Q(user__in=drivers_created_by_manager) | models.Q(user=request.user))

        # Serialize the expenses data
        serializer = ExpenseSerializer(expenses, many=True)
        
        return Response({"expenses": serializer.data}, status=200)



