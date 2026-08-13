from django.urls import path
from .views import (
    create_contact,
    video_list,
    create_enquiry,
    project_list,
    block_list,
    create_shoot_booking,
    verify_shoot_payment,
    shoot_booked_slots,
    shoot_time_slots,
    shoot_booking_list,
    shoot_booking_receipt_pdf,
)

urlpatterns = [
    path("videos/", video_list),
    path("enquiries/", create_enquiry),
    path("contact/", create_contact),
    path("projects/", project_list),
    path("blocks/", block_list),
    path("shoot-bookings/create/", create_shoot_booking),
    path("shoot-bookings/verify/", verify_shoot_payment),
    path("shoot-bookings/booked-slots/", shoot_booked_slots),
    path("shoot-bookings/time-slots/", shoot_time_slots),
    path("shoot-bookings/list/", shoot_booking_list),
    path("shoot-bookings/<int:booking_id>/receipt/", shoot_booking_receipt_pdf),
]
