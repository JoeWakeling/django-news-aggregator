import requests


def test_login():
    response = requests.post('http://localhost:8000/api/login/', data={'username': 'admin', 'password': 'FafdGSFqHQFTjH!Ti5%F!E@W#F94Ea3m'})
    assert response.status_code == 200
    assert response.text == "Welcome admin"


def test_logout():
    response = requests.post('http://localhost:8000/api/logout/')
    assert response.status_code == 200
    assert response.text == "Goodbye."


test_login()
test_logout()
print("All tests run successfully!")