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
    create_site_visit_booking,
    verify_site_visit_payment,
    site_visit_booked_slots,
    site_visit_time_slots,
    site_visit_booking_list,
    site_visit_booking_receipt_pdf,
    booking_pricing,
)

urlpatterns = [
    path("videos/", video_list),
    path("enquiries/", create_enquiry),
    path("contact/", create_contact),
    path("projects/", project_list),
    path("blocks/", block_list),

    # Admin-configurable pricing (base price + GST) for both booking services
    path("booking-pricing/", booking_pricing),

    # Ad video shoot slot booking
    path("shoot-bookings/create/", create_shoot_booking),
    path("shoot-bookings/verify/", verify_shoot_payment),
    path("shoot-bookings/booked-slots/", shoot_booked_slots),
    path("shoot-bookings/time-slots/", shoot_time_slots),
    path("shoot-bookings/list/", shoot_booking_list),
    path("shoot-bookings/<int:booking_id>/receipt/", shoot_booking_receipt_pdf),

    # Site visit slot booking
    path("site-visit-bookings/create/", create_site_visit_booking),
    path("site-visit-bookings/verify/", verify_site_visit_payment),
    path("site-visit-bookings/booked-slots/", site_visit_booked_slots),
    path("site-visit-bookings/time-slots/", site_visit_time_slots),
    path("site-visit-bookings/list/", site_visit_booking_list),
    path("site-visit-bookings/<int:booking_id>/receipt/", site_visit_booking_receipt_pdf),
]
