from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now
from core.models import Student, Transaction, Guest, NewEnrollee, TransactionNF1, Course
from .forms import StudentRegistrationForm, NewEnrolleeForm, GuestForm, QueueRequestForm
from .utils import generate_qr_id
from django.shortcuts import get_object_or_404
from django.urls import reverse
import qrcode
import io
from django.core.mail import EmailMessage
from django.http import JsonResponse

def register_student(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            student.qrId = generate_qr_id()
            student.save()

            # Generate QR code
            qr = qrcode.make(student.qrId)
            buffer = io.BytesIO()
            qr.save(buffer, format='PNG')
            buffer.seek(0)

            # Create email with QR image attachment
            email = EmailMessage(
                subject='Your Student QR Code',
                body=f'Hi {student.name},\n\nThank you for registering. Attached is your QR code.',
                from_email='noreply@phinmaed.com',
                to=[student.email],
            )
            email.attach('qr.png', buffer.read(), 'image/png')
            email.send(fail_silently=False)

            messages.success(request, "Student registered successfully! QR code sent via email.")
            return redirect(reverse('student_success', args=[student.id]))
    else:
        form = StudentRegistrationForm()
    
    return render(request, 'request/register_student.html', {'form': form})


def student_success(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    return render(request, 'request/student_success.html', {'student': student})



'''

-------------------------------             Guest and New Enrollees Temporary           ------------------------------------------

'''


# 📧 This is where all notifications go
NOTIFY_EMAIL = 'michael.magdosa.au@phinmaed.com'

def register_new_enrollee(request):
    if request.method == 'POST':
        form = NewEnrolleeForm(request.POST)
        if form.is_valid():
            enrollee = form.save(commit=False)
            enrollee.qrId = generate_qr_id()
            enrollee.save()

            # Generate QR code image
            qr = qrcode.make(enrollee.qrId)
            buffer = io.BytesIO()
            qr.save(buffer, format='PNG')
            buffer.seek(0)

            # Email with QR code image
            email = EmailMessage(
                subject='New Enrollee Registered',
                body=f'A new enrollee has registered:\n\n'
                     f'Department: {enrollee.department}\n'
                     f'Priority: {enrollee.priority}\n'
                     f'QR ID: {enrollee.qrId}',
                from_email='noreply@phinmaed.com',
                to=[NOTIFY_EMAIL],
            )
            email.attach('enrollee_qr.png', buffer.read(), 'image/png')
            email.send(fail_silently=False)

            messages.success(request, "New enrollee registered. QR code sent via email.")
            return redirect('register_new_enrollee')
    else:
        form = NewEnrolleeForm()

    return render(request, 'request/new_enrollee_form.html', {'form': form})


def register_guest(request):
    if request.method == 'POST':
        form = GuestForm(request.POST)
        if form.is_valid():
            guest = form.save(commit=False)
            guest.qrId = generate_qr_id()
            guest.save()

            # Generate QR code
            qr = qrcode.make(guest.qrId)
            buffer = io.BytesIO()
            qr.save(buffer, format='PNG')
            buffer.seek(0)

            email = EmailMessage(
                subject='New Guest Registered',
                body=f'A guest has registered:\n\n'
                     f'Department: {guest.department}\n'
                     f'Course: {guest.course}\n'
                     f'QR ID: {guest.qrId}',
                from_email='noreply@phinmaed.com',
                to=[NOTIFY_EMAIL],
            )
            email.attach('guest_qr.png', buffer.read(), 'image/png')
            email.send(fail_silently=False)

            messages.success(request, "Guest registered. QR code sent via email.")
            return redirect('register_guest')
    else:
        form = GuestForm()

    return render(request, 'request/guest_form.html', {'form': form})


'''
-------------------------------------       Request Queue Number        -------------------------------------
'''
def generate_queue_number(priority: bool):
    prefix = 'P' if priority else 'S'
    count = Transaction.objects.filter(priority=priority).count() + 1
    return f"{prefix}-{count:04d}"

"""
def request_queue(request):
    if request.method == 'POST':
        form = QueueRequestForm(request.POST)
        if form.is_valid():
            qr_id = form.cleaned_data['qrId']
            transaction_type = form.cleaned_data['transactionType']
            today = now().date()

            # Search in all requester models
            requester = None
            model = None

            for model_class in [Student, Guest, NewEnrollee]:
                try:
                    requester = model_class.objects.get(qrId=qr_id)
                    model = model_class
                    break
                except model_class.DoesNotExist:
                    continue

            if not requester:
                messages.error(request, "QR ID not found.")
                return redirect('request_queue')

            # Enforce rules for Students
            if isinstance(requester, Student):
                student_txn = Transaction.objects.filter(
                    requester_type=ContentType.objects.get_for_model(Student),
                    requester_id=requester.pk,
                    status__in=[Transaction.Status.ON_QUEUE, Transaction.Status.IN_PROCESS]
                ).order_by('-id').first()

                if student_txn and student_txn.created_at.date() == today:
                    messages.error(request, "Student already in queue today.")
                    return redirect('request_queue')

            # Determine priority
            is_priority = getattr(requester, 'priority', False)

            # Generate queue number
            queue_number = generate_queue_number(is_priority)

            txn = Transaction.objects.create(
                queueNumber=queue_number,
                transactionType=transaction_type,  # <- from form input
                status=Transaction.Status.ON_QUEUE,
                priority=is_priority,
                requester_type=ContentType.objects.get_for_model(model),
                requester_id=requester.pk,
            )

            messages.success(request, f"Transaction created: {txn.queueNumber}")
            return redirect('request_queue')

    else:
        form = QueueRequestForm()

    return render(request, 'request/request_queue.html', {'form': form})

"""
def load_courses(request):
    department_id = request.GET.get('department_id')
    courses = Course.objects.filter(department_id=department_id).order_by('name')
    return JsonResponse(list(courses.values('id', 'name')), safe=False)


def request_queue(request):
    if request.method == 'POST':
        form = QueueRequestForm(request.POST)
        if form.is_valid():
            qr_id = form.cleaned_data['qrId']
            transaction_type = form.cleaned_data['transactionType']
            today = now().date()

            requester = None
            for model_class in [Student, Guest, NewEnrollee]:
                try:
                    requester = model_class.objects.get(qrId=qr_id)
                    break
                except model_class.DoesNotExist:
                    continue

            if not requester:
                messages.error(request, "QR ID not found.")
                return redirect('request_queue')

            existing_txn = TransactionNF1.objects.filter(
                student_id=getattr(requester, 'id', None) if isinstance(requester, Student) else None,
                new_enrollee_id=getattr(requester, 'id', None) if isinstance(requester, NewEnrollee) else None,
                guest_id=getattr(requester, 'id', None) if isinstance(requester, Guest) else None,
                status__in=[TransactionNF1.Status.ON_QUEUE, TransactionNF1.Status.IN_PROCESS],
                created_at__date=today
            ).first()

            if existing_txn:
                messages.error(request, "Requester already has a transaction today.")
                return redirect('request_queue')

            queue_number = generate_queue_number(getattr(requester, 'priority', False))

            # Create TransactionNF1
            txn_nf1 = TransactionNF1.create_from_requester(
                requester=requester,
                transaction_type=transaction_type,
                queue_number=queue_number
            )

            # Create legacy Transaction
            Transaction.objects.create(
                queueNumber=txn_nf1.queueNumber,
                transactionType=txn_nf1.transactionType,
                status=txn_nf1.status,
                priority=txn_nf1.priority,
                onHoldCount=txn_nf1.onHoldCount,
                created_at=txn_nf1.created_at,
                reservedBy=txn_nf1.reservedBy,
                student=txn_nf1.student,
                new_enrollee=txn_nf1.new_enrollee,
                guest=txn_nf1.guest,
            )

            messages.success(request, f"Transaction created: {txn_nf1.queueNumber}")
            return redirect('request_queue')
    else:
        form = QueueRequestForm()

    return render(request, 'request/request_queue.html', {'form': form})