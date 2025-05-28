import csv
from django.core.management.base import BaseCommand
from core.models import Student
from django.utils.timezone import localtime

class Command(BaseCommand):
    help = "Exports all Student records to a CSV file."

    def handle(self, *args, **options):
        file_path = "students_export.csv"

        fields = [
            "id",
            "name",
            "studentId",
            "email",
            "roles",
            "priority_request",
            "priority",
            "course_id",
            "campus",
            "qrId",
            "year_level",
            "dateCreated"
        ]

        with open(file_path, mode="w", newline='', encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(fields)

            for student in Student.objects.select_related("course").all():
                row = [
                    student.id,
                    student.name,
                    student.studentId,
                    student.email,
                    student.roles,
                    student.priority_request,
                    student.priority,
                    student.course.id if student.course else "",
                    student.campus,
                    student.qrId,
                    student.get_year_level_display(),
                    localtime(student.dateCreated).isoformat()
                ]
                writer.writerow(row)

        self.stdout.write(self.style.SUCCESS(f"Student export complete: {file_path}"))
