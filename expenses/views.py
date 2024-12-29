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
    
    def parse_date(self, date_str):
        """
        Parse date string into datetime object, handling multiple formats.
        
        Args:
            date_str (str): Date string in various possible formats
            
        Returns:
            datetime: Parsed datetime object or None if parsing fails
        """
        date_formats = [
            '%Y-%m-%d',      # YYYY-MM-DD
            '%d/%m/%Y',      # DD/MM/YYYY
            '%m/%d/%Y',      # MM/DD/YYYY
            '%d-%m-%Y',      # DD-MM-YYYY
            '%d.%m.%Y',      # DD.MM.YYYY
            '%d %B %Y',      # DD Month YYYY
            '%d %b %Y',      # DD Mon YYYY
            '%B %d %Y',      # Month DD YYYY
            '%b %d %Y',      # Mon DD YYYY
            '%d/%m/%y',      # DD/MM/YY
            '%m/%d/%y',      # MM/DD/YY
        ]
        
        # Clean the date string
        date_str = date_str.strip()
        
        # Try each format
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        return None
    
    def extract_text_from_file(self, file_path):
        """
        Extract text from PDF or image files using pytesseract OCR.
        """
        try:
            if file_path.lower().endswith('.pdf'):
                images = convert_from_path(file_path)
                image = images[0]
            else:
                image = Image.open(file_path)
            
            extracted_text = pytesseract.image_to_string(image)
            return extracted_text

        except Exception as e:
            raise Exception(f"Error extracting text from file: {str(e)}")

    def extract_date_and_amount(self, text):
        """
        Extract date and amount from receipt text with enhanced pattern matching.
        
        Args:
            text (str): Text extracted from receipt
        
        Returns:
            tuple: (date_str, amount_float) - Extracted date and amount
        """
        # Date-related keywords that might precede dates
        date_keywords = r"(?:Date|DATE|Transaction Date|Trans Date|Purchase Date|Receipt Date|Order Date|Invoice Date|Bill Date|Service Date|Payment Date|Posted|Processed|Created|Issued|Printed)"
        
        # Common date patterns with optional keywords
        date_patterns = [
            # With keywords
            f"{date_keywords}:?\\s*" + r"(\d{4}-\d{2}-\d{2})",  # YYYY-MM-DD
            f"{date_keywords}:?\\s*" + r"(\d{2}/\d{2}/\d{4})",  # DD/MM/YYYY
            f"{date_keywords}:?\\s*" + r"(\d{2}-\d{2}-\d{4})",  # DD-MM-YYYY
            f"{date_keywords}:?\\s*" + r"(\d{2}\.\d{2}\.\d{4})",  # DD.MM.YYYY
            f"{date_keywords}:?\\s*" + r"(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})",  # 15 January 2024
            f"{date_keywords}:?\\s*" + r"(\d{1,2}/\d{1,2}/\d{2})",  # DD/MM/YY
            
            # Without keywords (fallback)
            r"\b(\d{4}-\d{2}-\d{2})\b",  # YYYY-MM-DD
            r"\b(\d{2}/\d{2}/\d{4})\b",  # DD/MM/YYYY
            r"\b(\d{2}-\d{2}-\d{4})\b",  # DD-MM-YYYY
            r"\b(\d{2}\.\d{2}\.\d{4})\b",  # DD.MM.YYYY
            r"\b(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})\b",  # 15 January 2024
            r"\b(\d{1,2}/\d{1,2}/\d{2})\b",  # DD/MM/YY
        ]
        
        # Amount-related keywords and patterns
        amount_patterns = [
            # With currency symbols and keywords
            r"(?:Total|TOTAL|Sum|SUM|Amount|AMOUNT|Balance|BALANCE|Due|DUE|Charge|CHARGE|Price|PRICE|Payment|PAYMENT|Paid|PAID|Bill|BILL|Final|FINAL|Grand Total|GRAND TOTAL|Sub-?total|SUB-?TOTAL):?\s*[\$\€\£\¥]?\s*\d+[,.]\d{2}\b",
            
            # Tax-related amounts
            r"(?:Tax|TAX|VAT|GST|HST|Sales Tax|SALES TAX):?\s*[\$\€\£\¥]?\s*\d+[,.]\d{2}\b",
            
            # Due amounts
            r"(?:Amount Due|AMOUNT DUE|Total Due|TOTAL DUE|Balance Due|BALANCE DUE):?\s*[\$\€\£\¥]?\s*\d+[,.]\d{2}\b",
            
            # Payment-specific amounts
            r"(?:Card Payment|CARD PAYMENT|Cash Payment|CASH PAYMENT|Payment Amount|PAYMENT AMOUNT|TOTAL|Total):?\s*[\$\€\£\¥]?\s*\d+[,.]\d{2}\b",
            
            # Simple currency amounts (fallback)
            r"[\$\€\£\¥]\s*\d+[,.]\d{2}\b",
            r"\d+[,.]\d{2}\s*[\$\€\£\¥]",
            
            # Numbers at end of line (likely totals)
            r"\b\d+[,.]\d{2}\s*$",
            
            # Bold or emphasized amounts (common in OCR)
            r"\*\s*[\$\€\£\¥]?\s*\d+[,.]\d{2}\s*\*",
            
            # Specific receipt keywords
            r"(?:Receipt Total|RECEIPT TOTAL|Invoice Total|INVOICE TOTAL|Total|TOTAL):?\s*[\$\€\£\¥]?\s*\d+[,.]\d{2}\b",
        ]
        
        # Extract date
        extracted_date = None
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Take the first matched date
                extracted_date = matches[0]
                # If the match is a tuple (from a capturing group), take the captured part
                if isinstance(extracted_date, tuple):
                    extracted_date = extracted_date[0]
                break
        
        # Extract amount
        extracted_amount = None
        for pattern in amount_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Take the last matched amount (usually the total)
                amount_str = matches[-1]
                # Clean up the amount string
                amount_str = re.sub(r'[^\d.,]', '', amount_str)
                amount_str = amount_str.replace(',', '.')
                try:
                    extracted_amount = float(amount_str)
                    # Verify it's a reasonable amount (not zero or negative)
                    if extracted_amount > 0:
                        break
                except ValueError:
                    continue
        
        return extracted_date, extracted_amount
    
    
    def extract_vendor_from_receipt(self, text):
        """
        Extract the vendor name from the receipt text using pattern matching.
        
        Args:
            text (str): Text extracted from receipt

        Returns:
            str: Extracted vendor name (if found)
        """
        try:
            vendor_patterns = [
                # Explicit identifiers
                r"(?:Vendor Name|Merchant|Store|Sold by|Billed To|Retailer|From):?\s*(\w[\w\s&.,'-]*)",
                
                # Contextual identifiers
                r"(?:Management Consultant|Consultant|Service Provider):?\s*(\w[\w\s&.,'-]*)",
                
                # General name patterns near key terms
                r"(?:(?:Name|Account Name):)\s*(\w[\w\s&.,'-]*)",
                
                # Header-like patterns
                r"^(?:(\w[\w\s&.,'-]*)\s*(?:LLC|Ltd|Inc|Corp|Company|Consultant))",  # Header
                r"^\s*(\w[\w\s&.,'-]*)\s*(?:Management|Services|Financial|Consulting)",  # Business context
                
                # Business suffixes
                r"(\w[\w\s&.,'-]*\b(?:LLC|Ltd|Inc|Corp))"
            ]

            for pattern in vendor_patterns:
                # Check each pattern one by one
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    # Stop and return the first match found
                    return match.group(1).strip()

        except Exception as e:
            raise Exception(f"Error extracting vendor from receipt: {str(e)}")

        return None

    
    

    def post(self, request):
        category = request.data.get('category')
        receipt = request.FILES.get('receipt')
        video = request.FILES.get('video')
        submitted_date = request.data.get('date')
        submitted_amount = request.data.get('amount')
        submitted_vendor = request.data.get('vendor')
        
        print(f"vendor {submitted_vendor}\n\n")

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
            if not video or not receipt or not submitted_vendor:
                return Response({
                    "error": "All fields are required."
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
                    
                    print(f"Extracted text: {extracted_text}\n\n")
                    
                     # Other validations (date and amount)
                    extracted_date, extracted_amount = self.extract_date_and_amount(extracted_text)
                    
                    print(f"Extracted Amount: {extracted_amount}\n\n")
                    print(f"Extracted Date: {extracted_date}\n\n")

                    if not extracted_date or not extracted_amount:
                        return Response({
                            "error": "Failed to extract valid date or amount from the receipt."
                        }, status=status.HTTP_400_BAD_REQUEST)
                        
                    # Parse both dates
                    parsed_extracted_date = self.parse_date(extracted_date)
                    parsed_submitted_date = self.parse_date(submitted_date)
                    
                    if not parsed_extracted_date or not parsed_submitted_date:
                        return Response({
                            "error": "Invalid date format in receipt or submitted date."
                        }, status=status.HTTP_400_BAD_REQUEST)
                        
                    # Compare dates
                    if parsed_extracted_date != parsed_submitted_date:
                        return Response({
                            "error": "Submitted date does not match the date on receipt.",
                            "submitted_date": submitted_date,
                            "receipt_date": extracted_date
                        }, status=status.HTTP_400_BAD_REQUEST)


                    # [Date and amount validations omitted for brevity]
                    
                    if float(extracted_amount) != float(submitted_amount):
                         return Response({
                            "error": "Submitted amount does not match the amount on receipt."
                        }, status=status.HTTP_400_BAD_REQUEST)
                         
                    # if extracted_date.lower() != submitted_date.lower():
                    #      return Response({
                    #         "error": "The date does not match the date on the receipt."
                    #     }, status=status.HTTP_400_BAD_REQUEST)

                    # Extract and validate vendor
                    extracted_vendor = self.extract_vendor_from_receipt(extracted_text)
                    if not extracted_vendor:
                        return Response({
                            "error": "Failed to extract vendor from the receipt."
                        }, status=status.HTTP_400_BAD_REQUEST)

                    if extracted_vendor.lower() != submitted_vendor.lower():
                        
                        print(f"Submitted Vender: {submitted_vendor}\n\n")
                        print(f"Extracted Vendor: {extracted_vendor}\n\n")
                        return Response({
                            "error": "Submitted vendor does not match the vendor on the receipt.",
                            "submitted_vendor": submitted_vendor,
                            "receipt_vendor": extracted_vendor
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
                status=status_value,
                vendor=submitted_vendor,
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



def extract_text_from_file(self, file_path):
    """
    Extract text from PDF or image files using pytesseract OCR.
    
    Args:
        file_path (str): Path to the receipt file (PDF or image)
    
    Returns:
        str: Extracted text from the file
    """
    try:
        # Check if file is PDF based on extension
        if file_path.lower().endswith('.pdf'):
            # Convert PDF to images
            images = convert_from_path(file_path)
            # Process first page only - assuming receipt is single page
            image = images[0]
        else:
            # Open image file directly
            image = Image.open(file_path)
        
        # Extract text using pytesseract
        extracted_text = pytesseract.image_to_string(image)
        return extracted_text

    except Exception as e:
        raise Exception(f"Error extracting text from file: {str(e)}")

def extract_date_and_amount(self, text):
    """
    Extract date and amount from receipt text.
    
    Args:
        text (str): Text extracted from receipt
    
    Returns:
        tuple: (date_str, amount_float) - Extracted date and amount
    """
    # Common date patterns (can be expanded based on your needs)
    date_patterns = [
        r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
        r'\d{2}/\d{2}/\d{4}',  # DD/MM/YYYY
        r'\d{2}-\d{2}-\d{4}',  # DD-MM-YYYY
    ]
    
    # Amount patterns (can be expanded based on your needs)
    amount_patterns = [
        r'\$?\s*\d+[,.]\d{2}\b',  # $XX.XX or XX.XX
        r'\$?\s*\d+[,.]\d{2}\s*$',  # Amount at end of line
        r'Total:\s*\$?\s*\d+[,.]\d{2}',  # Total: $XX.XX
        r'Amount:\s*\$?\s*\d+[,.]\d{2}'  # Amount: $XX.XX
    ]
    
    # Extract date
    extracted_date = None
    for pattern in date_patterns:
        matches = re.findall(pattern, text)
        if matches:
            extracted_date = matches[0]  # Take the first matched date
            break
    
    # Extract amount
    extracted_amount = None
    for pattern in amount_patterns:
        matches = re.findall(pattern, text)
        if matches:
            # Clean up the amount string and convert to float
            amount_str = matches[-1]  # Take the last matched amount (usually the total)
            amount_str = re.sub(r'[^\d.,]', '', amount_str)  # Remove all non-numeric characters except . and ,
            amount_str = amount_str.replace(',', '.')  # Replace comma with dot for float conversion
            try:
                extracted_amount = float(amount_str)
                break
            except ValueError:
                continue
    
    return extracted_date, extracted_amount



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
            # if expense.user != request.user:
            #     return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
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
            # if expense.user != request.user:
            #     return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
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

            # # Only allow authorized users to update the status (e.g., admin or expense owner)
            # if not request.user.is_staff and expense.user != request.user:
            #     return Response(
            #         {'error': 'Unauthorized. Only admins or the expense owner can accept expenses.'},
            #         status=status.HTTP_403_FORBIDDEN
            #     )

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



