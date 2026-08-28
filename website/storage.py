"""Cloudflare R2 media storage backend.

Thin wrapper around django-storages' S3Storage that validates the R2_*
environment variables lazily — only when Django actually needs to read or
write a file (a Project/Blogs image, a brochure, an upload_media_to_r2 run)
— rather than at process startup. This keeps commands that never touch media
(migrate, createsuperuser, shell, dumpdata/loaddata, ...) working even before
Cloudflare R2 has been configured in .env.
"""

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from storages.backends.s3 import S3Storage


class R2MediaStorage(S3Storage):
    def __init__(self, *args, **kwargs):
        required = {
            "R2_ACCESS_KEY_ID": settings.AWS_ACCESS_KEY_ID,
            "R2_SECRET_ACCESS_KEY": settings.AWS_SECRET_ACCESS_KEY,
            "R2_BUCKET_NAME": settings.AWS_STORAGE_BUCKET_NAME,
            "R2_ENDPOINT_URL": settings.AWS_S3_ENDPOINT_URL,
            "R2_PUBLIC_DOMAIN": settings.AWS_S3_CUSTOM_DOMAIN,
        }
        missing = [name for name, value in required.items() if not value]

        if missing:
            raise ImproperlyConfigured(
                f"Missing Cloudflare R2 environment variable(s): {', '.join(missing)}. "
                f"Copy .env.example to .env in sreemr-home-django/ and fill in your R2 "
                f"credentials — see the comments there for exactly where to find each "
                f"value in the Cloudflare dashboard. (Commands like migrate, "
                f"createsuperuser, and dumpdata don't need this — only file "
                f"upload/download does.)"
            )

        super().__init__(*args, **kwargs)
