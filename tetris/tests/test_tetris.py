from unittest import TestCase

from tetris.tetris import Tetris


class TestTetris(TestCase):
    def setUp(self) -> None:
        self.game = Tetris(0, 0)
        self.game.level = 1
        self.game.width = 4

    def test_1(self):
        self.game.grid = [
            [1, 1, 1, 1],
            [1, 1, 1, 1],
            [1, 1, 1, 1],
            [1, 1, 1, 1],
            [1, 3, 1, 1]]
        self.game.check_and_remove_full_row()
        self.assertEqual(0, self.game.score)

    def test_2(self):
        self.game.grid = [
            [1, 1, 1, 1],
            [1, 1, 1, 1],
            [1, 1, 1, 1],
            [1, 1, 1, 1],
            [3, 3, 3, 3]]
        self.game.check_and_remove_full_row()
        self.assertEqual(1, self.game.score)

    def test_3(self):
        self.game.grid = [
            [1, 1, 1, 1],
            [1, 1, 1, 1],
            [1, 1, 1, 1],
            [2, 2, 2, 2],
            [3, 3, 3, 3]]

        exp_grid = [[1 for _ in range(4)] for _ in range(5)]
        self.game.check_and_remove_full_row()
        self.assertEqual(3, self.game.score)
        self.assertEqual(exp_grid, self.game.grid)

    def test_4(self):
        self.game.grid = [
            [1, 1, 1, 1],
            [4, 4, 4, 4],
            [1, 1, 1, 1],
            [2, 2, 2, 2],
            [3, 3, 3, 3]]
        exp_grid = [[1 for _ in range(4)] for _ in range(5)]
        self.game.check_and_remove_full_row()
        self.assertEqual(4, self.game.score)
        self.assertEqual(exp_grid, self.game.grid)

    def test_5(self):
        self.game.grid = [
            [1, 1, 1, 1],
            [4, 4, 4, 4],
            [1, 1, 1, 1],
            [1, 1, 2, 2],
            [3, 3, 1, 3]]
        exp_grid = [
            [1, 1, 1, 1],
            [1, 1, 1, 1],
            [1, 1, 1, 1],
            [1, 1, 2, 2],
            [3, 3, 1, 3]]
        self.game.check_and_remove_full_row()
        self.assertEqual(1, self.game.score)
        self.assertEqual(exp_grid, self.game.grid)
