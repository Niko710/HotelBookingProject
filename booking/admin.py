from django.contrib import admin

from .models import Booking, Hotel, Room, RoomType


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "address")
    list_filter = ("city",)
    search_fields = ("name", "city", "address")


@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("name", "hotel", "room_type", "price", "max_guests")
    list_filter = ("hotel", "room_type")
    search_fields = ("name", "hotel__name")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "customer_name",
        "user",
        "room",
        "check_in",
        "check_out",
        "total_price",
        "is_confirmed",
    )
    list_filter = ("is_confirmed", "room__hotel", "room__room_type")
    list_editable = ("is_confirmed",)
    search_fields = ("customer_name", "customer_phone", "room__name")
    date_hierarchy = "check_in"
