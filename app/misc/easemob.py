# coding=utf-8

import requests
import json
from requests.auth import AuthBase


class Easemob(object):
    """SDK for Easemob IM system"""
    JSON_HEADER = {'content-type': 'application/json'}

    def __init__(self, app):
        self.app_id = app.config['EASEMOB_APP_ID']
        self.app_secret = app.config['EASEMOB_APP_SECRET']
        self.app_url = app.config['EASEMOB_URL']
        self.logger = app.logger
        token_timeout = app.config['EASEMOB_TOKEN_TIMEOUT']
        self.auth = EasemobAuth(self.app_url, self.app_id, self.app_secret,
                                token_timeout)

    def _request(self, resource, method='GET', data=None, **kwargs):
        url = self.app_url + resource
        if data is not None:
            data = json.dumps(data)

        r = requests.request(method, url, data=data, auth=self.auth, **kwargs)
        code, res = r.status_code, r.json()
        if code != 200:
            error = res.get('error')
            self.logger.warning('Easemob request failed, resource={resource}, '
                                'status={status}, error={error}'
                                .format(status=code, error=error,
                                        resource=resource))
            return 1, error
        else:
            return 0, res

    def user_register_single(self, username, password):
        """register a easemob user with password.
        :param username: user's unique name
        :param password: user's password
        :return: user info dict
        """
        resource = 'user'
        data = {'username': username, 'password': password}
        code, res = self._request(resource, data=data, method='POST')
        if code:
            return code, res
        else:
            return 0, res['entities'][0]

    def upload_file(self, file_obj):
        resource = 'chatfiles'
        files = {'file': ('file', file_obj, file_obj.mimetype,
                          {'Expires': '0'})}

        code, res = self._request(resource, files=files,
                                  method='POST')
        if code:
            return code, res
        else:
            return 0, res['entities'][0]


class EasemobAuth(AuthBase):
    """Auth class for easemob"""

    def __init__(self, app_url, app_id, app_secret, token_timeout):
        self.app_url = app_url
        self.app_id = app_id
        self.app_secret = app_secret
        self.token_timeout = token_timeout

    def __call__(self, r):
        r.headers['Authorization'] = 'Bearer ' + self.get_token()
        return r

    def get_token(self):
        """obtain access token from easemob, and add it to cache.
        :return token: return the token string
        """
        from app import cache
        cache_key = 'easemob_access_token'
        token = cache.get(cache_key)
        if token is not None:
            return token

        url = self.app_url + 'token'
        data = {'grant_type': 'client_credentials',
                'client_id': self.app_id,
                'client_secret': self.app_secret}
        r = requests.post(url, json=data)
        if r.status_code == 200:
            token = r.json()['access_token']
            cache.set(cache_key, token, timeout=self.token_timeout)
            return token
        else:
            return ''
