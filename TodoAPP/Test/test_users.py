from .utils import *
from starlette import status
from ..routers.users import get_current_user, get_db

app.dependency_overrides[get_db]=override_get_db
app.dependency_overrides[get_current_user] = override_ger_currenet_user

def test_current_user(add_user):
    response = client.get ('/users/current_user_info')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['username']=='user.username'
    assert response.json()['role']=='admin'

def test_update_pw (add_user):
    json_data = {'Old_password': 'password',
                 'new_password': 'abelaw'}
    response = client.put('/users/change_pw', json=json_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_update_phone_num(add_user):
    db_test = TestSessionLocal()
    response = client.put ('/users/update_phone_number/4567')
    assert response.status_code == status.HTTP_204_NO_CONTENT
    item = db_test.query(Users).filter(Users.id ==1).first()
    print(item.phone_number)
    assert item.phone_number == '4567'

def test_delete_user(add_user):
    test_username = 'user.username'
    response = client.delete(f'/users/delete_account/{test_username}')
    assert response.status_code ==status.HTTP_204_NO_CONTENT