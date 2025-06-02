from django.urls import path
from .views import (
    register_student,
    student_success,
    register_new_enrollee,
    register_guest,
    request_queue,
    load_courses,
    register_view,
    index,
    live_queue_status,
    live_queue_page, public_next_queues,
    recover_qr
    )

urlpatterns = [
    path('ajax/load-courses/', load_courses, name='ajax_load_courses'),
    path('student_register/', register_student, name='register_student'),
    path('student/success/<int:student_id>/', student_success, name='student_success'),
    path('student/recover_qr/', recover_qr, name='recover_qr'),

    path('new-enrollee/', register_new_enrollee, name='register_new_enrollee'),
    path('guest/', register_guest, name='register_guest'),
    path('queue-request/', request_queue, name='request_queue'),
    path('cashier_register/',register_view, name='register'),
    path('', index, name='index'),
    path("live-queue/", live_queue_status, name="live-queue-status"),
    path("live-queue-page/", live_queue_page, name="live-queue-page"),
    path("public-next-queues/", public_next_queues, name="public-next-queues"),



]
