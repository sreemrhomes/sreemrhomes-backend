from django.urls import path
from .views import create_contact, video_list, create_enquiry, project_list, block_list

urlpatterns = [
    path("videos/", video_list),
    path("enquiries/", create_enquiry),
    path("contact/", create_contact),
    path("projects/", project_list),
    path("blocks/", block_list),
]