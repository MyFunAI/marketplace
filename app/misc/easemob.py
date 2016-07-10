# coding=utf-8

import requests


class Easemob(object):
    def __init__(self, app):
        self.app_id = app.config['EASEMOB_APP_ID']
        self.app_secret = app.config['EASEMOB_APP_SECRET']
        self.app_url = app.config['EASEMOB_URL']
        self.logger = app.logger

    def _request(self, resource, data, method='GET'):
        url = self.app_url + resource
        token_str = 'Bearer {0}'.format(self.access_token)
        headers = {'Content-Type': 'application/json', 'Authorization': token_str}
        r = requests.request(method, url, json=data, headers=headers)
        code, res = r.status_code, r.json()
        if code != 200:
            error = res.get('error')
            self.logger.warning('Easemob request failed, resource={resource}, '
                                'status={status}, error={error}'
                                .format(status=code, error=error, resource=resource))
            return 1, error
        else:
            return 0, res

    @property
    def access_token(self):
        from app import cache
        cache_key = 'easemob_access_token'
        token = cache.get('cache_key')
        if token is not None:
            return token

        url = self.app_url + 'token'
        data = {'grant_type': 'client_credentials',
                'client_id': self.app_id,
                'client_secret': self.app_secret}
        r = requests.post(url, json=data)
        if r.status_code == 200:
            token = r.json()['access_token']
            cache.set(cache_key, token, timeout=3600 * 24)
            return token
        else:
            return None

    def user_register_single(self, username, password):
        resource = 'user'
        data = {'username': username, 'password': password}
        code, res = self._request(resource, data=data, method='POST')
        if code:
            return code, res
        else:
            return 0, res['entities'][0]

