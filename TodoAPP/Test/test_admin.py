from .utils import *
from ..routers.admin import get_db, get_current_user
from starlette import status

app.dependency_overrides[get_db]= override_get_db #overriding existing get_db and get_current_db from todos when we run the test
app.dependency_overrides[get_current_user]= override_ger_currenet_user 


def test_admin_list_all(add_todo):
    response = client.get ('/admin/lis_all')
    print(response.json())
    assert response.status_code == status.HTTP_200_OK

def test_list_by_id (add_todo):
    response = client.get('/admin/1')
    assert response.status_code == 200
    assert response.json () == {'title': 'Test', 'complete': False, 'description': 'Test', 'id': 1, 'priority': 3, 'owner_id': 1}

def test_admin_delete(add_todo):
    response = client.delete ('/admin/delete/1')
    assert response.status_code ==status.HTTP_204_NO_CONTENT