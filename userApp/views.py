from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.mail import send_mail
from django.db.utils import IntegrityError
from .models import CustomUser

@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Enforce authentication
def register_user(request):
    phone_number = request.data.get('phone')
    email = request.data.get('email')
    role = request.data.get('role')

    # Basic validations
    if not phone_number or not email or not role:
        return Response({"error": "Phone number, email, and role are required."}, status=400)

    if role not in ['driver', 'admin', 'manager']:
        return Response({"error": "Invalid role. Must be 'driver', 'admin', or 'manager'."}, status=400)

    # Check if the phone number or email already exists
    if CustomUser.objects.filter(phone_number=phone_number).exists():
        return Response({"error": "A user with this phone number already exists."}, status=400)
    if CustomUser.objects.filter(email=email).exists():
        return Response({"error": "A user with this email already exists."}, status=400)

    # Check the requesting user's role and permissions
    requesting_user = request.user
    if not hasattr(requesting_user, 'role'):
        return Response({"error": "User role is missing."}, status=403)

    if requesting_user.role == 'admin':
        allowed_roles = ['driver', 'manager', 'admin']
    elif requesting_user.role == 'manager':
        allowed_roles = ['driver']
    else:
        return Response({"error": "You do not have permission to create users."}, status=403)

    if role not in allowed_roles:
        return Response(
            {"error": f"As a {requesting_user.role}, you can only create users with roles: {', '.join(allowed_roles)}."},
            status=403,
        )

    try:
        # Generate a random password
        password = CustomUser.objects.make_random_password()

        # Create the user
        user = CustomUser.objects.create_user(
            phone_number=phone_number,
            email=email,
            role=role,
            password=password
        )

        # Set the "created_by" field to the logged-in user
        user.created_by = requesting_user
        user.save()

        # Send the password to the user's email
        send_mail(
            subject="Your Account Password",
            message=f"Hello, Your account has been created in Volcano ExpensePro. Your password is: {password}",
            from_email="no-reply@expensepro.com",
            recipient_list=[email],
        )

        return Response({"message": "User registered successfully. Check your email for the password."}, status=201)

    except IntegrityError:
        return Response({"error": "A user with this phone number or email already exists."}, status=400)




from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser

@api_view(['POST'])
def login_user(request):
    phone_number = request.data.get('phone')
    password = request.data.get('password')

    # Basic validations
    if not phone_number or not password:
        return Response({"error": "Phone number and password are required."}, status=400)

    # Authenticate the user
    user = authenticate(phone_number=phone_number, password=password)

    if user is None:
        return Response({"error": "Invalid phone number or password."}, status=401)

    # Generate JWT token
    refresh = RefreshToken.for_user(user)

    # Include user details in the response
    return Response({
        "id": user.id,
        "phone_number": user.phone_number,
        "email": user.email,
        "role": user.role,
        "created_at": user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        "token": {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        },
        "message": "Login successful."
    }, status=200)














import re
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.mail import send_mail
from .models import CustomUser

@api_view(['POST'])
def reset_password(request):
    phone_number = request.data.get('phone')
    new_password = request.data.get('new_password')

    # Basic validation
    if not phone_number:
        return Response({"error": "Phone number is required."}, status=400)

    if not new_password:
        return Response({"error": "New password is required."}, status=400)

    # Validate password strength
    if len(new_password) < 6:
        return Response({"error": "Password must be at least 6 characters long."}, status=400)
    if not re.search(r"[A-Z]", new_password):
        return Response({"error": "Password must contain at least one uppercase letter."}, status=400)
    if not re.search(r"[a-z]", new_password):
        return Response({"error": "Password must contain at least one lowercase letter."}, status=400)
    if not re.search(r"[0-9]", new_password):
        return Response({"error": "Password must contain at least one number."}, status=400)
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", new_password):
        return Response({"error": "Password must contain at least one special character."}, status=400)

    try:
        # Find the user
        user = CustomUser.objects.get(phone_number=phone_number)

        # Update the user's password
        user.set_password(new_password)
        user.save()

        # Send the new password to the user's email
        send_mail(
            subject="Your New Password",
            message=f"Your password has been reset. Your new password is: {new_password}",
            from_email="no-reply@expensepro.com",
            recipient_list=[user.email],
        )

        return Response({"message": "Password reset successfully. A confirmation has been sent to your email."}, status=200)

    except CustomUser.DoesNotExist:
        return Response({"error": "User with this phone number does not exist."}, status=404)






from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import CustomUser
from django.core.exceptions import ObjectDoesNotExist
from rest_framework_simplejwt.authentication import JWTAuthentication




# Delete a user by ID (admin only)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user_by_id(request, user_id):
    if request.user.role != 'admin':
        return Response({"error": "You are not authorized to delete users."}, status=403)
    
    try:
        user = CustomUser.objects.get(id=user_id)
        user.delete()
        return Response({"message": "User deleted successfully."}, status=200)
    except ObjectDoesNotExist:
        return Response({"error": "User with the given ID does not exist."}, status=404)





