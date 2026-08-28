from decimal import Decimal, ROUND_HALF_UP

from django.db import models
from django.conf import settings


TWO_PLACES = Decimal("0.01")


class Video(models.Model):
    youtube_url = models.URLField()

    def __str__(self):
        return self.youtube_url


class Enquiry(models.Model):

    full_name = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=20)

    status = models.CharField(max_length=100)
    property_type = models.CharField(max_length=100)

    city = models.CharField(max_length=200)

    min_area = models.CharField(max_length=50)
    max_area = models.CharField(max_length=50)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name


class ContactMessage(models.Model):

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Project(models.Model):

    title = models.CharField(max_length=200)
    badge = models.CharField(max_length=100, default="New Launch")
    bhk = models.CharField(max_length=100, default="2 BHK")
    location = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to="projects/")
    brouchure = models.FileField(upload_to="brochures/", default=None, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.title
    
class Blogs(models.Model):
    name = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to="blogs/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class BookingPricing(models.Model):
    """Admin-editable price + GST for each booking service (site visit / ad shoot).

    Exactly one active row per booking_type is the live price charged on the
    next booking of that type. Changing it here takes effect immediately —
    no code or settings.py changes needed. Past bookings keep their own
    snapshot of base/GST/total at the time they were paid (see
    ShootBooking/SiteVisitBooking below), so editing a price never rewrites
    old invoices.
    """

    BOOKING_TYPE_CHOICES = [
        ("site_visit", "Site Visit Booking"),
        ("shoot", "Ad Video Shoot Booking"),
    ]

    booking_type = models.CharField(max_length=20, choices=BOOKING_TYPE_CHOICES, unique=True)
    base_amount = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Price in INR, before GST."
    )
    gst_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("18.00"),
        help_text="GST rate applied on top of the base amount, e.g. 18.00 for 18%.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Uncheck to stop charging for this service (bookings will be blocked).",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Booking Pricing"
        verbose_name_plural = "Booking Pricing"
        ordering = ["booking_type"]

    def __str__(self):
        return f"{self.get_booking_type_display()} — Rs. {self.total_amount} (incl. {self.gst_percentage}% GST)"

    @property
    def gst_amount(self):
        return (self.base_amount * self.gst_percentage / Decimal("100")).quantize(
            TWO_PLACES, rounding=ROUND_HALF_UP
        )

    @property
    def total_amount(self):
        return (self.base_amount + self.gst_amount).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


def get_booking_pricing(booking_type, fallback_amount):
    """Returns (base_amount, gst_percentage, gst_amount, total_amount) as Decimals.

    Looks up the active BookingPricing row for booking_type. If none exists
    yet (e.g. right after this feature is deployed, before the admin has
    added pricing), falls back to a flat fallback_amount with 0% GST so the
    booking flow never breaks.
    """
    pricing = BookingPricing.objects.filter(booking_type=booking_type, is_active=True).first()

    if pricing:
        return pricing.base_amount, pricing.gst_percentage, pricing.gst_amount, pricing.total_amount

    base = Decimal(str(fallback_amount)).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
    return base, Decimal("0.00"), Decimal("0.00"), base


class ShootBooking(models.Model):
    """A booking for a professional ad video shoot at a property, paid for via Razorpay."""

    TIME_SLOT_CHOICES = [
        ("09:00-11:00", "9:00 AM - 11:00 AM"),
        ("11:00-13:00", "11:00 AM - 1:00 PM"),
        ("14:00-16:00", "2:00 PM - 4:00 PM"),
        ("16:00-18:00", "4:00 PM - 6:00 PM"),
    ]

    STATUS_CHOICES = [
        ("pending_payment", "Pending Payment"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
    ]

    property_name = models.CharField(max_length=200)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    shoot_address = models.CharField(max_length=300, blank=True)

    preferred_date = models.DateField()
    time_slot = models.CharField(max_length=50, choices=TIME_SLOT_CHOICES)
    notes = models.TextField(blank=True, null=True)

    # Pricing snapshot at the time this booking was created (from the active
    # BookingPricing row) — kept even if the admin changes prices later, so
    # this booking's own receipt/invoice never changes retroactively.
    base_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gst_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, help_text="Total amount charged (base + GST)."
    )

    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending_payment")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.property_name} - {self.preferred_date} ({self.get_time_slot_display()})"


