import logging

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import (
    Video,
    Enquiry,
    ContactMessage,
    Project,
    Blogs,
    ShootBooking,
    get_active_email_connection,
)
import json
import razorpay
from datetime import datetime
from xhtml2pdf import pisa

logger = logging.getLogger(__name__)


def video_list(request):

    videos = list(Video.objects.values())

    return JsonResponse(videos, safe=False)


@csrf_exempt
def create_enquiry(request):

    if request.method == "POST":

        try:

            data = json.loads(request.body)

            print(data)

            Enquiry.objects.create(
                full_name=data.get("full_name"),
                mobile_number=data.get("mobile_number"),
                status=data.get("status"),
                property_type=data.get("property_type"),
                city=data.get("city"),
                min_area=data.get("min_area"),
                max_area=data.get("max_area"),
            )

            return JsonResponse({
                "message": "Enquiry submitted successfully"
            })

        except Exception as e:

            return JsonResponse({
                "error": str(e)
            })

    return JsonResponse({
        "error": "Invalid request"
    })


@csrf_exempt
def create_contact(request):

    if request.method == "POST":

        try:

            data = json.loads(request.body)

            ContactMessage.objects.create(
                name=data.get("name"),
                email=data.get("email"),
                phone=data.get("phone"),
                message=data.get("message"),
            )

            return JsonResponse({
                "message": "Message sent successfully"
            })

        except Exception as e:

            return JsonResponse({
                "error": str(e)
            })

    return JsonResponse({
        "error": "Invalid request"
    })


def project_list(request):
    projects = []

    for project in Project.objects.all():
        projects.append({
            "id": project.id,
            "title": project.title,
            "location": project.location,
            "description": project.description,
            "image": request.build_absolute_uri(project.image.url) if project.image else None,
            "brouchure": request.build_absolute_uri(project.brouchure.url) if project.brouchure else None,
            "badge": project.badge,
            "bhk": project.bhk,
        })

    return JsonResponse(projects, safe=False)

def block_list(request):
    blogs = []

    for blog in Blogs.objects.all():

        blogs.append({
            "id": blog.id,
            "name": blog.name,
            "author": blog.author,
            "description": blog.description,
            "image": request.build_absolute_uri(blog.image.url),
        })

    return JsonResponse(blogs, safe=False)


# ---------------------------------------------------------------------------
# Ad video shoot booking + Razorpay payment
# ---------------------------------------------------------------------------

