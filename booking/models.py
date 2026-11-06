from django.contrib.auth.models import User
from django.db import models


class Hotel(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    address = models.CharField(max_length=150)
    image = models.ImageField(upload_to="hotels/", blank=True)

    def __str__(self):
        return self.name


class RoomType(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Room(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="rooms")
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.IntegerField()
    max_guests = models.IntegerField()
    image = models.ImageField(upload_to="rooms/", blank=True)

    def __str__(self):
        return self.name


class Booking(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="bookings"
    )
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=80)
    customer_phone = models.CharField(max_length=30)
    check_in = models.DateField()
    check_out = models.DateField()
    total_price = models.IntegerField()
    is_confirmed = models.BooleanField(default=True)

    def __str__(self):
        return self.customer_name
