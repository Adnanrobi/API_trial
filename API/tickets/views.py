from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .serializers import *
from .models import *
from accounts.models import *
from accounts.serializers import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404


##### TICKET VIEWS #####


class TicketCreateView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = OnlyUserProfileSerializer(request.user)
        if not serializer["is_med_user"].value:
            user_id = serializer["id"].value
            # Serialize the RegUser data
            data = request.data.copy()
            data["creator_id"] = user_id
            data["is_open"] = True

            serializer = TicketSerializer(data=data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(
                {"detail": "Access Denied"}, status=status.HTTP_403_FORBIDDEN
            )


class TicketUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, ticket_id, format=None):
        serializer = OnlyUserProfileSerializer(request.user)
        if not serializer["is_med_user"].value:
            # Check if the ticket exists
            try:
                ticket = Ticket.objects.get(pk=ticket_id)
            except Ticket.DoesNotExist:
                return Response(
                    {"error": "Ticket not found."}, status=status.HTTP_404_NOT_FOUND
                )

            user_id = serializer["id"].value
            # Ensure that the user is the owner of the ticket (if needed)
            if ticket.creator_id != user_id:
                return Response(
                    {"error": "User does not own this ticket."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Create the serializer with partial=True to allow partial updates
            serializer = TicketUpdateSerializer(ticket, data=request.data, partial=True)

            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"detail": "Access Denied"}, status=status.HTTP_403_FORBIDDEN
            )


class TicketDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, ticket_id, format=None):
        # Check if the user exists
        serializer = OnlyUserProfileSerializer(request.user)

        if not serializer["is_med_user"].value:
            # Check if the ticket exists
            try:
                ticket = Ticket.objects.get(pk=ticket_id)
            except Ticket.DoesNotExist:
                return Response(
                    {"error": "Ticket not found."}, status=status.HTTP_404_NOT_FOUND
                )

            # Ensure that the user is the owner of the ticket (if needed)
            user_id = serializer["id"].value
            if ticket.creator_id != user_id:
                return Response(
                    {"error": "User does not own this ticket."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            ticket = Ticket.objects.get(pk=ticket_id)
            # Delete the associated files (assuming a FileField named 'attachment')
            if ticket.files:
                ticket.files.delete(save=True)
            ticket.delete()
            return Response(
                {"message": "Ticket deleted."}, status=status.HTTP_204_NO_CONTENT
            )
        else:
            return Response(
                {"detail": "Access Denied"}, status=status.HTTP_403_FORBIDDEN
            )


class RegUserTicketListView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get(self, request):
        serializer = OnlyUserProfileSerializer(request.user)

        if not serializer["is_med_user"].value:
            user_id = serializer["id"].value
            tickets = Ticket.objects.filter(creator_id=user_id)

            paginator = PageNumberPagination()
            paginator.page_size = 10  # Set the number of items per page

            page = paginator.paginate_queryset(tickets, request)

            # Serialize the paginated data
            serializer = TicketSerializer(page, many=True)

            # Return the paginated response
            return paginator.get_paginated_response(serializer.data)

        else:
            return Response(
                {"error": "Access Denied"}, status=status.HTTP_404_NOT_FOUND
            )


##### MED-USER TICKET VIEWS #####


class MedUserOpenTicketListView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get(self, request):
        serializer = OnlyUserProfileSerializer(request.user)
        if serializer["is_med_user"].value:
            tickets = Ticket.objects.filter(
                is_open=True
            )  # only showing the opened ticket to med_user

            paginator = PageNumberPagination()
            paginator.page_size = 10  # Set the number of items per page

            page = paginator.paginate_queryset(tickets, request)

            # Serialize the paginated data
            serializer = TicketSerializer(page, many=True)

            # Return the paginated response
            return paginator.get_paginated_response(serializer.data)
        else:
            return Response(
                {"error": "Access Denied"}, status=status.HTTP_403_FORBIDDEN
            )


class MedUserCloseTicketListView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get(self, request):
        serializer = OnlyUserProfileSerializer(request.user)
        if serializer["is_med_user"].value:
            tickets = Ticket.objects.filter(
                opened_by_med_id=serializer["id"].value
            )  # only showing the opened ticket to med_user

            paginator = PageNumberPagination()
            paginator.page_size = 10  # Set the number of items per page

            page = paginator.paginate_queryset(tickets, request)

            # Serialize the paginated data
            serializer = TicketSerializer(page, many=True)

            # Return the paginated response
            return paginator.get_paginated_response(serializer.data)
        else:
            return Response(
                {"error": "Access Denied"}, status=status.HTTP_403_FORBIDDEN
            )


##### FOLLOWUP TICKETS VIEW #####


class TicketFollowupCreateView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def post(self, request, ticket_id, format=None):
        serializer = OnlyUserProfileSerializer(request.user)
        user_id = serializer["id"].value

        ticket = get_object_or_404(Ticket, pk=ticket_id)

        if ticket.is_open:
            # only medical user can open a ticket
            if serializer["is_med_user"].value:
                # Serialize the RegUser data
                data = request.data.copy()
                data["creator_id"] = user_id
                data["root"] = ticket_id
                data["is_medUser"] = serializer["is_med_user"].value

                serializer = TicketFollowUpSerializer(data=data)

                if serializer.is_valid():
                    serializer.save()
                    ticket.is_open = False
                    ticket.opened_by_med_id = user_id
                    ticket.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response(
                        serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )

            else:
                return Response(
                    {"detail": "Access Denied"}, status=status.HTTP_403_FORBIDDEN
                )
        else:
            check_root_user = ticket.creator_id == user_id
            check_assigned_med_user = user_id == ticket.opened_by_med_id
            if check_assigned_med_user or check_root_user:
                # Serialize the User data
                data = request.data.copy()
                data["creator_id"] = user_id
                data["root"] = ticket.id
                data["is_medUser"] = serializer["is_med_user"].value

                serializer = TicketFollowUpSerializer(data=data)

                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response(
                        serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )

            else:
                return Response(
                    {"detail": "Not allowed to follow-up"},
                    status=status.HTTP_400_BAD_REQUEST,
                )


class TicketFollowupUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, ticket_fu_id, format=None):
        serializer = OnlyUserProfileSerializer(request.user)
        # Check if the ticket exists
        try:
            ticket_fu = TicketFollowUp.objects.get(pk=ticket_fu_id)
        except TicketFollowUp.DoesNotExist:
            return Response(
                {"error": "Ticket not found."}, status=status.HTTP_404_NOT_FOUND
            )

        user_id = serializer["id"].value
        # Ensure that the user is the owner of the ticket (if needed)
        if ticket_fu.creator_id != user_id:
            return Response(
                {"error": "User does not own this ticket."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Create the serializer with partial=True to allow partial updates
        serializer = TicketFollowupUpdateSerializer(
            ticket_fu, data=request.data, partial=True
        )

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TicketFollowupDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, ticket_fu_id, format=None):
        # Check if the user exists
        serializer = OnlyUserProfileSerializer(request.user)

        # Check if the ticket exists
        try:
            ticket_fu = TicketFollowUp.objects.get(pk=ticket_fu_id)
        except TicketFollowUp.DoesNotExist:
            return Response(
                {"error": "Ticket not found."}, status=status.HTTP_404_NOT_FOUND
            )

        # Ensure that the user is the owner of the ticket (if needed)
        user_id = serializer["id"].value
        if ticket_fu.creator_id != user_id:
            return Response(
                {"error": "Access Denied"},
                status=status.HTTP_403_FORBIDDEN,
            )

        ticket_fu = TicketFollowUp.objects.get(pk=ticket_fu_id)
        # Delete the associated files (assuming a FileField named 'attachment')
        if ticket_fu.files:
            ticket_fu.files.delete(save=True)
        ticket_fu.delete()
        return Response(
            {"message": "Ticket deleted."}, status=status.HTTP_204_NO_CONTENT
        )


##### THIS LIST VIEW FOR BOTH REG-USER(CREATED_BY) AND MED-USER(OPENED BY) #####
class TicketFollowupListView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get(self, request, ticket_id):
        serializer = OnlyUserProfileSerializer(request.user)
        user_id = serializer["id"].value
        try:
            ticket = Ticket.objects.get(pk=ticket_id)
        except Ticket.DoesNotExist:
            return Response(
                {"error": "Ticket not found."}, status=status.HTTP_404_NOT_FOUND
            )

        # Ensure that the user is the owner of the ticket (if needed)
        user_id = serializer["id"].value
        if ticket.creator_id != user_id and ticket.opened_by_med_id != user_id:
            return Response(
                {"error": "Access Denied"},
                status=status.HTTP_403_FORBIDDEN,
            )

        tickets = TicketFollowUp.objects.filter(root=ticket_id).order_by(
            "-sequence_number"
        )

        paginator = PageNumberPagination()
        paginator.page_size = 10  # Set the number of items per page

        page = paginator.paginate_queryset(tickets, request)

        # Serialize the paginated data
        followup_serializer = TicketFollowUpSerializer(page, many=True)
        ticket_serializer = TicketSerializer(
            ticket
        )  # You might need to adjust this serializer
        response_data = {
            "ticket_details": ticket_serializer.data,
            "followup_data": followup_serializer.data,
        }
        # Return the paginated response
        return paginator.get_paginated_response(response_data)
