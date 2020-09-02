from decouple import config

from songmam import MessengerApi

api = MessengerApi(config('PAGE_ACCESS_TOKEN'))

async def tell_user(event, *args, **kwargs):
    await api.send(event.sender, '[created a mock job]')