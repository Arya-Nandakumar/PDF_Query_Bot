from django.db import models
import uuid
from django.utils import timezone

# Model for file upload
class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    session_id = models.CharField(max_length=255, default=uuid.uuid4)

# Model to save the PDF content
class PDFContent(models.Model):
    session_id = models.CharField(max_length=255, default=uuid.uuid4)
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_on = models.DateTimeField(auto_now=True)
    created_by = models.IntegerField(default=1)
    updated_on = models.DateTimeField(auto_now=True)
    updated_by = models.IntegerField(default=1)


    def save(self, *args, **kwargs):
        if not self.created_on:
            self.created_on = timezone.now()
        self.updated_on = timezone.now()
        return super().save(*args, **kwargs)



    def __str__(self):
        return f'{self.session_id} - {self.file.name}'

class MessagesHistory(models.Model):
    session_id = models.CharField(max_length=255, default=uuid.uuid4)
    text = models.JSONField()
    created_on = models.DateTimeField(auto_now=True)
    created_by = models.IntegerField(default=1)
    updated_on = models.DateTimeField(auto_now=True)
    updated_by = models.IntegerField(default=1)


    def __str__(self):
        return f"{self.type} Message - {self.created_on}"




