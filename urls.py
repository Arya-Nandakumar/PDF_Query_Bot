from django.urls import path
from faqbot.views import FileUploadView
from django.conf import settings
from django.conf.urls.static import static
from .views import ChatBotView

urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('handle_message/', ChatBotView.as_view(), name='handle_message'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
