from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("hotels/", views.hotel_list, name="hotel_list"),
    path("hotels/<int:hotel_id>/", views.hotel_detail, name="hotel_detail"),
    path("rooms/", views.room_list, name="room_list"),
    path("rooms/<int:room_id>/", views.room_detail, name="room_detail"),
    path("rooms/<int:room_id>/favorite/", views.toggle_favorite, name="toggle_favorite"),
    path("bookings/", views.booking_list, name="booking_list"),
    path(
        "bookings/<int:booking_id>/cancel/",
        views.cancel_booking,
        name="cancel_booking",
    ),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="booking/password_reset.html",
            email_template_name="booking/password_reset_email.html",
            subject_template_name="booking/password_reset_subject.txt",
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="booking/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="booking/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset-complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="booking/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]
