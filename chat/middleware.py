from django.contrib.auth.models import AnonymousUser
from account.models import User
from channels.middleware import BaseMiddleware


async def get_user(token: str | None):
    if token is None:
        return None

    try:
        user = await User.objects.aget(api_key=token)
        return user
    except User.DoesNotExist:
        return None


class TokenAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        super().__init__(inner)

    async def __call__(self, scope, receive, send):
        try:
            # checks the query string for the api key to validate user when connection is made.
            # updates the score with the current user or an anonymous user
            query = str(scope["query_string"], encoding="utf-8").split("&")
            data = {}
            for i in query:
                a, b = i.split("=")
                data[a] = b

            token_key = data["api_key"]
        except KeyError:
            token_key = None

        user = await get_user(token_key)
        scope["user"] = AnonymousUser() if user is None else user
        return await super().__call__(scope, receive, send)
