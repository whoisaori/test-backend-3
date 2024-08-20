from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from api.v1.permissions import IsStudentOrIsAdmin, ReadOnlyOrIsAdmin
from api.v1.serializers.course_serializer import (CourseSerializer,
                                                  CreateCourseSerializer,
                                                  CreateGroupSerializer,
                                                  CreateLessonSerializer,
                                                  GroupSerializer,
                                                  LessonSerializer)
from api.v1.serializers.user_serializer import SubscriptionSerializer
from courses.models import Course, Group
from users.models import Subscription


class LessonViewSet(viewsets.ModelViewSet):
    """Уроки."""

    permission_classes = (IsStudentOrIsAdmin,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return LessonSerializer
        return CreateLessonSerializer

    def perform_create(self, serializer):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        serializer.save(course=course)

    def get_queryset(self):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        return course.lessons.all()


class GroupViewSet(viewsets.ModelViewSet):
    """Группы."""

    permission_classes = (permissions.IsAdminUser,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return GroupSerializer
        return CreateGroupSerializer

    def perform_create(self, serializer):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        serializer.save(course=course)

    def get_queryset(self):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        return course.groups.all()


class CourseViewSet(viewsets.ModelViewSet):
    """Курсы """

    queryset = Course.objects.all()
    permission_classes = (ReadOnlyOrIsAdmin,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return CourseSerializer
        return CreateCourseSerializer

    @action(
        methods=['post'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def pay(self, request, pk):
        """Покупка доступа к курсу (подписка на курс)."""
        user = request.user
        course = get_object_or_404(Course, id=pk)

        # Проверяем, есть ли у пользователя достаточно бонусов
        if user.balance < course.price:
            return Response(
                {"detail": "Недостаточно бонусов для покупки курса."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверяем, не подписан ли уже пользователь на этот курс
        if Subscription.objects.filter(user=user, course=course).exists():
            return Response(
                {"detail": "Вы уже подписаны на этот курс."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Создаем подписку
        subscription = Subscription.objects.create(user=user, course=course)

        # Вычитаем бонусы
        user.balance -= course.price
        user.save()

        # Распределяем пользователя по группе
        existing_subscriptions = Subscription.objects.filter(course=course)
        group_counts = existing_subscriptions.values('group').annotate(count=Count('id'))
        group_counts_dict = {group_count['group']: group_count['count'] for group_count in group_counts}
        min_count = min(group_counts_dict.values(), default=0)
        available_groups = Group.objects.filter(course=course, id__in=[group for group, count in group_counts_dict.items() if count == min_count])
        if not available_groups.exists():
            available_groups = Group.objects.filter(course=course)
        subscription.group = available_groups.first()
        subscription.save()

        serializer = SubscriptionSerializer(subscription)
        data = serializer.data
        return Response(
            data=data,
            status=status.HTTP_201_CREATED
        )
