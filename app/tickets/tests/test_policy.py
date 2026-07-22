import pytest
from django.contrib.auth.models import User, Group
from tickets.policy import can_comment, can_create, can_assign, is_agent_user, can_change_due, can_update_status, can_view, check_status_change
from tickets.models import Ticket, TicketStatus

@pytest.mark.django_db
@pytest.mark.parametrize("group_name, expected", [
    ("Admin",     False),
    ("Agent",     False),
    ("Requester", True),
])
def test_can_create_by_role(group_name, expected):
    user = User.objects.create_user(username="A")
    user.groups.add(Group.objects.create(name=group_name))
    assert can_create(user) == expected   

@pytest.mark.django_db
@pytest.mark.parametrize("group_name, expected", [
    ("Admin",     False),
    ("Agent",     False),
    ("Requester", True),
])
def test_can_create_by_role(group_name, expected):
    user = User.objects.create_user(username="A")
    user.groups.add(Group.objects.create(name=group_name))
    assert can_create(user) == expected   

@pytest.mark.django_db
@pytest.mark.parametrize("group_name, expected", [
    ("Admin",     True),
    ("Agent",     False),
    ("Requester", False),
])
def test_can_assign_by_role(group_name, expected):
    user = User.objects.create_user(username="A")
    user.groups.add(Group.objects.create(name=group_name))
    assert can_assign(user) == expected

@pytest.mark.django_db
@pytest.mark.parametrize("group_name, expected", [
    ("Admin",     False),
    ("Agent",     True),
    ("Requester", False),
])
def test_is_agent_user(group_name, expected):
    user = User.objects.create_user(username="A")
    user.groups.add(Group.objects.create(name=group_name))
    assert is_agent_user(user) == expected

@pytest.mark.django_db
@pytest.mark.parametrize("group_name, expected", [
    ("Admin",     True),
    ("Agent",     False),
    ("Requester", False),
])
def test_can_change_due_by_role(group_name, expected):
    user = User.objects.create_user(username="A")
    user.groups.add(Group.objects.create(name=group_name))
    assert can_change_due(user) == expected

S = TicketStatus

@pytest.mark.parametrize("current, target, expected", [
    # --- from OPEN ---
    (S.OPEN,        S.OPEN,        False),
    (S.OPEN,        S.IN_PROGRESS, True),
    (S.OPEN,        S.PENDING,     True),
    (S.OPEN,        S.RESOLVED,    False),
    (S.OPEN,        S.CLOSED,      False),
    # --- from IN_PROGRESS ---
    (S.IN_PROGRESS, S.OPEN,        False),
    (S.IN_PROGRESS, S.IN_PROGRESS, False),
    (S.IN_PROGRESS, S.PENDING,     True),
    (S.IN_PROGRESS, S.RESOLVED,    True),
    (S.IN_PROGRESS, S.CLOSED,      False),
    # --- from PENDING ---
    (S.PENDING,     S.OPEN,        False),
    (S.PENDING,     S.IN_PROGRESS, True),
    (S.PENDING,     S.PENDING,     False),
    (S.PENDING,     S.RESOLVED,    False),
    (S.PENDING,     S.CLOSED,      False),
    # --- from RESOLVED ---
    (S.RESOLVED,    S.OPEN,        False),
    (S.RESOLVED,    S.IN_PROGRESS, False),
    (S.RESOLVED,    S.PENDING,     False),
    (S.RESOLVED,    S.RESOLVED,    False),
    (S.RESOLVED,    S.CLOSED,      True),
    # --- from CLOSED（終端）---
    (S.CLOSED,      S.OPEN,        False),
    (S.CLOSED,      S.IN_PROGRESS, False),
    (S.CLOSED,      S.PENDING,     False),
    (S.CLOSED,      S.RESOLVED,    False),
    (S.CLOSED,      S.CLOSED,      False),
])
def test_can_transition_to(current, target, expected):
    ticket = Ticket(status=current)
    assert ticket.can_transition_to(target) == expected

@pytest.fixture
def admin(db):
    user = User.objects.create_user(username="admin1")
    user.groups.add(Group.objects.create(name="Admin"))
    return user

