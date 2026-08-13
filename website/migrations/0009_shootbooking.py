from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0008_project_badge_project_bhk_project_brouchure_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="ShootBooking",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("property_name", models.CharField(max_length=200)),
                ("full_name", models.CharField(max_length=100)),
                ("phone", models.CharField(max_length=20)),
                ("email", models.EmailField(blank=True, max_length=254, null=True)),
                ("shoot_address", models.CharField(blank=True, max_length=300)),
                ("preferred_date", models.DateField()),
                (
                    "time_slot",
                    models.CharField(
                        choices=[
                            ("09:00-11:00", "9:00 AM - 11:00 AM"),
                            ("11:00-13:00", "11:00 AM - 1:00 PM"),
                            ("14:00-16:00", "2:00 PM - 4:00 PM"),
                            ("16:00-18:00", "4:00 PM - 6:00 PM"),
                        ],
                        max_length=50,
                    ),
                ),
                ("notes", models.TextField(blank=True, null=True)),
                ("amount", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("razorpay_order_id", models.CharField(blank=True, max_length=100, null=True)),
                ("razorpay_payment_id", models.CharField(blank=True, max_length=100, null=True)),
                ("razorpay_signature", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending_payment", "Pending Payment"),
                            ("paid", "Paid"),
                            ("failed", "Failed"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="pending_payment",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
