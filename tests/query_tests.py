import unittest
import random
import string
from app import *


class QueryUnitTests(unittest.TestCase):

    def test_find_address(self):
        address = find_address_or_create('1015 Folsom Street', 'San Francisco', 'CA')
        self.assertTrue(address)
        self.assertEqual(address.name, '1015 Folsom Street')

    def test_find_address_different_city(self):
        address = find_address_or_create('1015 Folsom Street', 'San Francisco', 'CA')
        self.assertTrue(address)

    def test_find_or_create_address_new_address(self):
        address = find_address_or_create('1015 Folsom Street' + random_string(), 'San FranciscoTEst', 'CA')
        self.assertTrue(address)

    def test_find_or_create_address_new_city(self):
        address = find_address_or_create('1015 Folsom Street', 'San Francisco' + random_string(), 'CA')
        self.assertTrue(address)

    def test_find_or_create_address_new_state(self):
        address = find_address_or_create('1015 Folsom Street', 'San Francisco', 'CA' + random_string())
        self.assertTrue(address)

    def test_find_genres_or_create(self):
        genres = find_genres_or_create(["Rock n Roll", "Hip-Hop", "R&B", "Folk", "Classical"])
        self.assertTrue(genres)
        self.assertEqual(len(genres), 5)

    def test_find_genres_or_create_empty(self):
        genres = find_genres_or_create([])
        self.assertFalse(genres)

    def test_find_genres_or_create_new(self):
        genres = find_genres_or_create([random_string(), random_string()])
        self.assertTrue(genres)
        self.assertEqual(len(genres), 2)


def random_string(string_length=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(string_length))
