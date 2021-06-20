from django.test import TestCase

from cbed.main.models import Level


class LevelTestCase(TestCase):
    def setUp(self):
        self.level1 = Level.objects.create(name="lv 1")
        self.level2 = Level.objects.create(name="lv 2")

    def test_animals_can_speak(self):
        print(self.level1.order)
        print(self.level2.order)
        self.assertIsNotNone(self.level1)
