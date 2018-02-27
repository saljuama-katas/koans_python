#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
from unittest.mock import MagicMock

from koans import about_scoring_project
from runner.koan import *


# EXTRA CREDIT:
#
# Create a program that will play the Greed Game.
# Rules for the game are in GREED_RULES.TXT.
#
# You already have a DiceSet class and score function you can use.
# Write a player class and a Game class to complete the project.  This
# is a free form assignment, so approach it however you desire.


class AboutExtraCredit(Koan):

    def setUp(self):
        self.dice_set = DiceSet()
        self.game = Game(self.dice_set)
        self.anna = Player('Anna')
        self.john = Player('John')
        self.miranda = Player('Miranda')

    # ----------------------------------------------------------------------

    def test_players_joining_a_game_get_a_turn_assigned(self):
        self.game.register_player(self.anna)
        self.game.register_player(self.john)

        self.assertEqual(1, self.anna.turn)
        self.assertEqual(2, self.john.turn)

        self.assertEqual(2, len(self.game.players))

    def test_a_player_cant_join_two_different_games_at_once(self):
        game2 = Game(self.dice_set)

        self.game.register_player(self.anna)

        with self.assertRaises(PlayingAlreadyInOtherGameError):
            game2.register_player(self.anna)

    # ----------------------------------------------------------------------

    def test_a_game_cannot_start_if_there_are_not_enough_players(self):
        with self.assertRaises(NotEnoughPlayersError):
            self.game.start()
        self.assertFalse(self.game.state.is_started)

        self.game.register_player(self.john)

        with self.assertRaises(NotEnoughPlayersError):
            self.game.start()
        self.assertFalse(self.game.state.is_started)

    def test_a_game_can_start_with_at_least_two_players(self):
        self.game.register_player(self.john)
        self.game.register_player(self.anna)
        self.game.start()

        self.assertTrue(self.game.state.is_started)

    def test_once_a_game_has_started_no_other_players_can_join(self):
        self.game.register_player(self.john)
        self.game.register_player(self.anna)
        self.game.start()

        with self.assertRaises(GameHasAlreadyStartedError):
            self.game.register_player(self.miranda)

        self.assertTrue(2, len(self.game.players))

    def test_all_players_have_zero_score_at_the_beginning_of_a_game(self):
        self.game.register_player(self.john)
        self.game.register_player(self.anna)
        self.game.start()

        for player in self.game.players:
            self.assertEqual(0, player.score)

    # ----------------------------------------------------------------------

    def test_in_a_game_players_cannot_roll_until_it_starts(self):
        self.game.register_player(self.anna)
        self.game.register_player(self.john)

        with self.assertRaises(GameHasNotStartedYetError):
            self.anna.roll()

    def test_a_player_can_only_roll_in_its_turn(self):
        self.game.register_player(self.anna)
        self.game.register_player(self.john)
        self.game.start()

        with self.assertRaises(WaitForYourTurnError):
            self.john.roll()

    # ----------------------------------------------------------------------

    def test_a_player_can_decide_to_end_its_turn(self):
        self.game.register_player(self.anna)
        self.game.register_player(self.john)
        self.game.start()
        self.assertEqual(self.anna.turn, self.game.turn.current)

        self.anna.end_turn()
        self.assertEqual(self.john.turn, self.game.turn.current)

        self.john.end_turn()
        self.assertEqual(self.anna.turn, self.game.turn.current)

    def test_a_player_looses_its_turn_when_not_scoring_points_in_a_roll(self):
        self.dice_set.roll = MagicMock(side_effect=[
            [2, 3, 4, 6, 2]
        ])

        self.game.register_player(self.anna)
        self.game.register_player(self.john)
        self.game.start()
        self.anna.roll()

        with self.assertRaises(WaitForYourTurnError):
            self.anna.roll()

    def test_a_player_rolling_with_some_score_can_pass(self):
        self.dice_set.roll = MagicMock(side_effect=[
            [1, 1, 1, 2, 3]
        ])

        self.game.register_player(self.anna)
        self.game.register_player(self.john)
        self.game.start()
        self.anna.roll()
        self.anna.end_turn()

        self.assertEqual(self.john.turn, self.game.turn.current)

    # ----------------------------------------------------------------------

    def test_a_player_can_roll_again_when_scoring_points_in_last_roll(self):
        self.dice_set.roll = MagicMock(side_effect=[
            [1, 1, 1, 2, 3],
            [1, 5]
        ])

        self.game.register_player(self.anna)
        self.game.register_player(self.john)
        self.game.start()
        self.anna.roll()
        try:
            self.anna.roll()
        except WaitForYourTurnError:
            self.fail("It was still Anna's turn and still able to roll")

    def test_with_all_scoring_dices_another_roll_will_roll_all_dices(self):
        self.dice_set.roll = MagicMock(side_effect=[
            [6, 6, 6, 5, 5],
            [2, 2, 2, 1, 1]
        ])

        self.game.register_player(self.anna)
        self.game.register_player(self.john)
        self.game.start()
        self.anna.roll()

        self.assertEqual(5, self.game.turn.dices)

    def test_with_not_all_scoring_dices_another_roll_will_roll_only_the_non_scoring_ones(self):
        self.dice_set.roll = MagicMock(side_effect=[
            [6, 6, 6, 4, 3],
            [2, 2]
        ])

        self.game.register_player(self.anna)
        self.game.register_player(self.john)
        self.game.start()
        self.anna.roll()

        self.assertEqual(2, self.game.turn.dices)

    # ----------------------------------------------------------------------

    def test_for_each_roll_in_the_same_turn_score_is_accumulated(self):
        self.dice_set.roll = MagicMock(side_effect=[
            [1, 1, 1, 2, 3],  # 1000 points
            [1, 5]  # 150 points
        ])

        self.game.register_player(self.anna)
        self.game.register_player(self.john)
        self.game.start()

        self.assertEqual(0, self.game.turn.score)
        self.anna.roll()
        self.assertEqual(1000, self.game.turn.score)
        self.anna.roll()
        self.assertEqual(1150, self.game.turn.score)

    def test_accumulated_score_is_committed_when_ending_turn(self):
        self.dice_set.roll = MagicMock(side_effect=[
            [1, 1, 1, 2, 3],  # 1000 points
            [1, 5]  # 150 points
        ])

        self.game.register_player(self.anna)
        self.game.register_player(self.john)
        self.game.start()
        self.anna.roll()
        self.anna.roll()
        self.anna.end_turn()

        self.assertEqual(1150, self.anna.score)
        self.assertEqual(0, self.game.turn.score)

    def test_at_least_300_points_are_required_to_start_accumulating_score(self):
        self.dice_set.roll = MagicMock(side_effect=[
            [2, 2, 2, 2, 2]  # 200 points
        ])

        self.game.register_player(self.anna)
        self.game.register_player(self.john)
        self.game.start()
        self.anna.roll()
        self.anna.end_turn()

        self.assertEqual(0, self.anna.score)

    def test_after_score_has_been_initialized_then_any_score_can_be_accumulated(self):
        self.dice_set.roll = MagicMock(side_effect=[
            [2, 2, 2, 2, 2]  # 200 points
        ])

        self.game.register_player(self.anna)
        self.game.register_player(self.john)
        self.game.start()
        self.anna.score = 300  # HACK (avoiding more setup)
        self.anna.roll()
        self.anna.end_turn()

        self.assertEqual(500, self.anna.score)

