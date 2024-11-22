from rest_framework import serializers
from .models import CustomUser
from django.core.mail import send_mail

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['phone_number', 'email', 'role']

    def create(self, validated_data):
        # Generate a random password
        password = CustomUser.objects.make_random_password()
        user = CustomUser.objects.create_user(
            phone_number=validated_data['phone_number'],
            email=validated_data['email'],
            role=validated_data['role'],
            password=password
        )

        # Send the password to the user via email
        send_mail(
            subject="Your Account Password",
            message=f"Your account has been created. Your password is: {password}",
            from_email="no-reply@expensepro.com",
            recipient_list=[user.email],
        )
        return user



from django.contrib.auth import authenticate
from rest_framework import serializers

class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        phone_number = data.get('phone_number')
        password = data.get('password')

        if not phone_number or not password:
            raise serializers.ValidationError("Both phone number and password are required.")

        user = authenticate(phone_number=phone_number, password=password)
        if not user:
            raise serializers.ValidationError("Invalid phone number or password.")

        return {'user': user}


from rest_framework import serializers

class ContactUsSerializer(serializers.Serializer):
    names = serializers.CharField(max_length=100, required=True)
    email = serializers.EmailField(required=True)
    subject = serializers.CharField(max_length=255, required=True)
    description = serializers.CharField(required=True)