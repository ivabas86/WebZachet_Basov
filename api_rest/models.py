from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model


# Пользователь
class User(AbstractUser):
    pass


# Отель
class restaurant(models.Model):
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    address = models.TextField()
    description = models.TextField()
    rating = models.FloatField()

    class Meta:
        db_table = 'api_rest_restaurant'

    def __str__(self):
        return self.name


# Номер
class table(models.Model):
    TABLE_TYPES = [
        ('single', 'Single'),
        ('double', 'Double'),
        ('for_four', 'For_four'),
    ]
    restaurant = models.ForeignKey(restaurant, on_delete=models.CASCADE, related_name='tables')
    table_number = models.CharField(max_length=10)
    table_type = models.CharField(max_length=10, choices=TABLE_TYPES)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    capacity = models.IntegerField()

    def __str__(self):
        return f"{self.restaurant.name} - {self.table_number}"


# Бронирование
class Booking(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='bookings')
    table = models.ForeignKey(table, on_delete=models.CASCADE, related_name='bookings')
    restaurant = models.ForeignKey(restaurant, on_delete=models.CASCADE)
    check_in_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    check_in_time = models.TimeField()
    check_out_time = models.TimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    class Meta:
        ordering = ['-check_in_date', '-check_in_time', '-check_out_time']

    def __str__(self):
        return (f"Booking by {self.user.username} - table {self.table.id} at {self.check_in_time} - {self.check_out_time} "
                f"on {self.check_in_date}")


    # def __str__(self):
    #     return f"Booking by {self.user.username} - table {self.table.id}"


# # Отзыв
# class Review(models.Model):
#     user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='reviews')
#     hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='reviews')
#     rating = models.IntegerField()
#     comment = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return f"Review by {self.user.username} - {self.hotel.name}"

