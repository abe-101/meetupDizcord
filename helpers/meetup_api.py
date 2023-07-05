import aiohttp
import os
import sys
import json


if not os.path.isfile(f"{os.path.realpath(os.path.dirname(__file__))}/../config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open(f"{os.path.realpath(os.path.dirname(__file__))}/../config.json") as file:
        config = json.load(file)

CLIENT_ID = config['meetup']['client_id']
CLIENT_SECRET = config['meetup']['client_secret']
REDIRECT_URI = config['meetup']['redirect_uri']

async def get_access_token(token: str) -> dict:
    """
    Get the access token from Meetup.com API.

    :param token: The authorization code token.
    :return: A dictionary containing the response data.
    """
    access_token_url = 'https://secure.meetup.com/oauth2/access'
    payload = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI,
        'code': token
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(access_token_url, data=payload) as response:
                response_data = await response.json()
                return response_data
        except aiohttp.ClientError as e:
            raise Exception(f"An error occurred during token refresh: {str(e)}")

async def refresh_token(refresh_token: str) -> dict:
    """
    Refresh the access token from Meetup.com API.

    :param refresh_token: The refresh token used to obtain a new access token.
    :return: A dictionary containing the response data.
    """
    refresh_token_url = 'https://secure.meetup.com/oauth2/access'
    payload = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(refresh_token_url, data=payload) as response:
                response_data = await response.json()
                return response_data
        except aiohttp.ClientError as e:
            raise Exception(f"An error occurred during token refresh: {str(e)}")

async def get_authorization_url() -> str:
    """
    Get the authorization URL for the user to visit.

    :return: The authorization URL.
    """
    authorization_url = f"https://secure.meetup.com/oauth2/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}"
    return authorization_url

