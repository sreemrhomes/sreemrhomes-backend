"""
One-time migration helper: uploads every file in the local media/ folder to
the Cloudflare R2 bucket configured in settings (STORAGES["default"]),
preserving the same relative paths (e.g. "projects/xyz.jpg").

Existing Project/Blogs/ShootBooking rows already store that relative path in
their ImageField/FileField (e.g. "projects/xyz.jpg"), so once those files
exist at the same path in R2, .image.url keeps resolving correctly with zero
database changes needed.

Usage (run from sreemr-home-django/, with .env filled in and the venv active):
    python manage.py upload_media_to_r2 --dry-run   # preview only
    python manage.py upload_media_to_r2             # actually upload
"""

from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import storages
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Uploads the local media/ folder to the configured Cloudflare R2 bucket."

    def add_arguments(self, parser):
        parser.add_argument(
            "--source",
            default=str(settings.BASE_DIR / "media"),
            help="Local folder to upload from (default: sreemr-home-django/media).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="List what would be uploaded/skipped without uploading anything.",
        )

    def handle(self, *args, **options):
        source = Path(options["source"])
        dry_run = options["dry_run"]

        if not source.exists():
            self.stderr.write(self.style.ERROR(f"Source folder not found: {source}"))
            return

        files = sorted(p for p in source.rglob("*") if p.is_file())

        if not files:
            self.stdout.write("No files found under " + str(source))
            return

        storage = storages["default"]

        uploaded = skipped = failed = 0

        for path in files:
            relative_path = path.relative_to(source).as_posix()

            try:
                already_there = storage.exists(relative_path)
            except Exception as exc:  # noqa: BLE001 - surface any R2/auth error clearly
                self.stderr.write(
                    self.style.ERROR(
                        f"Could not reach R2 while checking '{relative_path}': {exc}"
                    )
                )
                failed += 1
                continue

            if already_there:
                self.stdout.write(f"SKIP (already on R2): {relative_path}")
                skipped += 1
                continue

            if dry_run:
                self.stdout.write(f"WOULD UPLOAD: {relative_path} ({path.stat().st_size} bytes)")
                continue

            try:
                with open(path, "rb") as fh:
                    storage.save(relative_path, ContentFile(fh.read()))
                self.stdout.write(self.style.SUCCESS(f"Uploaded: {relative_path}"))
                uploaded += 1
            except Exception as exc:  # noqa: BLE001
                self.stderr.write(self.style.ERROR(f"FAILED: {relative_path} -> {exc}"))
                failed += 1

        if dry_run:
            self.stdout.write(f"\nDry run complete. {len(files)} local file(s) inspected.")
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nDone. Uploaded {uploaded}, skipped {skipped} (already on R2), "
                    f"{failed} failed."
                )
            )
            if failed:
                self.stdout.write(
                    self.style.WARNING(
                        "Some files failed — check your R2 credentials/bucket name in .env "
                        "and re-run the command (already-uploaded files will be skipped)."
                    )
                )
