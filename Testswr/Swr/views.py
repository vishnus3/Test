from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import CursorPagination
from django.db.models import Q
from django.db import transaction, IntegrityError

from .models import Employee
from .serializers import EmployeeSerializer

class EmployeeCursorPagination(CursorPagination):
    page_size = 10
    ordering = "-created_at"


class EmployeeListCreateAPI(APIView):
    pagination_class = EmployeeCursorPagination

    def get(self, request):
        search = request.query_params.get("search")

        qs = Employee.objects.only(
            "id",
            "first_name",
            "last_name",
            "email",
            "mobile",
            "role",
            "created_at"
        )

        if search:
            qs = qs.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )

        qs = qs.order_by("-created_at")

        paginator = self.pagination_class()
        paginated_qs = paginator.paginate_queryset(qs, request, view=self)

        serializer = EmployeeSerializer(paginated_qs, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        data = request.data.copy()

        # Normalize
        data["first_name"] = str(data.get("first_name", "")).strip()
        data["last_name"] = str(data.get("last_name", "")).strip()
        data["email"] = str(data.get("email", "")).strip().lower()
        data["mobile"] = str(data.get("mobile", "")).strip()
        data["role"] = str(data.get("role", "")).strip()

        serializer = EmployeeSerializer(data=data)

        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                employee = serializer.save()
        except IntegrityError:
            return Response(
                {"message": "Employee with this email already exists"},
                status=status.HTTP_409_CONFLICT
            )

        return Response(
            EmployeeSerializer(employee).data,
            status=status.HTTP_201_CREATED
        )


class EmployeeDetailAPI(APIView):

    def get_object(self, id):
        return Employee.objects.filter(id=id).first()

    def get(self, request, id):
        employee = Employee.objects.only(
            "id",
            "first_name",
            "last_name",
            "email",
            "mobile",
            "role",
            "created_at"
        ).filter(id=id).first()

        if not employee:
            return Response({"error": "Not found"}, status=404)

        return Response(EmployeeSerializer(employee).data)

    def put(self, request, id):
        employee = self.get_object(id)
        if not employee:
            return Response({"error": "Not found"}, status=404)

        data = request.data.copy()

        # Full update (PUT = replace)
        required_fields = ["first_name", "last_name", "email", "mobile", "role"]
        for field in required_fields:
            if field not in data:
                return Response(
                    {"error": f"{field} is required for full update"},
                    status=400
                )

        data["email"] = str(data.get("email")).strip().lower()

        serializer = EmployeeSerializer(employee, data=data)

        if serializer.is_valid():
            try:
                with transaction.atomic():
                    serializer.save()
            except IntegrityError:
                return Response(
                    {"message": "Email already exists"},
                    status=409
                )

            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    def delete(self, request, id):
        employee = self.get_object(id)
        if not employee:
            return Response({"error": "Not found"}, status=404)

        employee.delete()
        return Response({"message": "Deleted successfully"}, status=200)

