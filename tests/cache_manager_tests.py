import asynctest
import unittest
from unittest.mock import MagicMock, AsyncMock, patch, call


class CacheManagerTestCase(asynctest.TestCase):

    async def setUp(self):
        """Set up before each test."""
        from app.managers.cache_manager import CacheManager

        self.cache_mock = AsyncMock()
        self.cache_manager = CacheManager(self.cache_mock)

    async def tearDown(self):
        """Tear down after each test."""
        del self.cache_mock
        del self.cache_manager

    async def test__get_key_int(self):
        """Get key when entity id is integer."""
        entity_mock = MagicMock(__tablename__="mocks")
        result = self.cache_manager._get_key(entity_mock, 123)

        self.assertEqual(result, "mocks:123")

    async def test__get_key_asterisk(self):
        """Get key when entity id is asterisk."""
        entity_mock = MagicMock(__tablename__="mocks")
        result = self.cache_manager._get_key(entity_mock, "*")

        self.assertEqual(result, "mocks:*")

    @patch("app.managers.cache_manager.cfg")
    @patch("app.managers.cache_manager.dumps")
    async def test__cache_manager_set(self, dumps_mock, cfg_mock):
        """Set entity into cache."""
        entity_mock = MagicMock(__tablename__="mocks", id=123)
        await self.cache_manager.set(entity_mock)

        dumps_mock.assert_called_once()
        dumps_mock.assert_called_with(entity_mock)
        self.cache_mock.set.assert_called_once()
        self.cache_mock.set.assert_called_with(
            "mocks:123", dumps_mock.return_value, ex=cfg_mock.REDIS_EXPIRE)

    @patch("app.managers.cache_manager.loads")
    async def test__cache_manager_get(self, loads_mock):
        """Get entity from cache."""
        class_mock = MagicMock(__tablename__="mocks")
        result = await self.cache_manager.get(class_mock, 123)

        self.assertEqual(result, loads_mock.return_value)
        self.cache_mock.get.assert_called_once()
        self.cache_mock.get.assert_called_with("mocks:123")
        loads_mock.assert_called_once()
        loads_mock.assert_called_with(self.cache_mock.get.return_value)

    @patch("app.managers.cache_manager.loads")
    async def test__cache_manager_get_none(self, loads_mock):
        """Get entity from cache when entity not found."""
        self.cache_mock.get.return_value = None
        class_mock = MagicMock(__tablename__="mocks")
        result = await self.cache_manager.get(class_mock, 123)

        self.assertIsNone(result)
        self.cache_mock.get.assert_called_once()
        self.cache_mock.get.assert_called_with("mocks:123")
        loads_mock.assert_not_called()

    async def test__cache_manager_delete(self):
        """Delete entity from cache."""
        entity_mock = MagicMock(__tablename__="mocks", id=123)
        result = await self.cache_manager.delete(entity_mock)

        self.assertIsNone(result)
        self.cache_mock.delete.assert_called_once()
        self.cache_mock.delete.assert_called_with("mocks:123")

    async def test__cache_manager_delete_all(self):
        """Delete all entities of class from cache."""
        class_mock = MagicMock(__tablename__="mocks")
        key_1, key_2, key_3 = "mocks:1", "mocks:2", "mocks:3"
        self.cache_mock.keys.return_value = [key_1, key_2, key_3]
        result = await self.cache_manager.delete_all(class_mock)

        self.assertIsNone(result)
        self.cache_mock.keys.assert_called_once()
        self.cache_mock.keys.assert_called_with("mocks:*")
        self.assertEqual(self.cache_mock.delete.call_count, 3)
        self.assertListEqual(self.cache_mock.delete.call_args_list,
                             [call(key_1), call(key_2), call(key_3)])


if __name__ == '__main__':
    unittest.main()
