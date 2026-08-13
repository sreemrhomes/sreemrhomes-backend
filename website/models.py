from django.db import models
from django.conf import settings


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

    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

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
