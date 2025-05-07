from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Booking, restaurant, table


class restaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = restaurant
        fields = '__all__'


class tableSerializer(serializers.ModelSerializer):
    class Meta:
        model = table
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ('user', 'created_at')

    def validate(self, data):  # Переопределение валидации для проверки доступности номера
        table = data['table']
        check_in = data['check_in_date']
        check_out = data['check_out_date']

        overlaps = Booking.objects.filter(
            table=table,
            check_in_date__lt=check_out,
            check_out_date__gt=check_in,
            status='active'
        ).exists()

        if overlaps:
            raise serializers.ValidationError("Этот столик недоступен в эту дату")

        return data

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


# class ReviewSerializer(serializers.ModelSerializer):
#     user = serializers.StringRelatedField(read_only=True)
#
#     class Meta:
#         model = Review
#         fields = '__all__'


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        user = get_user_model().objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password']
        )
        return user