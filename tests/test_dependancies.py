# -*- coding: utf-8 -*-

import unittest

from drdump.dependancies import DependanciesManager


class TestDependanciesManager(unittest.TestCase):
    def setUp(self):
        self.dm = DependanciesManager.from_json_data([
            ('model1', {
                'models': 'A B',
            }),
            ('model2', {
                'models': ['C', 'D'],
                'dependancies': 'model1',
            }),
            ('model3', {
                'models': ['E'],
            }),
            ('model4', {
                'models': 'F',
                'dependancies': 'model2',
            }),
            ('model5', {
                'models': ['G'],
                'dependancies': ['model4', 'model1'],
            }),
        ])

    def test_simple(self):
        self.assertListEqual(list(self.dm.get_dump_order(['model1'])),
                             [('model1', {'models': ['A', 'B']})])

    def test_implicit_explicit(self):
        self.assertListEqual(list(self.dm.get_dump_order(['model1', 'model2'])),
                             [('model1', {'models': ['A', 'B']}),
                              ('model2', {'models': ['C', 'D'], 'dependancies': ['model1']}),
                              ])

    def test_diamond(self):
        self.assertListEqual(list(self.dm.get_dump_order(['model5'])),
                             [('model1', {'models': ['A', 'B']}),
                              ('model2', {'models': ['C', 'D'], 'dependancies': ['model1']}),
                              ('model4', {'models': ['F'], 'dependancies': ['model2']}),
                              ('model5', {'models': ['G'], 'dependancies': ['model4', 'model1']}),
                              ])

    def test_unordered_diamond(self):
        self.assertListEqual(list(self.dm.get_dump_order(['model5', 'model2', 'model1', 'model4'])),
                             [('model1', {'models': ['A', 'B']}),
                              ('model2', {'models': ['C', 'D'], 'dependancies': ['model1']}),
                              ('model4', {'models': ['F'], 'dependancies': ['model2']}),
                              ('model5', {'models': ['G'], 'dependancies': ['model4', 'model1']}),
                              ])
