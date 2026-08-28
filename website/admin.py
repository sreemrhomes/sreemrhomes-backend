from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Video,
    Enquiry,
    ContactMessage,
    Project,
    Blogs,
    ShootBooking,
    SiteVisitBooking,
    BookingPricing,
    EmailConfiguration,
)


admin.site.register(Video)
admin.site.register(Enquiry)
admin.site.register(ContactMessage)
admin.site.register(Project)
admin.site.register(Blogs)


@admin.register(BookingPricing)
class BookingPricingAdmin(admin.ModelAdmin):
    """Lets the admin set price + GST for Site Visit / Shoot bookings directly.

    base_amount and gst_percentage are edit-in-place from the list page (no
    need to open each row), while the GST amount and final total are shown
    live as read-only columns so there's never any doubt what a customer
    will actually be charged.
    """

    list_display = (
        "booking_type",
        "base_amount",
        "gst_percentage",
        "display_gst_amount",
        "display_total_amount",
        "is_active",
        "updated_at",
    )
    list_editable = ("base_amount", "gst_percentage", "is_active")
    list_display_links = ("booking_type",)
    readonly_fields = ("display_gst_amount", "display_total_amount", "created_at", "updated_at")
    fields = (
        "booking_type",
        "base_amount",
        "gst_percentage",
        "display_gst_amount",
        "display_total_amount",
        "is_active",
        "created_at",
        "updated_at",
    )

    def has_add_permission(self, request):
        # At most one row per booking_type is meaningful (unique=True already
        # enforces this at the DB level) — once both site_visit and shoot
        # exist, hide "Add" so nobody creates a confusing duplicate.
        if BookingPricing.objects.count() >= len(BookingPricing.BOOKING_TYPE_CHOICES):
            return False
        return super().has_add_permission(request)

    @admin.display(description="GST Amount (Rs.)")
    def display_gst_amount(self, obj):
        # obj is a blank, unsaved instance on the "add" form (base_amount not
        # filled in yet) — nothing to compute until it's actually saved.
        if obj.pk is None or obj.base_amount is None:
            return "—"
        return f"Rs. {obj.gst_amount}"

    @admin.display(description="Total Charged (Rs.)")
    def display_total_amount(self, obj):
        if obj.pk is None or obj.base_amount is None:
            return "—"
        return format_html("<strong>Rs. {}</strong>", obj.total_amount)


@admin.register(EmailConfiguration)
class EmailConfigurationAdmin(admin.ModelAdmin):
    list_display = (
        "email_host_user",
        "email_host",
        "email_port",
        "email_use_tls",
        "email_use_ssl",
        "is_active",
        "updated_at",
    )
    list_filter = ("is_active", "email_use_tls", "email_use_ssl")
    search_fields = ("email_host", "email_host_user", "default_from_email")


@admin.register(ShootBooking)
class ShootBookingAdmin(admin.ModelAdmin):
    list_display = (
        "property_name",
        "full_name",
        "phone",
        "preferred_date",
        "time_slot",
        "base_amount",
        "gst_amount",
        "amount",
        "status",
        "created_at",
    )
    list_filter = ("status", "preferred_date", "time_slot")
    search_fields = ("property_name", "full_name", "phone", "email", "razorpay_order_id", "razorpay_payment_id")
    readonly_fields = (
        "base_amount",
        "gst_percentage",
        "gst_amount",
        "amount",
        "razorpay_order_id",
        "razorpay_payment_id",
        "razorpay_signature",
        "created_at",
        "updated_at",
    )
    ordering = ("-created_at",)


@admin.register(SiteVisitBooking)
class SiteVisitBookingAdmin(admin.ModelAdmin):
    list_display = (
        "community",
        "full_name",
        "phone",
        "property_category",
        "preferred_date",
        "time_slot",
        "base_amount",
        "gst_amount",
        "amount",
        "status",
        "created_at",
    )
    list_filter = ("status", "property_category", "preferred_date", "time_slot")
    search_fields = (
        "community",
        "location",
        "full_name",
        "phone",
        "email",
        "razorpay_order_id",
        "razorpay_payment_id",
    )
    readonly_fields = (
        "base_amount",
        "gst_percentage",
        "gst_amount",
        "amount",
        "razorpay_order_id",
        "razorpay_payment_id",
        "razorpay_signature",
        "created_at",
        "updated_at",
    )
    ordering = ("-created_at",)

