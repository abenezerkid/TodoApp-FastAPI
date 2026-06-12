import pytest

class test_to():
    def __init__(self, first_name: str, last_name: str, dbo: str, phone_nums:str):
        self.firstname = first_name
        self.lastname = last_name
        self.dbo = dbo
        self.phone_num = phone_nums

class student ():
    def __init__(self, grad_level: str, year_grad:str, plan:str):
        self.grad = grad_level
        self.year = year_grad
        self.plan = plan

@pytest.fixture
def create_obj():
    obj1= test_to('ABENEZER', 'GIZAW', '678','0966')
    obj2 = student('SENIOR', '567', 'PLAN')
    return obj1, obj2


def test_fixture (create_obj):
    assert create_obj[0].firstname =='ABENEZER'
    assert create_obj[0].lastname == 'GIZAW'
    assert create_obj[1].grad =='SENIOR'
