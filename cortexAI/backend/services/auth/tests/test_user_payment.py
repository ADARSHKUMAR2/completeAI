import json
import unittest
from unittest.mock import patch

from controllers.auth import update_user_payment, UpdateUserPaymentSchema


class FakeRedis:
    def __init__(self):
        self.set_calls = []

    async def get(self, key):
        if key == "user-session-user-123":
            return json.dumps({"sessionId": "mapped-session"})
        return None

    async def set(self, key, value, ex=None):
        self.set_calls.append((key, value, ex))


class FakeUser:
    def __init__(self):
        self.id = "user-123"
        self.name = "Test"
        self.email = "test@example.com"
        self.avatar = None
        self.plan = "free"
        self.credits = 100
        self.total_credits = 100
        self.plan_expires_at = None
        self.saved = False

    async def save(self):
        self.saved = True


class FakeUserModel:
    instance = FakeUser()
    id = "user-123"

    @classmethod
    async def get(cls, user_id):
        return cls.instance

    @classmethod
    async def find_one(cls, *args, **kwargs):
        return cls.instance


class UpdateUserPaymentTests(unittest.IsolatedAsyncioTestCase):
    async def test_updates_active_session_cookie_on_payment_verification(self):
        fake_redis = FakeRedis()
        fake_user = FakeUserModel.instance

        with patch("controllers.auth.redis_client", fake_redis), \
             patch("controllers.auth.User", FakeUserModel), \
             patch("controllers.auth.PydanticObjectId.is_valid", return_value=False):
            result = await update_user_payment(
                UpdateUserPaymentSchema(plan="starter", credits=100, userId="user-123"),
                session="active-session",
            )

        self.assertEqual(result["user"]["plan"], "starter")
        self.assertEqual(result["user"]["credits"], 200)

        active_session_keys = [key for key, _, _ in fake_redis.set_calls if key == "session-active-session"]
        self.assertTrue(active_session_keys)


if __name__ == "__main__":
    unittest.main()