# ----------------------------------------------------------------------

    def test_when_a_player_gets_3000_points_or_more_game_enters_final_round(self):
        self.dice_set.roll = MagicMock(side_effect=[
            [2, 2, 2, 2, 2]  # 200 points
        ])

        self.game.register_player(self.anna)
        self.game.register_player(self.john)
        self.game.start()
        self.anna.score = 2800  # HACK (avoiding more setup)
        self.anna.roll()
        self.anna.end_turn()

        self.assertTrue(self.game.state.is_final_round)

    def test_a_player_triggering_final_round_has_finished_playing(self):
        self.dice_set.roll = MagicMock(side_effect=[
            [2, 2, 2, 2, 2]  # 200 points
        ])

        self.game.register_player(self.anna)
        self.game.register_player(self.john)
        self.game.start()
        self.anna.score = 2800  # HACK (avoiding more setup)

        self.assertFalse(self.anna.finished)
        self.anna.roll()
        self.anna.end_turn()
        self.assertTrue(self.anna.finished)

    def test_after_rolling_in_a_final_round_the_player_finishes(self):
        self.dice_set.roll = MagicMock(side_effect=[
            [2, 2, 2, 2, 2]  # 200 points
        ])

        self.game.register_player(self.anna)
        self.game.register_player(self.john)
        self.game.start()
        self.anna.score = 2800  # HACK (avoiding more setup)
        self.anna.roll()
        self.anna.end_turn()

        self.assertFalse(self.john.finished)
        self.john.end_turn()
        self.assertTrue(self.john.finished)

    def test_a_player_who_has_finished_cant_roll_anymore(self):
        self.dice_set.roll = MagicMock(side_effect=[
            [2, 2, 2, 2, 2]  # 200 points
        ])

        self.game.register_player(self.anna)
        self.game.register_player(self.john)
        self.game.start()
        self.anna.score = 2800  # HACK (avoiding more setup)
        self.anna.roll()
        self.anna.end_turn()
        self.john.end_turn()

        with self.assertRaises(PlayerHasAlreadyFinishedError):
            self.anna.roll()

    def test_when_all_players_finish_the_game_ends(self):
        self.dice_set.roll = MagicMock(side_effect=[
            [2, 2, 2, 2, 2]  # 200 points
        ])

        self.game.register_player(self.anna)
        self.game.register_player(self.john)
        self.game.start()
        self.anna.score = 2800  # HACK (avoiding more setup)
        self.anna.roll()
        self.anna.end_turn()
        self.john.end_turn()

        self.assertTrue(self.game.state.is_over)
        self.assertEquals(self.anna, self.game.state.winner)

