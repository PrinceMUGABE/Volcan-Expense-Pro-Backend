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

class CreateExpenseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        category = request.data.get('category')
        receipt = request.FILES.get('receipt')
        video = request.FILES.get('video')
        date = ''
        amount = ''
        status_value = 'pending'

        # Validate required fields
        if not receipt:
            return Response({"error": "Receipt is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not category:
            return Response({"error": "Expense category is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not video:
            return Response({"error": "Video is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Save the file
        receipt_path = os.path.join(settings.MEDIA_ROOT, 'receipts')
        os.makedirs(receipt_path, exist_ok=True)

        receipt_full_path = os.path.join(receipt_path, receipt.name)
        with open(receipt_full_path, 'wb+') as destination:
            for chunk in receipt.chunks():
                destination.write(chunk)

        # Process the file to extract text
        try:
            extracted_text = self.extract_text_from_file(receipt_full_path)
            print(f"Extracted Text: {extracted_text}")  # Log the extracted text for debugging

            # Extract date and amount
            extracted_date, extracted_amount = self.extract_date_and_amount(extracted_text)

            # Validate extracted values
            if not extracted_date:
                return Response(
                    {"error": "Failed to extract a valid date from the receipt."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if not extracted_amount:
                return Response(
                    {"error": "Failed to extract a valid amount from the receipt."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Log extracted date and amount for debugging
            print(f"Extracted Date: {extracted_date}")
            print(f"Extracted Amount: {extracted_amount}")

            # Override with extracted values if available
            date = extracted_date
            amount = extracted_amount

        except Exception as e:
            return Response({"error": f"Failed to process the receipt: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        # Create the expense record
        expense = Expense.objects.create(
            user=request.user,
            category=category,
            amount=amount,
            receipt=receipt,
            video=video,
            date=date,
            status=status_value,
        )

        # Prepare response data
        response_data = {
            "id": expense.id,
            "category": expense.category,
            "amount": str(expense.amount),
            "receipt": expense.receipt.url,
            "video": expense.video.url if expense.video else None,
            "date": expense.date,
            "status": expense.status,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)

    def extract_text_from_file(self, file_path):
    
        
        # Set the path to Tesseract-OCR executable
        pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

        # Check if file is a PDF or an image
        if file_path.lower().endswith('.pdf'):
            text = ''
            poppler_path = r'C:\Program Files\poppler-24.08.0\Library\bin'  # Update this path
            pages = convert_from_path(file_path, poppler_path=poppler_path)
            for page in pages:
                text += pytesseract.image_to_string(page)
            return text
        elif file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            return pytesseract.image_to_string(Image.open(file_path))
        else:
            raise ValueError("Unsupported file type. Only images and PDFs are allowed.")


    
    def extract_date_and_amount(self, text):
        # Define keywords for amounts and dates
        amount_keywords = [
            "Total", "Amount", "Grand Total", "Balance Due", "Payable Amount",
            "Due Amount", "Net Payable", "Total Amount Due", "Total Payable",
            "Amount Paid", "Sum", "Subtotal", "Charge", "TOTAL AMOUNT", "Paid", 
            "Total net price", "Total Gross", "Total Price", "Total gross price", "Balance"
        ]
        date_keywords = [
            "Date", "Issued On", "Receipt Date", "Invoice Date", "Transaction Date",
            "Billing Date", "Order Date", "Dated", "Due Date", "Issued Date"
        ]

        # Enhanced patterns for amount and date
        amount_pattern = (
            r'(\b(?:' + '|'.join(re.escape(kw) for kw in amount_keywords) + r')\b)'
            r'\s*[:\-]?\s*([$€£]?[\d,.]+(?:\s?(USD|EUR|GBP|RWF)?)?)'
        )
        date_pattern = (
            r'(\b(?:' + '|'.join(re.escape(kw) for kw in date_keywords) + r')\b)'
            r'\s*[:\-]?\s*(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})'
        )

        # Extract date
        date_match = re.search(date_pattern, text, re.IGNORECASE)
        extracted_date = date_match.group(2) if date_match else None

        # Extract amounts and clean them
        amounts = []
        for match in re.finditer(amount_pattern, text, re.IGNORECASE):
            raw_amount = match.group(2)
            cleaned_amount = re.sub(r'[^\d.]', '', raw_amount)  # Remove non-numeric characters except '.'
            if cleaned_amount:
                try:
                    amounts.append(float(cleaned_amount))
                except ValueError:
                    continue

        # Use the largest amount as the most likely one (if multiple found)
        extracted_amount = max(amounts) if amounts else None

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







