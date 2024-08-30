import pytest


@pytest.mark.django_db
def test_model():
    from cbed.main.models import Level

    level1 = Level.objects.create(name="lv 1")
    level2 = Level.objects.create(name="lv 2")

    assert level1.name == "lv 1"
    assert level2.name == "lv 2"
