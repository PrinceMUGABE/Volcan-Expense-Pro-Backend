from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Policy
from .serializers import PolicySerializer, UpdatePolicySerializer

# Create a policy
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_policy(request):
    data = request.data
    data['created_by'] = request.user.id
    serializer = PolicySerializer(data=data, partial=True)
    if serializer.is_valid():
        serializer.save(created_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Get a policy by ID
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_policy_by_id(request, policy_id):
    try:
        policy = Policy.objects.get(id=policy_id)
        serializer = PolicySerializer(policy)
        return Response(serializer.data)
    except Policy.DoesNotExist:
        return Response({"error": "Policy not found"}, status=status.HTTP_404_NOT_FOUND)

# Get all policies
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_policies(request):
    policies = Policy.objects.all()
    serializer = PolicySerializer(policies, many=True)
    return Response(serializer.data)




# Get all policies created by the logged-in user
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_policies_by_user(request):
    policies = Policy.objects.filter(created_by=request.user)
    serializer = PolicySerializer(policies, many=True)
    return Response(serializer.data)

# Update a policy
import logging

logger = logging.getLogger(__name__)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_policy(request, policy_id):
    try:
        policy = Policy.objects.get(id=policy_id)
        user = request.user
        if user.role != 'admin':
            return Response({"error": "You are not authorized to update this policy"}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = UpdatePolicySerializer(policy, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Policy.DoesNotExist:
        return Response({"error": "Policy not found"}, status=status.HTTP_404_NOT_FOUND)




# Delete a policy
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_policy(request, policy_id):
    try:
        policy = Policy.objects.get(id=policy_id)
        admin = request.user
        if admin.role != 'admin':
           return Response({"error": "Only admin is allowed to delete policy"}, status=status.HTTP_403_FORBIDDEN)
         
        policy.delete()
        return Response({"message": "Policy deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    except Policy.DoesNotExist:
        return Response({"error": "Policy not found"}, status=status.HTTP_404_NOT_FOUND)





