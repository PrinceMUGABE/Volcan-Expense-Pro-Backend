from rest_framework import serializers
from .models import Expense
from userApp.models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'phone_number', 'email', 'role', 'is_active', 'created_at', 'created_by']



from rest_framework import serializers
from .models import Expense
import base64

class ExpenseSerializer(serializers.ModelSerializer):
    video_base64 = serializers.SerializerMethodField()  # New field for the base64-encoded video
    user = UserSerializer(read_only=True)

    class Meta:
        model = Expense
        fields = ['id', 'user', 'category', 'vendor', 'amount', 'receipt', 'video', 'video_base64', 'date', 'status', 'reimbursement_status', 'created_at']

    def get_video_base64(self, obj):
        if obj.video and hasattr(obj.video, 'path'):
            try:
                with open(obj.video.path, 'rb') as video_file:
                    return base64.b64encode(video_file.read()).decode('utf-8')
            except Exception as e:
                print(f"Error encoding video for {obj}: {e}")
                return None
        return None
