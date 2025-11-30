from rest_framework import serializers
from .models import Conversation, Message

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'conversation', 'role', 'content', 'timestamp', 'metadata']
        read_only_fields = ['id', 'timestamp']

    def validate_role(self, value):
        if not value or len(value) > 20:
            raise serializers.ValidationError("Role must be 1-20 characters")
        return value

class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['role', 'content', 'metadata']
        extra_kwargs = {
            'metadata': {'required': False, 'default': dict}
        }

    def validate_role(self, value):
        if not value or len(value) > 20:
            raise serializers.ValidationError("Role must be 1-20 characters")
        return value

    def create(self, validated_data):
        # Ensure metadata has a default value if not provided
        if 'metadata' not in validated_data or validated_data['metadata'] is None:
            validated_data['metadata'] = {}
        return super().create(validated_data)

class ConversationListSerializer(serializers.ModelSerializer):
    message_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'user', 'title', 'collection_name', 'created_at', 'updated_at', 'is_archived', 'message_count', 'last_message']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def get_message_count(self, obj):
        return obj.messages.count()

    def get_last_message(self, obj):
        last_msg = obj.messages.order_by('-timestamp').first()
        if last_msg:
            return {
                'content': last_msg.content[:100],
                'role': last_msg.role,
                'timestamp': last_msg.timestamp
            }
        return None

class ConversationDetailSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'title', 'collection_name', 'created_at', 'updated_at', 'is_archived', 'messages', 'message_count']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_message_count(self, obj):
        return obj.messages.count()

class ConversationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ['id', 'title', 'collection_name']
        read_only_fields = ['id']