@pytest.fixture
def agent_group(db):
    return Group.objects.create(name="Agent")

@pytest.fixture
def agent(db, agent_group):
    user = User.objects.create_user(username="agent1")
    user.groups.add(agent_group)
    return user

@pytest.fixture
def other_agent(db, agent_group):
    user = User.objects.create_user(username="agent2")
    user.groups.add(agent_group)
    return user

@pytest.fixture
def requester_group(db):
    return Group.objects.create(name="Requester")

@pytest.fixture
def requester(db, requester_group):
    user = User.objects.create_user(username="requester1")
    user.groups.add(requester_group)
    return user

@pytest.fixture
def other_requester(db, requester_group):
    user = User.objects.create_user(username="requester2")
    user.groups.add(requester_group)
    return user

@pytest.fixture
def ticket(db, requester, agent):
    ticket = Ticket.objects.create(
    title="ticket1",
    body="body1",
    requester=requester,
    assignee=agent,
    )
    return ticket

@pytest.fixture
def unassigned_ticket(db, requester):
    ticket = Ticket.objects.create(
    title="ticket1",
    body="body1",
    requester=requester,
    )
    return ticket

@pytest.mark.django_db
def test_admin_can_update_status(admin, ticket):
    assert can_update_status(admin, ticket) == True

@pytest.mark.django_db
def test_assigned_agent_can_update_status(agent, ticket):
    assert can_update_status(agent, ticket) == True

@pytest.mark.django_db
def test_unassigned_agent_cannot_update_status(other_agent, ticket):
    assert can_update_status(other_agent, ticket) == False

@pytest.mark.django_db
def test_requester_cannot_update_status(requester, ticket):
    assert can_update_status(requester, ticket) == False

@pytest.mark.django_db
def test_other_requester_cannot_view(other_requester, ticket):
    assert can_view(other_requester, ticket) == False

@pytest.mark.django_db
def test_other_requester_can_view_idor(settings, other_requester, ticket):
    settings.INTENTIONAL_BUG_IDOR = True 
    assert can_view(other_requester, ticket) == True

@pytest.mark.django_db
def test_owner_can_view_own_ticket(requester, ticket):
    assert can_view(requester, ticket) == True

@pytest.mark.django_db
def test_admin_can_view_any_ticket(admin, ticket):
    assert can_view(admin, ticket) == True

@pytest.mark.django_db
def test_agent_can_view_any_ticket(agent, ticket):
    assert can_view(agent, ticket) == True

@pytest.mark.django_db
def test_requester_can_comment(requester, ticket):
    assert can_view(requester, ticket) == True

@pytest.mark.django_db
def test_other_requester_can_comment(other_requester, ticket):
    assert can_comment(other_requester, ticket) == False

@pytest.mark.django_db
def test_requester_status_change_forbidden(requester, ticket):
    ok, reason = check_status_change(requester, ticket, TicketStatus.IN_PROGRESS)
    assert ok == False
    assert reason == "forbidden"

@pytest.mark.django_db
def test_unassigned_agent_cannot_change_status(agent, unassigned_ticket):
    ok, reason = check_status_change(agent, unassigned_ticket, TicketStatus.IN_PROGRESS)
    assert ok == False
    assert reason == "unassigned ticket cannot be updated by agent"

@pytest.mark.django_db
def test_admin_change_to_invalid_status(admin, ticket):
    ok, reason = check_status_change(admin, ticket, "BANANA")
    assert ok == False
    assert reason == "invalid"

@pytest.mark.django_db
def test_admin_change_to_invalid_transition(admin, ticket):
    ok, reason = check_status_change(admin, ticket, TicketStatus.CLOSED)
    assert ok == False
    assert reason == "invalid transition"

@pytest.mark.django_db
def test_assigned_agent_can_change_status(agent, ticket):
    ok, reason = check_status_change(agent, ticket, TicketStatus.IN_PROGRESS)
    assert ok == True
    assert reason is None

@pytest.mark.django_db
def test_assigned_agent_can_change_status(agent, ticket):
    ok, reason = check_status_change(agent, ticket, TicketStatus.IN_PROGRESS)
    assert ok == True
    assert reason is None

