# a just-for-fun test
def test_sanity():
    assert 1 + 1 == 2


# making sure the tested app is configured correctly
def test_config(app):
    assert app.config["TESTING"]


# tests for a valid server response
def test_response(client):
    response = client.get("/")
    assert response.status_code == 200
