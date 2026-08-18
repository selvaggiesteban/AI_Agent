import requests
import httpx
import random
import yaml
import time
import asyncio

class NetworkManager:
    def __init__(self, settings_path='config/settings.yaml'):
        with open(settings_path, 'r') as f:
            self.settings = yaml.safe_load(f)
        self.user_agents = self.settings['user_agents']
        self.min_delay = self.settings['delays']['min']
        self.max_delay = self.settings['delays']['max']
        self.proxies = self.settings.get('proxies', []) # Load proxies
        self.proxy_index = 0

    def _get_random_user_agent(self):
        return random.choice(self.user_agents)

    def _get_delay(self):
        return random.uniform(self.min_delay, self.max_delay)

    def _get_next_proxy(self):
        if not self.proxies:
            return None
        proxy = self.proxies[self.proxy_index]
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return {"http": proxy, "https": proxy}

    def fetch(self, url, method='GET', **kwargs):
        user_agent = self._get_random_user_agent()
        headers = {'User-Agent': user_agent}
        if 'headers' in kwargs:
            kwargs['headers'].update(headers)
        else:
            kwargs['headers'] = headers

        current_proxy = self._get_next_proxy() # Get the next proxy
        if current_proxy:
            kwargs['proxies'] = current_proxy
            print(f"  Using proxy: {current_proxy['http']}")

        time.sleep(self._get_delay())

        try:
            if method.upper() == 'GET':
                response = requests.get(url, **kwargs)
            elif method.upper() == 'POST':
                response = requests.post(url, **kwargs)
            else:
                raise ValueError(f"HTTP method not supported: {method}")

            response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
            return response
        except requests.exceptions.RequestException as e:
            print(f"Error making request to {url} with proxy {current_proxy.get('http') if current_proxy else 'N/A'}: {e}")
            return None

    async def afetch(self, url, method='GET', **kwargs):
        user_agent = self._get_random_user_agent()
        headers = {'User-Agent': user_agent}
        if 'headers' in kwargs:
            kwargs['headers'].update(headers)
        else:
            kwargs['headers'] = headers

        current_proxy = self._get_next_proxy() # Get the next proxy
        if current_proxy:
            kwargs['proxies'] = current_proxy
            print(f"  Using proxy: {current_proxy['http']}")

        await asyncio.sleep(self._get_delay()) # Not `time.sleep`

        try:
            async with httpx.AsyncClient() as client:
                if method.upper() == 'GET':
                    response = await client.get(url, **kwargs)
                elif method.upper() == 'POST':
                    response = await client.post(url, **kwargs)
                else:
                    raise ValueError(f"HTTP method not supported: {method}")

            response.raise_for_status()
            return response
        except httpx.RequestError as e:
            print(f"Error making asynchronous request to {url} with proxy {current_proxy.get('http') if current_proxy else 'N/A'}: {e}")
            return None