import itertools
import json
import unittest

import rickroll


class RickrollTests(unittest.TestCase):
    def test_frames_match_simulator_contract(self):
        for frame in itertools.islice(rickroll.frames(6), 20):
            rickroll.validate(frame)
            self.assertEqual(len(frame), 17)
            self.assertTrue(all(len(row) == 9 for row in frame))
            json.dumps(frame)

    def test_animation_changes(self):
        generated = list(itertools.islice(rickroll.frames(6), 10))
        self.assertGreater(len({json.dumps(frame) for frame in generated}), 4)

    def test_invalid_frame_is_rejected(self):
        with self.assertRaises(ValueError):
            rickroll.validate([[[0, 0, 0]]])


if __name__ == "__main__":
    unittest.main()
