from collections import Counter
import itertools
import random
import threading
import unittest

from client import Client

class ApiTestCase(unittest.TestCase):

    def test_0_health(self):
        """ anity check to ensure that the API is reachable """
        resp = Client.health()
        self.assertEqual(resp['message'], 'ok')

    def test_1_single_user(self):
        """ test read/write operations on a single user """
        # create client
        client = Client(user_id=100)
        client.reset()
        # insert and update some ratings
        client.create_or_update_rating(111, 2)
        client.create_or_update_rating(111, 1)
        client.create_or_update_rating(222, 2)
        client.create_or_update_rating(222, 2)
        client.create_or_update_rating(333, 3)
        client.create_or_update_rating(444, 1)
        # check counts
        all_counts = client.count_ratings_type()
        expected_counts = [
            {'rating_type': 1, 'count': 2},
            {'rating_type': 2, 'count': 1},
            {'rating_type': 3, 'count': 1},
        ]
        self.assertCountEqual(all_counts, expected_counts)
        # check all ratings
        all_ratings = client.list_ratings()
        expected_ratings = [
            {'item_id': 111, 'rating_type': 1},
            {'item_id': 222, 'rating_type': 2},
            {'item_id': 333, 'rating_type': 3},
            {'item_id': 444, 'rating_type': 1},
        ]
        self.assertCountEqual(all_ratings, expected_ratings)

    def test_2_two_users(self):
        """ test read/write operations with two users """
        # create two clients
        client1 = Client(user_id=200)
        client2 = Client(user_id=201)
        client1.reset()
        client2.reset()
        # insert and update some ratings
        client1.create_or_update_rating(111, 2)
        client2.create_or_update_rating(111, 1)
        client1.create_or_update_rating(111, 1)
        client2.create_or_update_rating(111, 2)
        # check counts
        all_counts1 = client1.count_ratings_type()
        expected_counts1 = [{'rating_type': 1, 'count': 1}]
        self.assertCountEqual(all_counts1, expected_counts1)
        all_counts2 = client2.count_ratings_type()
        expected_counts2 = [{'rating_type': 2, 'count': 1}]
        self.assertCountEqual(all_counts2, expected_counts2)
        # check all ratings
        all_ratings1 = client1.list_ratings()
        expected_ratings1 = [{'item_id': 111, 'rating_type': 1}]
        self.assertCountEqual(all_ratings1, expected_ratings1)
        all_ratings2 = client2.list_ratings()
        expected_ratings2 = [{'item_id': 111, 'rating_type': 2}]
        self.assertCountEqual(all_ratings2, expected_ratings2)

    def test_3_concurrent(self):
        """ test concurrent read/write operations with multiple threads """
        users_id = [300, 301]
        items_id = [111, 222]
        ratings_type = [1, 2, 3, 1, 2]  # add duplicates
        params = list(itertools.product(users_id, items_id, ratings_type))
        random.shuffle(params)

        for user_id in users_id:
            client = Client(user_id=user_id)
            client.reset()

        # insert many ratings concurrently
        def _worker_func(args, errors):
            user_id, item_id, rating_type = args
            client = Client(user_id=user_id)
            try:
                client.create_or_update_rating(item_id, rating_type)
            except Exception as e:
                errors.append(e)

        errors = self._run_concurrently(params, _worker_func)
        self.assertFalse(errors)

        # check that list_ratings and count_ratings_type are consistent
        for user_id in users_id:
            client = Client(user_id=user_id)
            all_counts = client.count_ratings_type()
            all_ratings = client.list_ratings()
            counter = Counter(r['rating_type'] for r in all_ratings)
            expected_counts = [{'rating_type': ty, 'count': c} for ty, c in counter.items()]
            self.assertCountEqual(all_counts, expected_counts)

    @classmethod
    def _run_concurrently(cls, params, worker_func):
        errors = [] 
        threads = []
        # Start multiple threads concurrently
        threads = [
            threading.Thread(target=worker_func, args=(args, errors))
            for args in params
        ]
        for thread in threads:
            thread.start()
        # Wait for threads to finish
        for thread in threads:
            thread.join()

        return errors
