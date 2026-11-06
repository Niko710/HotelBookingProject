import datetime

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ProfileForm, RegisterForm
from .models import Booking, Hotel, Room, RoomType


def parse_date(value):
    try:
        return datetime.date.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def room_is_available(room, check_in, check_out):
    return not Booking.objects.filter(
        room=room,
        check_in__lt=check_out,
        check_out__gt=check_in,
    ).exists()


def home(request):
    favorites = request.session.get("favorites", [])
    rooms = list(
        Room.objects.filter(id__in=favorites).select_related("hotel", "room_type")
    )
    has_favorites = bool(rooms)

    if not rooms:
        rooms = list(Room.objects.select_related("hotel", "room_type")[:3])

    return render(
        request,
        "booking/home.html",
        {
            "rooms": rooms,
            "favorite_ids": favorites,
            "has_favorites": has_favorites,
        },
    )


def hotel_list(request):
    hotels = Hotel.objects.all().order_by("id")
    cities = sorted(set(Hotel.objects.values_list("city", flat=True)))
    city = request.GET.get("city", "")

    if city:
        hotels = hotels.filter(city=city)

    paginator = Paginator(hotels, 6)
    page_obj = paginator.get_page(request.GET.get("page"))

    params = request.GET.copy()
    params.pop("page", None)
    query_string = params.urlencode()

    return render(
        request,
        "booking/hotel_list.html",
        {
            "hotels": page_obj,
            "page_obj": page_obj,
            "cities": cities,
            "city": city,
            "query_string": query_string,
        },
    )


def hotel_detail(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    favorites = request.session.get("favorites", [])

    return render(
        request,
        "booking/hotel_detail.html",
        {"hotel": hotel, "favorite_ids": favorites},
    )


def room_list(request):
    rooms = Room.objects.select_related("hotel", "room_type").order_by("id")

    room_type = request.GET.get("room_type", "")
    price_from = request.GET.get("price_from", "")
    price_to = request.GET.get("price_to", "")
    check_in_text = request.GET.get("check_in", "")
    check_out_text = request.GET.get("check_out", "")

    if room_type:
        rooms = rooms.filter(room_type_id=room_type)

    if price_from.isdigit():
        rooms = rooms.filter(price__gte=int(price_from))

    if price_to.isdigit():
        rooms = rooms.filter(price__lte=int(price_to))

    check_in = parse_date(check_in_text)
    check_out = parse_date(check_out_text)

    if check_in_text or check_out_text:
        if not check_in or not check_out:
            messages.error(request, "Please choose both check-in and check-out dates.")
        elif check_out <= check_in:
            messages.error(request, "Check-out must be after check-in.")
        else:
            rooms = [
                room
                for room in rooms
                if room_is_available(room, check_in, check_out)
            ]

    favorites = request.session.get("favorites", [])

    paginator = Paginator(rooms, 6)
    page_obj = paginator.get_page(request.GET.get("page"))

    params = request.GET.copy()
    params.pop("page", None)
    query_string = params.urlencode()

    return render(
        request,
        "booking/room_list.html",
        {
            "rooms": page_obj,
            "page_obj": page_obj,
            "query_string": query_string,
            "room_types": RoomType.objects.all(),
            "room_type": room_type,
            "price_from": price_from,
            "price_to": price_to,
            "check_in": check_in_text,
            "check_out": check_out_text,
            "favorite_ids": favorites,
        },
    )


def room_detail(request, room_id):
    room = get_object_or_404(
        Room.objects.select_related("hotel", "room_type"), id=room_id
    )

    errors = []
    name = ""
    phone = ""
    check_in_text = request.GET.get("check_in", "")
    check_out_text = request.GET.get("check_out", "")

    if request.user.is_authenticated:
        name = request.user.get_full_name() or request.user.username

    if request.method == "POST":
        name = request.POST.get("customer_name", "").strip()
        phone = request.POST.get("customer_phone", "").strip()
        check_in_text = request.POST.get("check_in", "")
        check_out_text = request.POST.get("check_out", "")

        check_in = parse_date(check_in_text)
        check_out = parse_date(check_out_text)

        if not name:
            errors.append("Please enter your name.")
        if not phone:
            errors.append("Please enter your phone number.")
        if not check_in or not check_out:
            errors.append("Please choose both dates.")
        elif check_out <= check_in:
            errors.append("Check-out must be after check-in.")
        elif check_in < datetime.date.today():
            errors.append("Check-in cannot be in the past.")

        if not errors:
            if not room_is_available(room, check_in, check_out):
                errors.append("This room is already booked for these dates.")
            else:
                nights = (check_out - check_in).days
                Booking.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    room=room,
                    customer_name=name,
                    customer_phone=phone,
                    check_in=check_in,
                    check_out=check_out,
                    total_price=nights * room.price,
                    is_confirmed=True,
                )
                messages.success(request, "Booking saved.")
                return redirect("booking_list")

    return render(
        request,
        "booking/room_detail.html",
        {
            "room": room,
            "errors": errors,
            "name": name,
            "phone": phone,
            "check_in": check_in_text,
            "check_out": check_out_text,
        },
    )


def booking_list(request):
    bookings = Booking.objects.select_related("room__hotel").order_by("-id")
    cities = sorted({booking.room.hotel.city for booking in bookings})
    city = request.GET.get("city", "")

    if city:
        bookings = bookings.filter(room__hotel__city=city)

    paginator = Paginator(bookings, 5)
    page_obj = paginator.get_page(request.GET.get("page"))

    params = request.GET.copy()
    params.pop("page", None)
    query_string = params.urlencode()

    return render(
        request,
        "booking/booking_list.html",
        {
            "bookings": page_obj,
            "page_obj": page_obj,
            "cities": cities,
            "city": city,
            "query_string": query_string,
        },
    )


@require_POST
def toggle_favorite(request, room_id):
    get_object_or_404(Room, id=room_id)

    favorites = request.session.get("favorites", [])

    if room_id in favorites:
        favorites.remove(room_id)
        messages.info(request, "Room removed from favorites.")
    else:
        favorites.append(room_id)
        messages.success(request, "Room added to favorites.")

    request.session["favorites"] = favorites

    next_page = request.POST.get("next", "")
    if next_page.startswith("/") and not next_page.startswith("//"):
        return redirect(next_page)
    return redirect("home")


@require_POST
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.delete()
    messages.success(request, "Booking canceled.")

    next_page = request.POST.get("next", "")
    if next_page.startswith("/") and not next_page.startswith("//"):
        return redirect(next_page)
    return redirect("booking_list")


def register_view(request):
    if request.user.is_authenticated:
        return redirect("profile")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect("profile")
    else:
        form = RegisterForm()

    return render(request, "booking/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("profile")

    next_url = request.GET.get("next") or request.POST.get("next", "")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            if next_url and next_url.startswith("/") and not next_url.startswith("//"):
                return redirect(next_url)
            return redirect("home")
    else:
        form = AuthenticationForm(request)

    return render(request, "booking/login.html", {"form": form, "next": next_url})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("home")


@login_required(login_url="login")
def profile_view(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("profile")
    else:
        form = ProfileForm(instance=request.user)

    user_bookings = (
        Booking.objects.filter(user=request.user)
        .select_related("room__hotel")
        .order_by("-id")
    )
    favorites = request.session.get("favorites", [])
    favorite_rooms = Room.objects.filter(id__in=favorites).select_related(
        "hotel", "room_type"
    )

    return render(
        request,
        "booking/profile.html",
        {
            "form": form,
            "bookings": user_bookings,
            "favorite_rooms": favorite_rooms,
            "favorite_ids": favorites,
        },
    )
