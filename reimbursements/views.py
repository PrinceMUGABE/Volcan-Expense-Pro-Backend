# reimbursements/views.py
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.timezone import now
from .models import Reimbursement
from django.db import transaction
from datetime import timedelta

@require_http_methods(["GET"])
def trigger_reimbursement_checks(request):
    try:
        with transaction.atomic():
            # Get reimbursements that haven't been notified in the last 24 hours
            reimbursements = Reimbursement.objects.filter(
                is_paid=False,
                last_notification_sent__isnull=True
            ) | Reimbursement.objects.filter(
                is_paid=False,
                last_notification_sent__lt=now() - timedelta(days=1)
            )

            notification_count = 0
            for reimbursement in reimbursements:
                # Only send notifications during 6 AM hour
                current_time = now().time()
                if current_time.hour >= 0 and current_time.hour <=6:
                    reimbursement.check_and_notify()
                    notification_count += 1

            return JsonResponse({
                "status": "success",
                "message": f"Processed {notification_count} reimbursements",
                "timestamp": now().isoformat()
            })
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)
        
        
        
        
        
        
        
        
        
        







from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Reimbursement
from .serializers import ReimbursementSerializer
from rest_framework.generics import ListAPIView, RetrieveAPIView, DestroyAPIView

class ReimbursementListView(ListAPIView):
    """
    Retrieve all reimbursements.
    """
    queryset = Reimbursement.objects.all()
    serializer_class = ReimbursementSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Optionally, add additional filters based on query parameters or logged-in user
        return self.list(request, *args, **kwargs)
    
    
    

class ReimbursementDetailView(RetrieveAPIView):
    """
    Retrieve a reimbursement by its ID.
    """
    queryset = Reimbursement.objects.all()
    serializer_class = ReimbursementSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    
    
    
from rest_framework.exceptions import PermissionDenied  
import logging
logger = logging.getLogger(__name__)



class UserReimbursementListView(ListAPIView):
    
    
    """
    Retrieve all reimbursements related to the logged-in user (based on the associated expense).
    """
    serializer_class = ReimbursementSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        print(f"User: {self.request.user}, Role: {self.request.user.role}")
        # logger.info(f"Expenses found: {Expense.objects.filter(user=self.request.user).count()}")
        # Check if the user is a driver, otherwise deny access
        if self.request.user.role != 'driver':
            raise PermissionDenied("You are not authorized to view this resource.")

        # Fetch reimbursements for the current driver's expenses
        user_expenses = Expense.objects.filter(user=self.request.user)
        
        print(f'\n\n Found Expenses: {user_expenses}\n\n')
        
        return Reimbursement.objects.filter(expense__in=user_expenses)   
    
    

class ReimbursementDeleteView(DestroyAPIView):
    """
    Delete a reimbursement (accessible only to admins or the user who created it).
    """
    queryset = Reimbursement.objects.all()
    serializer_class = ReimbursementSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        reimbursement = self.get_object()
        # Allow deletion only if the logged-in user is an admin or the one who created the expense
        if not request.user.is_staff and reimbursement.expense.user != request.user:
            return Response(
                {'error': 'Unauthorized. Only admins or the expense owner can delete reimbursements.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return self.destroy(request, *args, **kwargs)









from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Reimbursement
from rest_framework.decorators import action
from .serializers import ReimbursementSerializer
from userApp.models import CustomUser
from expenses.models import Expense
from django.db import models
from expenses.serializers import ExpenseSerializer

class ReimbursementPaidView(APIView):
    """
    Mark a reimbursement as paid and update the associated expense status to 'paid'.
    """
    permission_classes = [IsAuthenticated]

    def put(self, request, reimbursement_id):
        try:
            # Fetch the reimbursement
            reimbursement = Reimbursement.objects.get(id=reimbursement_id)

            # Only allow admin or the user who created the expense to mark the reimbursement as paid
            if not request.user.is_staff and reimbursement.expense.user != request.user:
                return Response(
                    {'error': 'Unauthorized. Only admins or the expense owner can mark the reimbursement as paid.'},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Mark the reimbursement as paid
            reimbursement.is_paid = True
            reimbursement.save()

            return Response(
                {'message': 'Reimbursement marked as paid successfully.', 'paid_at': reimbursement.paid_at},
                status=status.HTTP_200_OK
            )

        except Reimbursement.DoesNotExist:
            return Response({'error': 'Reimbursement not found.'}, status=status.HTTP_404_NOT_FOUND)



# from rest_framework.generics import ListAPIView
# from rest_framework.permissions import IsAuthenticated
# from .models import Reimbursement, Expense, CustomUser
# from .serializers import ReimbursementSerializer
from django.db.models import Q


# class ManagerGetReimbursementView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         # Ensure that only managers can access this view
#         if request.user.role != 'manager':
#             return Response({"error": "You are not authorized to view this resource."}, status=403)

#         # Get drivers created by the manager
#         drivers_created_by_manager = CustomUser.objects.filter(created_by=request.user)

#         # Get expenses created by drivers and by the manager themselves
#         expenses = Expense.objects.filter(
#             models.Q(user__in=drivers_created_by_manager) | models.Q(user=request.user)
#         )
        
#         # Use __in to filter reimbursements for the list of expenses
#         reimbursement = Reimbursement.objects.filter(expense__in=expenses)

#         # Serialize the reimbursements data
#         serializer = ReimbursementSerializer(reimbursement, many=True)
        
        
#         print(f'\nFound Reimbursements: {serializer.data}\n\n')
        
#         # Return the response with serialized reimbursement data
#         return Response({"reimbursements": serializer.data}, status=200)
    
   
class ManagerGetReimbursementView(ListAPIView):
    """
    Retrieve all reimbursements for a manager:
    - Reimbursements for the drivers they manage.
    - Reimbursements directly created by the manager.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ReimbursementSerializer

    def get_queryset(self):
        # Ensure that only managers can access this view
        if self.request.user.role != 'manager':
            return Response({"error": "You are not authorized to view this resource."}, status=403)

        # Get drivers created by the manager
        drivers_created_by_manager = CustomUser.objects.filter(created_by=self.request.user)

        # Get expenses created by drivers and by the manager themselves
        expenses = Expense.objects.filter(
            Q(user__in=drivers_created_by_manager) | Q(user=self.request.user)
        )

        # Return the reimbursements for the filtered expenses
        return Reimbursement.objects.filter(expense__in=expenses) 
    
    
    
    