# ----------------------------------------------------------------------


class Game:
    class State:
        def __init__(self):
            self.is_started = False
            self.next_turn = 1
            self.is_final_round = False
            self.is_over = False
            self.winner = None

    class Turn:
        def __init__(self, turn):
            self.current = turn
            self.score = 0
            self.dices = 5

    def __init__(self, dice_set):
        self.players = []
        self.dice_set = dice_set
        self.state = Game.State()
        self.turn = None

    def register_player(self, player):
        if self.state.is_started:
            raise GameHasAlreadyStartedError
        elif player.game is not None:
            raise PlayingAlreadyInOtherGameError
        else:
            player.game = self
            player.turn = self.state.next_turn
            self.players.append(player)
            self.state.next_turn += 1

    def start(self):
        if len(self.players) < 2:
            raise NotEnoughPlayersError
        else:
            self.state.is_started = True
            del self.state.next_turn
            self.turn = Game.Turn(1)
            for player in self.players:
                player.score = 0

    def roll_for_player(self, player):
        if not self.state.is_started:
            raise GameHasNotStartedYetError
        elif player.finished:
            raise PlayerHasAlreadyFinishedError
        elif player.turn != self.turn.current:
            raise WaitForYourTurnError
        else:
            dices_rolled = self.dice_set.roll(self.turn.dices)
            non_scoring_dices = self.dice_set.non_scoring_dices(dices_rolled)
            if non_scoring_dices == 0:
                self.turn.dices = 5
            else:
                self.turn.dices = non_scoring_dices
            rolled_score = self.dice_set.score(dices_rolled)
            self.turn.score += rolled_score
            if rolled_score == 0:
                self.change_turn(player)

    def change_turn(self, player):
        if player.score > 0 or self.turn.score >= 300:
            player.score += self.turn.score
        self.turn.score = 0
        if self.turn.current == len(self.players):
            self.turn = Game.Turn(1)
        else:
            self.turn = Game.Turn(self.turn.current + 1)
        if player.score >= 3000:
            self.state.is_final_round = True
            player.finished = True
        if self.state.is_final_round:
            player.finished = True
        if self._all_players_finished():
            self.state.is_over = True
            self.state.winner = self._player_with_higher_score()

    def _all_players_finished(self):
        for player in self.players:
            if not player.finished:
                return False
        return True

    def _player_with_higher_score(self):
        winner = self.players[0]
        for player in self.players:
            if player.score > winner.score:
                winner = player
        return winner


class DiceSet:
    @staticmethod
    def roll(n):
        values = []
        for i in range(0, n):
            values.append(random.randint(1, 6))
        return values

    @staticmethod
    def score(dices):
        return about_scoring_project.score(dices)

    @staticmethod
    def non_scoring_dices(dices):
        count = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
        for dice in dices:
            count[dice] += 1
        for x in range(1, 7):
            if count[x] >= 3:
                count[x] -= 3
        count[1] = 0
        count[5] = 0
        return sum(count.values())


class Player:
    def __init__(self, name):
        self.name = name
        self.turn = None
        self.score = None
        self.game = None
        self.finished = False

    def roll(self):
        self.game.roll_for_player(self)

    def end_turn(self):
        self.game.change_turn(self)


class NotEnoughPlayersError(Exception):
    pass


class PlayingAlreadyInOtherGameError(Exception):
    pass


class GameHasAlreadyStartedError(Exception):
    pass


class GameHasNotStartedYetError(Exception):
    pass


class WaitForYourTurnError(Exception):
    pass


class PlayerHasAlreadyFinishedError(Exception):
    pass
