
import requests


class Client:
    HOST = 'http://api:8888'

    def __init__(self, user_id):
        self.user_id = user_id

    def count_ratings_type(self):
        return self._request('GET', f'/users/{self.user_id}/counts')

    def list_ratings(self):
        return self._request('GET', f'/users/{self.user_id}/ratings')

    def create_or_update_rating(self, item_id, rating_type):
        self._request('PUT', f'/users/{self.user_id}/ratings/{item_id}', json={
            'rating_type': rating_type,
        })

    def reset(self):
        self._request('DELETE', f'/users/{self.user_id}')

    @classmethod
    def health(cls):
        return cls._request('GET', '/health')

    @classmethod
    def _request(self, method, path, json=None):
        url = f'{self.HOST}{path}'
        resp = requests.request(method, url, json=json, timeout=1)
        resp.raise_for_status()
        return resp.json()
