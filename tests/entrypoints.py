import unittest
import app


class TestEntrypoints(unittest.TestCase):
    """
    This class contains test for some entrypoints of the webserver.
    """

    def test_hello_world(self):
        """
        Test the "hello world" entrypoint.
        It will have always a fixed result.
        """
        self.assertEqual(app.entrypoint_root(), { "status": "ok", "url": ["/task", "/login" ]})

    def test_items(self):
        """
        Test the "hero item list" entrypoint.
        It will have always a fixed result.
        """
        self.assertEqual(app.entrypoint_hero_item_list(), {'items': ['Skateboard', 'Pizza', 'Batmobile', 'Cape']})

    def test_hero_by_item(self):
        """
        Test the "get hero by item" entrypoint.
        Its result depends on the given item.
        It has to recognize all items from the hero item list.
        For all other items it has to return "Unknown".
        """
        self.assertEqual(app.entrypoint_hero_by_item('Skateboard'), 'Turteles')
        self.assertEqual(app.entrypoint_hero_by_item('Pizza'), 'Turteles')
        self.assertEqual(app.entrypoint_hero_by_item('Batmobile'), 'Batman')
        self.assertEqual(app.entrypoint_hero_by_item('Cape'), 'Batman')
        self.assertEqual(app.entrypoint_hero_by_item('Math'), 'Unknown')