from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from .models import CustomUser

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from .models import CustomUser

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user(request, user_id):
    phone_number = request.data.get('phone_number')
    email = request.data.get('email')
    role = request.data.get('role')

    # Validate required fields
    if not phone_number or not email or not role:
        return Response({"error": "Phone number, email, and role are required for updating a user."}, status=400)

    try:
        user = CustomUser.objects.get(id=user_id)

        # Allow access only if the requesting user is admin or updating their own data
        # If you want to restrict update access based on roles, you can add this check as well
        # if request.user.role != 'admin' and request.user.id != user.id and request.user.role != 'manager':
        #     return Response({"error": "You are not authorized to update this user."}, status=403)

        # Check for duplicate phone number if it's different from the current one
        if phone_number != user.phone_number and CustomUser.objects.filter(phone_number=phone_number).exists():
            return Response({"error": "This phone number is already assigned to another user."}, status=400)

        # Check for duplicate email if it's different from the current one
        if email != user.email and CustomUser.objects.filter(email=email).exists():
            return Response({"error": "This email address is already assigned to another user."}, status=400)

        # Update user fields
        user.phone_number = phone_number
        user.email = email
        user.role = role
        user.save()

        return Response({"message": "User updated successfully."}, status=200)

    except ObjectDoesNotExist:
        return Response({"error": "User with the given ID does not exist."}, status=404)

    


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_all_users(request):
    if request.user.role != 'admin':
        return Response({"error": "You are not authorized to view this resource."}, status=403)
    
    users = CustomUser.objects.all().values(
        'id', 'phone_number', 'email', 'role', 'created_at', 'created_by__id', 'created_by__phone_number', 'created_by__email', 'created_by__role', 'created_by__created_at',
    )
    return Response({"users": list(users)}, status=200)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_by_id(request, user_id):
    try:
        user = CustomUser.objects.select_related('created_by').get(id=user_id)
        
        # if request.user.role != 'admin' and request.user.id != user.id or request.user.role != 'manager' and request.user.id != user.id:
        #     return Response({"error": "You are not authorized to access this user."}, status=403)
        
        created_by_user = user.created_by
        return Response({
            "id": user.id,
            "phone_number": user.phone_number,
            "email": user.email,
            "role": user.role,
            "created_at": user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "created_by": {
                "id": created_by_user.id,
                "email": created_by_user.email,
                "phone": created_by_user.phone_number,
                "role": created_by_user.role,
                "created_at": created_by_user.created_at,
            } if created_by_user else None,
        }, status=200)
    except ObjectDoesNotExist:
        return Response({"error": "User with the given ID does not exist."}, status=404)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_by_email(request):
    email = request.query_params.get('email')

    if not email:
        return Response({"error": "Email is required to search for a user."}, status=400)

    try:
        user = CustomUser.objects.select_related('created_by').get(email=email)
        
        if request.user.role != 'admin' and request.user.email != email:
            return Response({"error": "You are not authorized to access this user."}, status=403)

        created_by_user = user.created_by
        return Response({
            "id": user.id,
            "phone_number": user.phone_number,
            "email": user.email,
            "role": user.role,
            "created_at": user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "created_by": {
                "id": created_by_user.id,
                "email": created_by_user.email,
                "role": created_by_user.role,
                "phone": created_by_user.phone_number,
                "created_at": created_by_user.created_at,
            } if created_by_user else None,
        }, status=200)
    except ObjectDoesNotExist:
        return Response({"error": "User with the given email does not exist."}, status=404)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_by_phone(request):
    phone_number = request.query_params.get('phone_number')

    if not phone_number:
        return Response({"error": "Phone number is required to search for a user."}, status=400)

    try:
        user = CustomUser.objects.select_related('created_by').get(phone_number=phone_number)
        
        if request.user.role != 'admin' and request.user.phone_number != phone_number:
            return Response({"error": "You are not authorized to access this user."}, status=403)

        created_by_user = user.created_by
        return Response({
            "id": user.id,
            "phone_number": user.phone_number,
            "email": user.email,
            "role": user.role,
            "created_at": user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "created_by": {
                "id": created_by_user.id,
                "email": created_by_user.email,
                "role": created_by_user.role,
                "phone": created_by_user.phone_number,
                "created_at": created_by_user.created_at,
            } if created_by_user else None,
        }, status=200)
    except ObjectDoesNotExist:
        return Response({"error": "User with the given phone number does not exist."}, status=404)




import logging
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import ContactUsSerializer
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework import status

# Configure logging
logger = logging.getLogger(__name__)

@api_view(['POST'])
def contact_us(request):
    logger.info("Received contact request with data: %s", request.data)
    
    serializer = ContactUsSerializer(data=request.data)
    
    if serializer.is_valid():
        names = serializer.validated_data['names']
        email = serializer.validated_data['email']
        subject = serializer.validated_data['subject']
        description = serializer.validated_data['description']
        
        # Check for empty fields
        if not names.strip():
            logger.error("Name field is empty.")
            return Response({"error": "Name field cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)
        if not subject.strip():
            logger.error("Subject field is empty.")
            return Response({"error": "Subject field cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)
        if not description.strip():
            logger.error("Description field is empty.")
            return Response({"error": "Description field cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            logger.error("Invalid email format: %s", email)
            return Response({"error": "Invalid email format."}, status=status.HTTP_400_BAD_REQUEST)

        # Sending email
        try:
            send_mail(
                subject=f"Contact Us: {subject}",
                message=f"Name: {names}\nEmail: {email}\n\nDescription:\n{description}",
                from_email=email,
                recipient_list=['harerimanaclementkella@gmail.com'],
                fail_silently=False,
            )
            logger.info("Email sent successfully to %s", email)
            return Response({"message": "Email sent successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception("An error occurred while sending email: %s", e)
            return Response({"error": "Failed to send email."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    logger.error("Invalid serializer data: %s", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

   
   
   
   # Manager Drivers
   
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def manager_list_all_users(request):
    if request.user.role != 'manager':
        return Response({"error": "You are not authorized to view this resource."}, status=403)
    
    # Filter users where 'created_by' matches the logged-in user's ID
    users = CustomUser.objects.filter(created_by=request.user).values(
        'id', 'phone_number', 'email', 'role', 'created_at',
        'created_by__id', 'created_by__phone_number', 'created_by__email', 'created_by__role', 'created_by__created_at',
    )
    
    return Response({"users": list(users)}, status=200)
