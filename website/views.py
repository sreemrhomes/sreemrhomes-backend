from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Video, Enquiry, ContactMessage, Project, Blogs
import json


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