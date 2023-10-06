from rest_framework import generics
from rest_framework import status
from .models import Text
from .serializers import TextSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework import generics
from django.db.models import F
from accounts.serializers import OnlyUserProfileSerializer
from .serializers import *
from .models import *
from rest_framework.permissions import IsAuthenticated


class TextCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = OnlyUserProfileSerializer(request.user)
        if not serializer["is_med_user"].value:
            user_id = serializer["id"].value
            # Serialize the RegUser data
            data = request.data.copy()
            data["user_id"] = user_id

            serializer = TextSerializer(data=data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(
                {"detail": "Access Denied"}, status=status.HTTP_403_FORBIDDEN
            )


class TextUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, text_id, format=None):
        serializer = OnlyUserProfileSerializer(request.user)
        if not serializer["is_med_user"].value:
            try:
                text = Text.objects.get(pk=text_id)
            except Text.DoesNotExist:
                return Response(
                    {"error": "Text not found."}, status=status.HTTP_404_NOT_FOUND
                )

            user_id = serializer["id"].value
            if text.user_id != user_id:
                return Response(
                    {"error": "User cannot update."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Create the serializer with partial=True to allow partial updates
            serializer = TextSerializer(text, data=request.data, partial=True)

            if serializer.is_valid(raise_exception=True):
                instance = serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"detail": "Access Denied"}, status=status.HTTP_403_FORBIDDEN
            )


class TextDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, text_id, format=None):
        # Check if the user exists
        serializer = OnlyUserProfileSerializer(request.user)

        if not serializer["is_med_user"].value:
            # Check if the ticket exists
            try:
                text = Text.objects.get(pk=text_id)
            except Text.DoesNotExist:
                return Response(
                    {"error": "Text not found."}, status=status.HTTP_404_NOT_FOUND
                )

            # Ensure that the user is the owner of the ticket (if needed)
            user_id = serializer["id"].value
            if text.user_id != user_id:
                return Response(
                    {"error": "User cannot delete"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            text = Text.objects.get(pk=text_id)

            print("OK")
            text.delete()
            return Response(
                {"message": "Text deleted."}, status=status.HTTP_204_NO_CONTENT
            )
        else:
            return Response(
                {"detail": "Access Denied"}, status=status.HTTP_403_FORBIDDEN
            )


class CustomPagination(PageNumberPagination):
    page_size_query_param = "perpage"  # Set the query parameter for page size


class TextListView(ListAPIView):
    queryset = Text.objects.all()
    serializer_class = TextSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        serializer = OnlyUserProfileSerializer(self.request.user)
        user_id = serializer.data["id"]
        queryset = (
            Text.objects.filter(user_id=user_id)
            .annotate(timestamp=F("created_at"))
            .order_by("-timestamp")
        )

        # Assuming queryset is a list of objects, and each object has a 'results' attribute

        # queryset.reverse()
        print(queryset)
        return queryset


class TextDetailAPIView(generics.RetrieveAPIView):
    queryset = Text.objects.all()
    serializer_class = TextSerializer
