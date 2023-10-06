from django.urls import path
from texts.views import *

urlpatterns = [
    path("<int:text_id>/update/", TextUpdateView.as_view()),
    path("<int:text_id>/delete/", TextDeleteView.as_view()),
    path("<int:pk>/", TextDetailAPIView.as_view()),
    path("user/", TextListView.as_view(), name="paginated-text-list"),
    path("create/", TextCreateView.as_view()),
]
