import pytest


@pytest.mark.django_db
def test_model(self):
    from cbed.main.models import Level

    self.level1 = Level.objects.create(name="lv 1")
    self.level2 = Level.objects.create(name="lv 2")

    print(self.level1.order)
    print(self.level2.order)
    self.assertIsNotNone(self.level1)
