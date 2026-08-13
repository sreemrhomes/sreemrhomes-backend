from django.contrib import admin
from .models import Video, Enquiry, ContactMessage, Project, Blogs, ShootBooking, EmailConfiguration


admin.site.register(Video)
admin.site.register(Enquiry)
admin.site.register(ContactMessage)
admin.site.register(Project)
admin.site.register(Blogs)


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
        "amount",
        "status",
        "created_at",
    )
    list_filter = ("status", "preferred_date", "time_slot")
    search_fields = ("property_name", "full_name", "phone", "email", "razorpay_order_id", "razorpay_payment_id")
    readonly_fields = (
        "razorpay_order_id",
        "razorpay_payment_id",
        "razorpay_signature",
        "created_at",
        "updated_at",
    )
    ordering = ("-created_at",)

