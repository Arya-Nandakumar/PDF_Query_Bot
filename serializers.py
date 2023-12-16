# serializers.py in your_app

from rest_framework import serializers
from .models import UploadedFile, MessagesHistory

class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = ['file', 'session_id']


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessagesHistory
        fields = '__all__'