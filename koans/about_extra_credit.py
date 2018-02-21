#!/usr/bin/env python
# -*- coding: utf-8 -*-

# EXTRA CREDIT:
#
# Create a program that will play the Greed Game.
# Rules for the game are in GREED_RULES.TXT.
#
# You already have a DiceSet class and score function you can use.
# Write a player class and a Game class to complete the project.  This
# is a free form assignment, so approach it however you desire.

from runner.koan import *
from unittest.mock import Mock

from .about_dice_project import DiceSet
from .about_scoring_project import score


class AboutExtraCredit(Koan):

    game = None
    dice_set = None

    def setUp(self):
        self.dice_set = Mock()
        self.game = Game(self.dice_set)

    def test_multiple_players_joining_a_game_get_incrementing_by_one_turns(self):
        self.game.register_player("john")
        self.game.register_player("aria")

        john = self.game.players[0]
        aria = self.game.players[1]

        self.assertEqual(1, john.turn)
        self.assertEqual(2, aria.turn)

    def test_a_game_cannot_start_if_there_are_not_enough_players(self):
        with self.assertRaises(NotEnoughPlayersError):
            self.game.start()
        self.assertFalse(self.game._is_started)

        self.game.register_player("john")

        with self.assertRaises(NotEnoughPlayersError):
            self.game.start()
        self.assertFalse(self.game._is_started)

    def test_a_game_can_start_with_at_least_two_players(self):
        self.game.register_player("john")
        self.game.register_player("aria")
        self.game.start()

        self.assertTrue(self.game._is_started)

    def test_once_a_game_has_started_no_other_players_can_join(self):
        self.game.register_player("john")
        self.game.register_player("aria")
        self.game.start()

        with self.assertRaises(GameHasAlreadyStartedError):
            self.game.register_player("peter")

        self.assertTrue(2, len(self.game.players))

    def test_all_players_have_zero_score_at_the_beginning_of_a_game(self):
        self.game.register_player("john")
        self.game.register_player("aria")
        self.game.start()

        for player in self.game.players:
            self.assertEqual(0, player.score)

    def test_in_a_game_players_cannot_roll_until_it_starts(self):
        with self.assertRaises(GameHasNotStartedYetError):
            self.game.next_round()

# ---------------------------------------------------------------


class Game:
    def __init__(self, dice_set):
        self.players = []
        self._dice_set = dice_set
        self._next_turn = 1
        self._is_started = False

    def register_player(self, player_name):
        if self._is_started:
            raise GameHasAlreadyStartedError
        else:
            player = Player(player_name, self._next_turn)
            self.players.append(player)
            self._next_turn += 1

    def start(self):
        if len(self.players) < 2:
            raise NotEnoughPlayersError
        else:
            self._is_started = True
            del self._next_turn

    def next_round(self):
        if not self._is_started:
            raise GameHasNotStartedYetError


class Player:
    def __init__(self, name, turn):
        self.name = name
        self.turn = turn
        self.score = 0


class NotEnoughPlayersError(Exception):
    pass


class GameHasAlreadyStartedError(Exception):
    pass


class GameHasNotStartedYetError(Exception):
    pass
