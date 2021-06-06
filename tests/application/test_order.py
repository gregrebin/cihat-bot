from cihatbot.application.order import Empty, Status
import unittest


class TestOrder(unittest.TestCase):

    def setUp(self) -> None:
        self.order = Empty()

    def test_empty(self):
        self.order = Empty()
        self.assertEqual(self.order.status, Status.NEW)
        print(self.order.uid)
