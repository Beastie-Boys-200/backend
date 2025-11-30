from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404

from .models import Conversation, Message
from .serializers import (
    ConversationListSerializer,
    ConversationDetailSerializer,
    ConversationCreateSerializer,
    MessageSerializer,
    MessageCreateSerializer,
)
from .permissions import IsConversationOwner

class ConversationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # КРИТИЧЕСКИ ВАЖНО: фильтровать по текущему пользователю
        queryset = Conversation.objects.filter(
            user=self.request.user
        ).prefetch_related('messages')

        # Фильтр по коллекции
        collection_name = self.request.query_params.get('collection_name')
        if collection_name:
            queryset = queryset.filter(collection_name=collection_name)

        # Фильтр по архиву
        is_archived = self.request.query_params.get('is_archived')
        if is_archived is not None:
            queryset = queryset.filter(is_archived=is_archived.lower() == 'true')

        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return ConversationListSerializer
        elif self.action == 'create':
            return ConversationCreateSerializer
        elif self.action == 'retrieve':
            return ConversationDetailSerializer
        return ConversationDetailSerializer

    def perform_create(self, serializer):
        # Всегда устанавливать текущего пользователя
        # IsAuthenticated permission гарантирует, что user существует
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['get'], url_path='messages')
    def messages(self, request, pk=None):
        conversation = self.get_object()

        # Get limit parameter (n) from query params
        limit = request.query_params.get('n')

        if limit:
            try:
                limit = int(limit)
                if limit <= 0:
                    return Response(
                        {'error': 'Parameter n must be a positive integer'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                # Get last n messages (ordered by timestamp descending, then reversed for chronological order)
                messages = list(conversation.messages.order_by('-timestamp')[:limit])
                messages.reverse()  # Return in chronological order (oldest first)
            except ValueError:
                return Response(
                    {'error': 'Parameter n must be a valid integer'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            # Return all messages if n is not specified
            messages = conversation.messages.all()

        # Always return serialized data, even if messages list is empty
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='messages')
    def add_message(self, request, pk=None):
        conversation = self.get_object()
        serializer = MessageCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(conversation=conversation)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MessageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Message.objects.filter(
            conversation__user=self.request.user
        ).select_related('conversation')
