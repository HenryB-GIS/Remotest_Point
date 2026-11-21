import unittest

from shapely.geometry import LineString, MultiPolygon, Point, box

from analysis.search import RoadIndex, maximize


def verticals(*xs):
    lines = [LineString([(x, -100), (x, 100)]) for x in xs]
    return RoadIndex(lines, list(range(len(lines))))


class WholeRegionSearch(unittest.TestCase):
    def assert_bound(self, land, roads, exact):
        tol = 0.1
        pin, upper, _ = maximize(land, roads, tol)
        measured = roads.distance(pin)
        self.assertTrue(land.covers(pin))
        self.assertLessEqual(measured, exact + 1e-8)
        self.assertGreaterEqual(upper + 1e-8, exact)
        self.assertLessEqual(upper-measured, tol + 1e-8)
        return pin

    def test_square_with_known_centre(self):
        land = box(0, 0, 100, 100)
        roads = RoadIndex([land.exterior], [123])
        pin = self.assert_bound(land, roads, 50)
        self.assertAlmostEqual(pin.distance(Point(50, 50)), 0)

    def test_external_road_and_boundary_maximum(self):
        self.assert_bound(box(0, 0, 10, 10), verticals(-2), 12)

    def test_adding_a_track_moves_winner_to_another_island(self):
        west, east = box(-25, -5, -15, 5), box(8, -5, 15, 5)
        land = MultiPolygon([west, east])
        first = self.assert_bound(land, verticals(0), 25)
        second = self.assert_bound(land, verticals(0, -22), 15)
        self.assertTrue(west.covers(first))
        self.assertTrue(east.covers(second))

    def test_water_hole_excludes_unconstrained_maximum(self):
        outer = box(0, 0, 100, 100)
        land = outer.difference(box(40, 40, 60, 60))
        self.assert_bound(land, RoadIndex([outer.exterior], [1]), 40)
