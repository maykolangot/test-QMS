import csv
from django.core.management.base import BaseCommand
from core.models import TransactionNF1
from django.utils.timezone import localtime

class Command(BaseCommand):
    help = "Exports all TransactionNF1 entries to a CSV file."

    def handle(self, *args, **options):
        file_path = "nf1_transactions_export.csv"
        
        fields = [
            "id",
            "queueNumber",
            "transactionType",
            "status",
            "priority",
            "onHoldCount",
            "created_at",
            "updated_at",
            "requester_type",
            "requester_id",
            "course_id",
            "campus",
            "transaction_for",
            "reservedBy_id",
        ]

        with open(file_path, mode="w", newline='', encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(fields)

            for tx in TransactionNF1.objects.select_related(
                "student", "new_enrollee", "guest", "reservedBy", "course"
            ).all():
                requester = tx.get_requester()
                requester_type = (
                    "Student" if tx.student else
                    "NewEnrollee" if tx.new_enrollee else
                    "Guest" if tx.guest else
                    "None"
                )

                row = [
                    tx.id,
                    tx.queueNumber,
                    tx.transactionType,
                    tx.get_status_display(),  # human-readable
                    tx.priority,
                    tx.onHoldCount,
                    localtime(tx.created_at).isoformat(),
                    localtime(tx.updated_at).isoformat(),
                    requester_type,
                    requester.id if requester else "",
                    tx.course.id if tx.course else "",
                    tx.get_campus_display() if hasattr(tx, 'get_campus_display') else tx.campus,
                    tx.get_transaction_for_display(),
                    tx.reservedBy.id if tx.reservedBy else "",
                ]
                writer.writerow(row)

        self.stdout.write(self.style.SUCCESS(f"Export complete: {file_path}"))
