from django.contrib import admin
from .models import User, restaurant, table, Booking

admin.site.register(User)
admin.site.register(restaurant)
admin.site.register(table)
admin.site.register(Booking)

