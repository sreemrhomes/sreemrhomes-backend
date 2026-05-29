from django.db import models


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
    
class Block(models.Model):
    name = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to="blocks/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name