class SiteVisitBooking(models.Model):
    """A booking for a physical property site-visit slot, paid for via Razorpay.

    Kept as its own model (separate from ShootBooking) since a site visit and
    an ad-video shoot are different services with different fields, pricing,
    and time slots, even though both share the same slot-booking + payment flow.
    """

    PROPERTY_CATEGORY_CHOICES = [
        ("flat", "Flat / Apartment"),
        ("villa", "Villa"),
    ]

    # Only these two slots are offered by the frontend's restricted slot picker.
    TIME_SLOT_CHOICES = [
        ("11:00-13:00", "11:00 AM - 1:00 PM"),
        ("14:00-16:00", "2:00 PM - 4:00 PM"),
    ]

    STATUS_CHOICES = [
        ("pending_payment", "Pending Payment"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
    ]

    # Contact
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)

    # Community / location
    community = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    property_name = models.CharField(max_length=250, blank=True)
    site_address = models.CharField(max_length=300, blank=True)

    # Property category & specifications
    property_category = models.CharField(max_length=10, choices=PROPERTY_CATEGORY_CHOICES, default="flat")
    bhk_type = models.CharField(max_length=50, blank=True)
    structure = models.CharField(max_length=50, blank=True)
    floor_number = models.CharField(max_length=50, blank=True)
    total_floors = models.CharField(max_length=50, blank=True)
    size_sqft = models.CharField(max_length=50, blank=True)
    facing = models.CharField(max_length=20, blank=True)
    furnishing = models.CharField(max_length=30, blank=True)
    parking = models.CharField(max_length=30, blank=True)
    villa_number = models.CharField(max_length=50, blank=True)

    # Slot
    preferred_date = models.DateField()
    time_slot = models.CharField(max_length=50, choices=TIME_SLOT_CHOICES)
    notes = models.TextField(blank=True, null=True)

    # Pricing snapshot at the time this booking was created (from the active
    # BookingPricing row) — kept even if the admin changes prices later, so
    # this booking's own receipt/invoice never changes retroactively.
    base_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gst_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, help_text="Total amount charged (base + GST)."
    )

    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending_payment")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.community} - {self.preferred_date} ({self.get_time_slot_display()})"


class EmailConfiguration(models.Model):
    """Backend entity for managing email host and SMTP settings dynamically without environment variables."""

    email_host = models.CharField(max_length=255, default="smtp.gmail.com", help_text="SMTP server address")
    email_port = models.IntegerField(default=587, help_text="SMTP port (e.g. 587 for TLS, 465 for SSL)")
    email_use_tls = models.BooleanField(default=True, help_text="Use TLS connection")
    email_use_ssl = models.BooleanField(default=False, help_text="Use SSL connection")
    email_host_user = models.CharField(max_length=255, blank=True, default="", help_text="SMTP Username / Email address")
    email_host_password = models.CharField(max_length=255, blank=True, default="", help_text="SMTP Password / App Password")
    default_from_email = models.CharField(
        max_length=255,
        default="Sreemr Homes <noreply@sreemrhomes.com>",
        help_text="Default Sender header (e.g. Sreemr Homes <noreply@sreemrhomes.com>)",
    )
    is_active = models.BooleanField(default=True, help_text="Set to True to use this email configuration")

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Email Configuration"
        verbose_name_plural = "Email Configurations"
        ordering = ["-updated_at"]

    def __str__(self):
        status = "Active" if self.is_active else "Inactive"
        user = self.email_host_user or "Console Fallback"
        return f"{user} ({self.email_host}:{self.email_port}) - {status}"


def get_active_email_connection():
    """
    Returns tuple of (connection, from_email) using the active EmailConfiguration backend entity.
    If no active configuration exists or host user is empty, falls back to Django default mail connection.
    """
    from django.core.mail import get_connection

    try:
        config = EmailConfiguration.objects.filter(is_active=True).first()
        if config and config.email_host_user:
            connection = get_connection(
                backend="django.core.mail.backends.smtp.EmailBackend",
                host=config.email_host,
                port=config.email_port,
                username=config.email_host_user,
                password=config.email_host_password,
                use_tls=config.email_use_tls,
                use_ssl=config.email_use_ssl,
                fail_silently=False,
            )
            from_email = config.default_from_email or getattr(settings, "DEFAULT_FROM_EMAIL", "Sreemr Homes <noreply@sreemrhomes.com>")
            return connection, from_email
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning("Could not load dynamic EmailConfiguration: %s", e)

    return get_connection(fail_silently=False), getattr(settings, "DEFAULT_FROM_EMAIL", "Sreemr Homes <noreply@sreemrhomes.com>")
