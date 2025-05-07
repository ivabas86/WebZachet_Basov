from django.http import Http404
from django.views.decorators.csrf import csrf_exempt
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin, CreateModelMixin, UpdateModelMixin, \
    DestroyModelMixin
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import restaurant, table, Booking, table, restaurant
from .serializers import BookingSerializer, RegisterSerializer, tableSerializer, restaurantSerializer
from rest_framework import viewsets, permissions, filters, generics, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework.permissions import IsAuthenticated

# class YourView(APIView):
#     permission_classes = [IsAuthenticated]  # Требует аутентификации

class CustomPermission(permissions.BasePermission):
    """
    Пользователи могут выполнять различные действия в зависимости от их роли.
    """

    def has_permission(self, request, view):
        # Разрешаем только GET запросы для неаутентифицированных пользователей
        if request.method == 'GET' and not request.user.is_authenticated:
            return True

        # Разрешаем GET и POST запросы для аутентифицированных пользователей
        if request.method in ['GET', 'POST'] and request.user.is_authenticated:
            return True

        # Разрешаем все действия для администраторов
        if request.user.is_superuser:
            return True

        # Во всех остальных случаях возвращаем False
        return False


class restaurantViewSet(viewsets.ModelViewSet):
    queryset = restaurant.objects.all()
    serializer_class = restaurantSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'city']
    ordering = ['id']  # Чтобы не было предупреждения пагинации при формировании всех объектов,
    # так как для пагинации может быть важен порядок, чтобы не было дублирования. Используется OrderingFilter и ordering
    # иначе придется писать queryset = Hotel.objects.all().order_by('id')

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]  # Только админ может создавать, изменять, удалять
        return [permissions.AllowAny()]  # Пользователь может только смотреть


class tableViewSet(viewsets.ModelViewSet):
    queryset = table.objects.all()
    serializer_class = tableSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['table_type']
    filterset_fields = ['restaurant', 'table_type']
    ordering = ['id']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]  # Только админ может создавать, изменять, удалять
        return [permissions.AllowAny()]  # Пользователь может только смотреть


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']

    # authentication_classes = [JWTAuthentication]
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    permission_classes = [IsAuthenticated]
    # @csrf_exempt

    def get_queryset(self):
        """
        Так сможем разграничить направленность пользователя, если он часть команды сервиса is_staff==True, то он
        видит всё, если это обычный пользователь, то видит только свои брони
        :return:
        """
        # user = self.request.user
        # if user.is_staff:
        #     return self.queryset
        # return self.queryset.filter(user=user)

        user = self.request.user
        if user.is_staff:
            return Booking.objects.all().order_by('id')
        return Booking.objects.filter(user=user).order_by('-created_at')

    def get_permissions(self):
        if self.action in ['list', 'create', 'retrieve', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        user = self.serializer_class(data=request.data)
        user.is_valid(raise_exception=True)
        created_user = user.save()
        refresh = RefreshToken.for_user(created_user)
        return Response({
            "user": user.data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)




class restGenericAPIView(GenericAPIView, RetrieveModelMixin, ListModelMixin, CreateModelMixin, UpdateModelMixin,
                           DestroyModelMixin):
    queryset = restaurant.objects.all()
    serializer_class = restaurantSerializer
    # Переопределяем атрибут permission_classes для указания нашего собственного разрешения
    permission_classes = [CustomPermission]
    authentication_classes = [JWTAuthentication]

    # def get(self, request, *args, **kwargs):
    #     if kwargs.get(self.lookup_field):  # если был передан id или pk
    #         # возвращаем один объект
    #         return self.retrieve(request, *args, **kwargs)
    #     # Иначе возвращаем список объектов
    #     return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if kwargs.get(self.lookup_field):
            try:
                # возвращаем один объект
                return self.retrieve(request, *args, **kwargs)
            except Http404:
                return Response({'message': 'не найден'}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Иначе возвращаем список объектов
            return self.list(request, *args, **kwargs)
