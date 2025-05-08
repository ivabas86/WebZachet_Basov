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
    # check_in_time = serializers.TimeField(format='%H:%M:%S', input_formats=['%H:%M:%S'])
    # check_out_time = serializers.TimeField(format='%H:%M:%S', input_formats=['%H:%M:%S'])
    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ('user', 'created_at','status','restaurant')

    def validate(self, data):  # Переопределение валидации для проверки доступности столика
        table = data['table']
        check_in = data['check_in_date']
        check_in_time = data['check_in_time']
        check_out_time = data['check_out_time']
        data['restaurant'] = table.restaurant
        overlaps = Booking.objects.filter(
            restaurant=data['restaurant'],
            table=table,
            check_in_date=check_in,
            check_in_time=check_in_time,
            check_out_time=check_out_time,
            status='active'
        ).exists()

        if overlaps:
            raise serializers.ValidationError("Этот столик недоступен в эту дату и указанное время")

        return data

    # def validate(self, data):
    #     table = data.get('table')
    #     check_in = data.get('check_in_date')
    #
    #     if not all([table, check_in]):
    #         raise serializers.ValidationError("Необходимо указать столик и дату бронирования")
    #
    #     data['restaurant'] = table.restaurant
    #
    #     overlapping = Booking.objects.filter(
    #         restaurant=data['restaurant'],
    #         table=table,
    #         check_in_date=check_in,
    #         status='active'
    #     )
    #
    #     if self.instance:
    #         overlapping = overlapping.exclude(pk=self.instance.pk)
    #
    #     if overlapping.exists():
    #         raise serializers.ValidationError(
    #             f"Столик {table} в ресторане {data['restaurant']} уже забронирован "
    #             f" на дату {overlapping.first().check_in_date}"
    #         )
    #
    #     return data

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


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