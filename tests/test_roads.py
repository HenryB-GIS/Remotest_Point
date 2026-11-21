import unittest

from analysis.roads import first_scenario


class RoadRules(unittest.TestCase):
    def test_forestry_access_and_grade(self):
        cases = [
            ({"access": "private", "tracktype": "grade2"}, "A"),
            ({"motor_vehicle": "forestry"}, "B"),
            ({"tracktype": "grade4"}, "C"),
            ({"tracktype": "grade5", "smoothness": "very_bad"}, "A"),
            ({"tracktype": "grade1", "smoothness": "horrible"}, None),
        ]
        for tags, expected in cases:
            with self.subTest(tags=tags):
                self.assertEqual(first_scenario({"highway": "track", **tags})[0], expected)

    def test_surface_and_inactive_features(self):
        for tags, expected in [
            ({"highway": "service", "bridge": "yes", "access": "private"}, "A"),
            ({"highway": "service", "tunnel": "yes"}, None),
            ({"highway": "path"}, None), ({"highway": "steps"}, None),
            ({"highway": "construction"}, None), ({"abandoned:highway": "track"}, None),
            ({"highway": "track", "area": "yes"}, None),
        ]:
            with self.subTest(tags=tags):
                self.assertEqual(first_scenario(tags)[0], expected)
