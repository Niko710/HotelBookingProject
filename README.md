# Hotel Booking

Django course project. Hotels, rooms and bookings are stored in a local SQLite
database. The application does not use an external API.

## Pages

- Home - favorite rooms, or three sample rooms when there are none
- Hotels - all hotels, filter by city
- Hotel details - rooms of one hotel
- Rooms - all rooms, filter by type, price and dates, six rooms per page
- Bookings - booked rooms, filter by city, cancel booking
- Register & Login - user accounts with password reset
- Profile - personal info, user bookings, and saved rooms

## Models

- `Hotel` - name, city, address, image
- `RoomType` - Single Room, Double Room, Deluxe Room, Family Room
- `Room` - hotel, room type, name, price, max guests, image
- `Booking` - room, customer name, phone, check-in, check-out, total price, status

A hotel has many rooms. A room type has many rooms. A room has many bookings.
Images are uploaded to the `media/` folder and the database stores their paths.

## How to run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata sample_data
python manage.py runserver
```

Open http://127.0.0.1:8000/.

The local `db.sqlite3` already contains the sample data, but that file is ignored
by Git. On a fresh copy, run `migrate` and `loaddata` first. The fixture imports 4
hotels, 4 room types, 8 rooms and 3 bookings.

To use the admin page, create a user first:

```bash
python manage.py createsuperuser
```

Then open http://127.0.0.1:8000/admin/.

The admin has simple list pages:

- **Hotels** - filter by city, search by name, city or address.
- **Room types** - search by name.
- **Rooms** - filter by hotel or room type, search by room or hotel name.
- **Bookings** - filter by status, hotel or room type, search by guest, phone or
  room, and browse by check-in date.

## Main decisions

- **SQLite instead of an external API.** All data is stored locally, so the
  models are the source of truth. SQLite is built into Django and needs no server.
- **Images with `ImageField`.** Files live in `media/`, the database stores the
  relative path. `Pillow` is required for `ImageField`.
- **Availability is checked in the database.** A booking overlaps when
  `check_in < new_check_out` and `check_out > new_check_in`.
- **The total price is calculated on the server.** The browser cannot change the
  price that is saved.
- **Favorites use the session.** There is no login system, so favorite room IDs
  are stored in the browser session.
- **One shared room card.** `_room_card.html` is included by the home, hotel
  detail and room list pages, so the card markup is written only once.
- **Django Paginator.** Rooms and hotels show six items per page, and bookings
  show five per page. Pagination links keep the current filters, so page 2 stays
  filtered.
- **Plain HTML and a small CSS file.** The project focuses on Django and the
  database, not on a frontend framework. The styling is a simple blue and white
  theme with a plain header, blue hero, white cards, buttons and a table.
- **Sample data is a fixture.** `booking/fixtures/sample_data.json` can be loaded
  with `loaddata`, so the data can be restored at any time.
- **User accounts.** Built-in Django authentication for register, login, logout,
  password reset and user profiles. Bookings made while logged in link to the user.

## Project structure

```text
FinalProject/
├── manage.py
├── requirements.txt
├── README.md
├── .gitignore
├── db.sqlite3                 # local database (ignored by Git)
├── media/
│   ├── hotels/
│   └── rooms/
├── hotel_project/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── booking/
    ├── models.py
    ├── forms.py
    ├── views.py
    ├── urls.py
    ├── admin.py
    ├── apps.py
    ├── tests.py
    ├── migrations/
    │   ├── 0001_initial.py
    │   └── 0002_booking_user.py
    ├── fixtures/
    │   └── sample_data.json
    ├── templates/booking/
    │   ├── base.html
    │   ├── home.html
    │   ├── hotel_list.html
    │   ├── hotel_detail.html
    │   ├── room_list.html
    │   ├── room_detail.html
    │   ├── booking_list.html
    │   ├── _room_card.html
    │   ├── login.html
    │   ├── register.html
    │   ├── profile.html
    │   ├── password_reset.html
    │   ├── password_reset_done.html
    │   ├── password_reset_confirm.html
    │   └── password_reset_complete.html
    └── static/booking/css/style.css
```

## Checks

```bash
python manage.py check
python manage.py shell -c "from booking.models import Hotel, Room, Booking; print(Hotel.objects.count(), Room.objects.count(), Booking.objects.count())"
```

Expected output: `4 8 3`.
