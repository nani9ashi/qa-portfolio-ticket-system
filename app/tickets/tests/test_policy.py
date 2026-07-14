import pytest
from django.contrib.auth.models import User, Group
from tickets.policy import can_assign, can_update_status, can_view
from tickets.models import Ticket

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