def get_razorpay_client():
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def send_shoot_booking_receipt_email(booking):
    """Emails an HTML payment receipt for a confirmed shoot booking.

    Failures are logged rather than raised, so a broken mail server never
    breaks the payment flow for the customer (their payment already succeeded).
    """

    if not booking.email:
        return

    context = {
        "booking": booking,
        "time_slot_label": booking.get_time_slot_display(),
        "company_name": "Sreemr Homes",
    }

    html_content = render_to_string("emails/shoot_booking_receipt.html", context)
    text_content = strip_tags(html_content)

    try:
        connection, from_email = get_active_email_connection()
        email = EmailMultiAlternatives(
            subject=f"Payment Receipt - Ad Video Shoot Booking #{booking.id}",
            body=text_content,
            from_email=from_email,
            to=[booking.email],
            connection=connection,
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
    except Exception:
        logger.exception(
            "Failed to send shoot booking receipt email for booking #%s", booking.id
        )


def shoot_time_slots(request):
    """Returns the list of bookable time slots (single source of truth for the frontend)."""

    return JsonResponse({
        "time_slots": [
            {"value": value, "label": label}
            for value, label in ShootBooking.TIME_SLOT_CHOICES
        ]
    })


def shoot_booked_slots(request):
    """Returns which time slots are already paid & booked for a given date."""

    date_str = request.GET.get("date")

    if not date_str:
        return JsonResponse({"error": "date query param is required (YYYY-MM-DD)."}, status=400)

    try:
        parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

    booked = list(
        ShootBooking.objects.filter(
            preferred_date=parsed_date, status="paid"
        ).values_list("time_slot", flat=True)
    )

    return JsonResponse({"date": date_str, "booked_slots": booked})


@csrf_exempt
def create_shoot_booking(request):
    """Creates a pending ShootBooking and a matching Razorpay order for the booking fee."""

    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    try:
        data = json.loads(request.body)

        full_name = (data.get("full_name") or "").strip()
        phone = (data.get("phone") or "").strip()
        email = (data.get("email") or "").strip()
        property_name = (data.get("property_name") or "").strip()
        shoot_address = (data.get("shoot_address") or "").strip()
        preferred_date = data.get("preferred_date")
        time_slot = data.get("time_slot")
        notes = data.get("notes") or ""

        if not all([full_name, phone, property_name, preferred_date, time_slot]):
            return JsonResponse({"error": "Please fill all required fields."}, status=400)

        try:
            parsed_date = datetime.strptime(preferred_date, "%Y-%m-%d").date()
        except ValueError:
            return JsonResponse({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

        if parsed_date < timezone.localdate():
            return JsonResponse({"error": "Preferred date cannot be in the past."}, status=400)

        if time_slot not in dict(ShootBooking.TIME_SLOT_CHOICES):
            return JsonResponse({"error": "Invalid time slot."}, status=400)

        already_booked = ShootBooking.objects.filter(
            preferred_date=parsed_date, time_slot=time_slot, status="paid"
        ).exists()

        if already_booked:
            return JsonResponse(
                {"error": "This slot is already booked. Please choose another slot."}, status=409
            )

        amount_inr = settings.SHOOT_BOOKING_AMOUNT_INR
        amount_paise = int(amount_inr * 100)

        booking = ShootBooking.objects.create(
            property_name=property_name,
            full_name=full_name,
            phone=phone,
            email=email,
            shoot_address=shoot_address,
            preferred_date=parsed_date,
            time_slot=time_slot,
            notes=notes,
            amount=amount_inr,
            status="pending_payment",
        )

        client = get_razorpay_client()

        try:
            order = client.order.create({
                "amount": amount_paise,
                "currency": "INR",
                "payment_capture": 1,
                "notes": {
                    "booking_id": str(booking.id),
                    "property_name": property_name,
                    "preferred_date": preferred_date,
                    "time_slot": time_slot,
                },
            })
        except Exception as e:
            booking.status = "failed"
            booking.save(update_fields=["status"])
            return JsonResponse({"error": f"Could not initiate payment: {str(e)}"}, status=502)

        booking.razorpay_order_id = order["id"]
        booking.save(update_fields=["razorpay_order_id"])

        return JsonResponse({
            "booking_id": booking.id,
            "order_id": order["id"],
            "amount": amount_paise,
            "currency": "INR",
            "key": settings.RAZORPAY_KEY_ID,
            "name": full_name,
            "email": email,
            "phone": phone,
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def verify_shoot_payment(request):
    """Verifies the Razorpay payment signature and marks the booking as paid."""

    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    try:
        data = json.loads(request.body)

        booking_id = data.get("booking_id")
        razorpay_order_id = data.get("razorpay_order_id")
        razorpay_payment_id = data.get("razorpay_payment_id")
        razorpay_signature = data.get("razorpay_signature")

        if not all([booking_id, razorpay_order_id, razorpay_payment_id, razorpay_signature]):
            return JsonResponse({"error": "Missing payment details."}, status=400)

        try:
            booking = ShootBooking.objects.get(id=booking_id, razorpay_order_id=razorpay_order_id)
        except ShootBooking.DoesNotExist:
            return JsonResponse({"error": "Booking not found."}, status=404)

        client = get_razorpay_client()

        params = {
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature,
        }

        try:
            client.utility.verify_payment_signature(params)
        except razorpay.errors.SignatureVerificationError:
            booking.status = "failed"
            booking.save(update_fields=["status"])
            return JsonResponse({"error": "Payment verification failed."}, status=400)

        booking.razorpay_payment_id = razorpay_payment_id
        booking.razorpay_signature = razorpay_signature
        booking.status = "paid"
        booking.save(update_fields=["razorpay_payment_id", "razorpay_signature", "status"])

        send_shoot_booking_receipt_email(booking)

        return JsonResponse({
            "message": "Payment verified. Your shoot slot is booked!",
            "booking_id": booking.id,
            "status": booking.status,
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def shoot_booking_list(request):
    """Staff-only: lists all ad video shoot bookings for internal review.

    Requires the caller to already be logged in with a staff account (e.g.
    via /admin/ in the same browser session).
    """

    if not (request.user.is_authenticated and request.user.is_staff):
        return JsonResponse(
            {"error": "Unauthorized. Please log in via the admin panel first."}, status=403
        )

    bookings = []

    for booking in ShootBooking.objects.all():
        bookings.append({
            "id": booking.id,
            "property_name": booking.property_name,
            "full_name": booking.full_name,
            "phone": booking.phone,
            "email": booking.email,
            "shoot_address": booking.shoot_address,
            "preferred_date": booking.preferred_date.isoformat(),
            "time_slot": booking.time_slot,
            "time_slot_label": booking.get_time_slot_display(),
            "notes": booking.notes,
            "amount": str(booking.amount),
            "status": booking.status,
            "razorpay_order_id": booking.razorpay_order_id,
            "razorpay_payment_id": booking.razorpay_payment_id,
            "created_at": booking.created_at.isoformat(),
        })

    return JsonResponse({"bookings": bookings}, safe=False)


def shoot_booking_receipt_pdf(request, booking_id):
    """Renders the payment receipt as a downloadable PDF for a paid booking.

    Requires the requester to know the booking's phone number (passed as a
    ?phone= query param) so booking IDs alone can't be enumerated to pull up
    someone else's name, address and payment details.
    """

    try:
        booking = ShootBooking.objects.get(id=booking_id)
    except ShootBooking.DoesNotExist:
        return JsonResponse({"error": "Booking not found."}, status=404)

    phone = (request.GET.get("phone") or "").strip()
    if not phone or phone != booking.phone:
        return JsonResponse({"error": "Unauthorized."}, status=403)

    if booking.status != "paid":
        return JsonResponse({"error": "Receipt is only available for paid bookings."}, status=400)

    context = {
        "booking": booking,
        "time_slot_label": booking.get_time_slot_display(),
        "company_name": "Sreemr Homes",
    }

    html_content = render_to_string("emails/shoot_booking_receipt.html", context)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="Sreemr_Homes_Receipt_{booking.id}.pdf"'

    pisa_status = pisa.CreatePDF(html_content, dest=response, encoding="UTF-8")

    if pisa_status.err:
        return JsonResponse({"error": "Could not generate the PDF receipt."}, status=500)

    return response