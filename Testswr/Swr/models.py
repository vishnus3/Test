from django.db import models
from django.db.models import Index
from django.db.models.functions import Lower


class Employee(models.Model):
    first_name = models.CharField(max_length=120, db_index=True)
    last_name = models.CharField(max_length=120, db_index=True)
    email = models.EmailField(unique=True, db_index=True)
    mobile = models.CharField(max_length=15, db_index=True)
    role = models.CharField(max_length=120, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "employees"

        indexes = [
            # Composite index for full name searches
            Index(fields=["first_name", "last_name"], name="emp_name_idx"),

            # Fast sorting + recent records
            Index(fields=["-created_at"], name="emp_created_idx"),

            # Case-insensitive email search
            Index(Lower("email"), name="emp_email_lower_idx"),

            # Case-insensitive name search
            Index(Lower("first_name"), name="emp_fname_lower_idx"),
            Index(Lower("last_name"), name="emp_lname_lower_idx"),
        ]

        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
