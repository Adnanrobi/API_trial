from django.db import models

# Create your models here.
from django.db import models
from accounts.models import User

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

import os


def custom_file_upload_path(instance, filename):
    # Define a custom upload path for files
    return f"ticket_files/{filename}"


# Custom validator to check file size
def validate_file_size(value):
    max_file_size = 4 * 1024 * 1024  # 4MB in bytes
    if value.size > max_file_size:
        raise ValidationError(_("File size exceeds the maximum limit of 4MB."))


# Create your models here.
class Ticket(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField()
    # FileField for multiple files
    files = models.FileField(
        upload_to=custom_file_upload_path,
        validators=[validate_file_size],
        blank=True,
        null=True,
    )
    is_open = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, db_column="timestamp")
    updated_at = models.DateTimeField(auto_now=True)
    opened_by_med_id = models.IntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Handle multiple files (if needed)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Delete associated files from the "uploads" folder
        if self.files:
            file_path = os.path.join(settings.MEDIA_ROOT, self.files.name)
            if os.path.exists(file_path):
                print(f"Deleting file: {file_path}")  # Debugging statement
                os.remove(file_path)
            else:
                print(f"File not found: {file_path}")  # Debugging statement
        else:
            print("self.files is none")  # Debugging statement

        # Call the parent class's delete method to delete the database record
        super().delete(*args, **kwargs)


# Create your models here.
class TicketFollowUp(models.Model):
    root = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    sequence_number = models.IntegerField()
    is_medUser = models.BooleanField()
    description = models.TextField()
    # FileField for multiple files
    files = models.FileField(
        upload_to=custom_file_upload_path,
        validators=[validate_file_size],
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, db_column="timestamp")
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Calculate the sequence number based on the 'root' field and existing records
        if not self.sequence_number:
            last_record = (
                TicketFollowUp.objects.filter(root=self.root)
                .order_by("-sequence_number")
                .first()
            )
            if last_record:
                self.sequence_number = last_record.sequence_number + 1
            else:
                self.sequence_number = 1
        # super(TicketFollowUp, self).save(*args, **kwargs)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Delete associated files from the "uploads" folder
        if self.files:
            file_path = os.path.join(settings.MEDIA_ROOT, self.files.name)
            if os.path.exists(file_path):
                print(f"Deleting file: {file_path}")  # Debugging statement
                os.remove(file_path)
            else:
                print(f"File not found: {file_path}")  # Debugging statement
        else:
            print("self.files is none")  # Debugging statement

        # Call the parent class's delete method to delete the database record
        super().delete(*args, **kwargs)
