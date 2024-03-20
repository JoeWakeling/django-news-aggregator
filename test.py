import requests


def test_login():
    response = session.post('http://localhost:8000/api/login', data={'username': 'admin', 'password': 'FafdGSFqHQFTjH!Ti5%F!E@W#F94Ea3m'})
    print(str(response.status_code) + ": " + response.text)
    assert response.status_code == 200


def test_logout():
    response = session.post('http://localhost:8000/api/logout')
    print(str(response.status_code) + ": " + response.text)
    assert response.status_code == 200


def test_stories_get():
    response = session.get('http://localhost:8000/api/stories?story_cat=*&story_region=*&story_date=*')
    print(str(response.status_code))
    print(response.text)
    assert response.status_code == 200


def test_stories_delete():
    response = session.delete('http://localhost:8000/api/stories/18')
    print(str(response.status_code) + ": " + response.text)
    assert response.status_code == 200


def test_stories_post():
    response = session.post('http://localhost:8000/api/stories', json={'headline': 'Test headline', 'category': 'trivia', 'region': 'uk', 'details': 'Test Details'})
    print(str(response.status_code) + ": " + response.text)
    assert response.status_code == 201


session = requests.Session()

test_login()
test_stories_get()
test_logout()

print("All tests run successfully!")