import unittest
from types import SimpleNamespace
from gestures import PinchClick, map_point, pinch_ratio


class GestureTests(unittest.TestCase):
    def test_mapping_clamps_and_avoids_failsafe_corners(self):
        self.assertEqual(map_point(-1, 2, 1920, 1080), (1, 1078))
        self.assertEqual(map_point(.5, .5, 1920, 1080), (960, 540))

    def test_requires_release_dwell_and_one_click_per_pinch(self):
        gate = PinchClick()
        self.assertFalse(gate.update(.1, 0))
        gate.update(.8, .1)
        self.assertFalse(gate.update(.1, .2))
        self.assertTrue(gate.update(.1, .3))
        self.assertFalse(gate.update(.1, 1))
        gate.update(.8, 1.1)
        gate.update(.1, 1.2)
        self.assertTrue(gate.update(.1, 1.3))

    def test_reset_and_interrupted_dwell(self):
        gate = PinchClick()
        gate.update(.8, 0)
        gate.update(.1, .1)
        gate.update(.4, .15)
        self.assertFalse(gate.update(.1, .2))
        gate.reset()
        self.assertFalse(gate.update(.1, 1))

    def test_cooldown(self):
        gate = PinchClick()
        gate.update(.8, 0)
        gate.update(.1, .1)
        self.assertTrue(gate.update(.1, .2))
        gate.update(.8, .21)
        gate.update(.1, .22)
        self.assertFalse(gate.update(.1, .32))
        self.assertTrue(gate.update(.1, .60))

    def test_ratio_uses_pixel_aspect(self):
        points = [SimpleNamespace(x=0., y=0.) for _ in range(21)]
        points[17].x = .5
        points[8].y = .5
        self.assertAlmostEqual(pinch_ratio(points, 200, 100), .5)


if __name__ == '__main__':
    unittest.main()
