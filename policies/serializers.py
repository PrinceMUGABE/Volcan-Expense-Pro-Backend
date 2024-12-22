from rest_framework import serializers
from .models import Policy
from userApp.models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'phone_number', 'email', 'role', 'is_active', 'created_at', 'created_by']



class PolicySerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Policy
        fields = ['id', 'description', 'created_by', 'name', 'created_date']


class UpdatePolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = Policy
        fields = ['id', 'description', 'name']
