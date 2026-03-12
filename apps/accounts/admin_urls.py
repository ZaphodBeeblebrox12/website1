"""
URL configuration for accounts app (admin endpoints).
"""
from django.urls import path

from .views import (
    ban_user,
    staff_approval_action,
    staff_approvals_list,
    unban_user,
)

urlpatterns = [
    path("staff-approvals/", staff_approvals_list, name="staff-approvals-list"),
    path("staff-approvals/action/", staff_approval_action, name="staff-approval-action"),
    path("ban/", ban_user, name="ban-user"),
    path("unban/", unban_user, name="unban-user"),
]
