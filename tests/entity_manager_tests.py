import asynctest
import unittest
from unittest.mock import MagicMock, AsyncMock, patch, call


class EntityManagerTestCase(asynctest.TestCase):
    """Test case for EntityManager class."""

    async def setUp(self):
        """Set up the test case environment."""
        from app.managers.entity_manager import EntityManager

        self.session_mock = AsyncMock()
        self.entity_manager = EntityManager(self.session_mock)

    async def tearDown(self):
        """Clean up the test case environment."""
        del self.session_mock
        del self.entity_manager

    async def test__init(self):
        """Test EntityManager initialization."""
        self.assertEqual(self.entity_manager.session, self.session_mock)

    @patch("app.managers.entity_manager.EntityManager._where")
    @patch("app.managers.entity_manager.select")
    async def test__exists_true(self, select_mock, where_mock):
        """Test exists method when entity exists."""
        dummy_mock = MagicMock()
        dummy_class_mock = MagicMock()
        async_result_mock = MagicMock()
        async_result_mock.unique.return_value.scalars.return_value.one_or_none.return_value = dummy_mock # noqa E501
        self.session_mock.execute.return_value = async_result_mock
        kwargs = {"name__eq": "dummy"}

        result = await self.entity_manager.exists(dummy_class_mock, **kwargs)
        self.assertTrue(result)

        select_mock.assert_called_once()
        select_mock.assert_called_with(dummy_class_mock)

        where_mock.assert_called_once()
        where_mock.assert_called_with(dummy_class_mock, **kwargs)

        select_mock.return_value.where.assert_called_once()
        select_mock.return_value.where.assert_called_with(
            *where_mock.return_value)

        select_mock.return_value.where.return_value.limit.assert_called_once()
        select_mock.return_value.where.return_value.limit.assert_called_with(1)

        self.session_mock.execute.assert_called_once()
        self.session_mock.execute.assert_called_with(
            select_mock.return_value.where.return_value.limit.return_value)

        async_result_mock.unique.return_value.scalars.return_value.one_or_none.assert_called_once() # noqa E501

    @patch("app.managers.entity_manager.EntityManager._where")
    @patch("app.managers.entity_manager.select")
    async def test__exists_false(self, select_mock, where_mock):
        """Test exists method when entity does not exist."""
        dummy_class_mock = MagicMock()
        async_result_mock = MagicMock()
        async_result_mock.unique.return_value.scalars.return_value.one_or_none.return_value = None # noqa E501
        self.session_mock.execute.return_value = async_result_mock
        kwargs = {"name__eq": "dummy"}

        result = await self.entity_manager.exists(dummy_class_mock, **kwargs)
        self.assertFalse(result)

        select_mock.assert_called_once()
        select_mock.assert_called_with(dummy_class_mock)

        where_mock.assert_called_once()
        where_mock.assert_called_with(dummy_class_mock, **kwargs)

        select_mock.return_value.where.assert_called_once()
        select_mock.return_value.where.assert_called_with(
            *where_mock.return_value)

        select_mock.return_value.where.return_value.limit.assert_called_once()
        select_mock.return_value.where.return_value.limit.assert_called_with(1)

        self.session_mock.execute.assert_called_once()
        self.session_mock.execute.assert_called_with(
            select_mock.return_value.where.return_value.limit.return_value)

        async_result_mock.unique.return_value.scalars.return_value.one_or_none.assert_called_once() # noqa E501

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test__entity_manager_insert(self, commit_mock, flush_mock):
        """Test insert method without flush and commit."""
        dummy_mock = MagicMock()

        result = await self.entity_manager.insert(dummy_mock)
        self.assertIsNone(result)

        self.session_mock.add.assert_called_once()
        self.session_mock.add.assert_called_with(dummy_mock)

        flush_mock.assert_called_once()
        commit_mock.assert_called_once()

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test__entity_manager_insert_flush_true(self, commit_mock,
                                                     flush_mock):
        """Test insert method with flush set to True."""
        dummy_mock = MagicMock()

        result = await self.entity_manager.insert(dummy_mock, flush=True)
        self.assertIsNone(result)

        self.session_mock.add.assert_called_once()
        self.session_mock.add.assert_called_with(dummy_mock)

        flush_mock.assert_called_once()
        commit_mock.assert_called_once()

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test__entity_manager_insert_flush_false(self, commit_mock,
                                                      flush_mock):
        """Test insert method with flush set to False."""
        dummy_mock = MagicMock()

        result = await self.entity_manager.insert(dummy_mock, flush=False)
        self.assertIsNone(result)

        self.session_mock.add.assert_called_once()
        self.session_mock.add.assert_called_with(dummy_mock)

        flush_mock.assert_not_called()
        commit_mock.assert_called_once()

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test__entity_manager_insert_commit_true(self, commit_mock,
                                                      flush_mock):
        """Test insert method with commit set to True."""
        dummy_mock = MagicMock()

        result = await self.entity_manager.insert(dummy_mock, commit=True)
        self.assertIsNone(result)

        self.session_mock.add.assert_called_once()
        self.session_mock.add.assert_called_with(dummy_mock)

        flush_mock.assert_called_once()
        commit_mock.assert_called_once()

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test__entity_manager_insert_commit_false(self, commit_mock,
                                                       flush_mock):
        """Test insert method with commit set to False."""
        dummy_mock = MagicMock()

        result = await self.entity_manager.insert(dummy_mock, commit=False)
        self.assertIsNone(result)

        self.session_mock.add.assert_called_once()
        self.session_mock.add.assert_called_with(dummy_mock)

        flush_mock.assert_called_once()
        commit_mock.assert_not_called()

    @patch("app.managers.entity_manager.select")
    async def test__entity_manager_select(self, select_mock):
        """Test select method for fetching a single entity."""
        dummy_mock = MagicMock(id=123)
        dummy_class_mock = MagicMock(id=123)
        async_result_mock = MagicMock()
        async_result_mock.unique.return_value.scalars.return_value.one_or_none.return_value = dummy_mock # noqa E501
        self.session_mock.execute.return_value = async_result_mock

        result = await self.entity_manager.select(dummy_class_mock, 123)
        self.assertEqual(result, dummy_mock)

        select_mock.assert_called_once()
        select_mock.assert_called_with(dummy_class_mock)

        select_mock.return_value.where.assert_called_once()
        select_mock.return_value.where.assert_called_with(True)

        select_mock.return_value.where.return_value.limit.assert_called_once()
        select_mock.return_value.where.return_value.limit.assert_called_with(1)

        async_result_mock.unique.return_value.scalars.return_value.one_or_none.assert_called_once() # noqa E501

    @patch("app.managers.entity_manager.EntityManager._where")
    @patch("app.managers.entity_manager.select")
    async def test__entity_manager_select_by(self, select_mock, where_mock):
        """Test select_by method for fetching a single entity by key."""
        dummy_mock = MagicMock(key="dummy")
        dummy_class_mock = MagicMock()
        async_result_mock = MagicMock()
        async_result_mock.unique.return_value.scalars.return_value.one_or_none.return_value = dummy_mock # noqa E501
        self.session_mock.execute.return_value = async_result_mock

        result = await self.entity_manager.select_by(
            dummy_class_mock, key__eq="dummy")
        self.assertEqual(result, dummy_mock)

        select_mock.assert_called_once()
        select_mock.assert_called_with(dummy_class_mock)

        where_mock.assert_called_once()
        where_mock.assert_called_with(dummy_class_mock, key__eq="dummy")

        select_mock.return_value.where.assert_called_once()
        select_mock.return_value.where.assert_called_with(
            *where_mock.return_value)

        select_mock.return_value.where.return_value.limit.assert_called_once()
        select_mock.return_value.where.return_value.limit.assert_called_with(1)

        async_result_mock.unique.return_value.scalars.return_value.one_or_none.assert_called_once() # noqa E501

    @patch("app.managers.entity_manager.EntityManager._limit")
    @patch("app.managers.entity_manager.EntityManager._offset")
    @patch("app.managers.entity_manager.EntityManager._order_by")
    @patch("app.managers.entity_manager.EntityManager._where")
    @patch("app.managers.entity_manager.select")
    async def test__select_all(self, select_mock, where_mock, order_by_mock,
                               offset_mock, limit_mock):
        """Test select_all method for fetching multiple entities."""
        dummy_mock = MagicMock()
        dummy_class_mock = MagicMock()
        async_result_mock = MagicMock()
        async_result_mock.unique.return_value.scalars.return_value.all.return_value = [dummy_mock] # noqa E501
        self.session_mock.execute.return_value = async_result_mock
        kwargs = {"name__eq": "dummy", "order_by": "id", "order": "asc",
                  "offset": 1, "limit": 2}

        result = await self.entity_manager.select_all(
            dummy_class_mock, **kwargs)
        self.assertListEqual(result, [dummy_mock])

        select_mock.assert_called_once()
        select_mock.assert_called_with(dummy_class_mock)

        where_mock.assert_called_once()
        where_mock.assert_called_with(dummy_class_mock, **kwargs)

        order_by_mock.assert_called_once()
        order_by_mock.assert_called_with(dummy_class_mock, **kwargs)

        offset_mock.assert_called_once()
        offset_mock.assert_called_with(**kwargs)

        limit_mock.assert_called_once()
        limit_mock.assert_called_with(**kwargs)

        select_mock.return_value.where.assert_called_once()
        select_mock.return_value.where.assert_called_with(
            *where_mock.return_value)

        select_mock.return_value.where.return_value.order_by.assert_called_once() # noqa E501
        select_mock.return_value.where.return_value.order_by.assert_called_with(order_by_mock.return_value) # noqa E501

        select_mock.return_value.where.return_value.order_by.return_value.offset.assert_called_once() # noqa E501
        select_mock.return_value.where.return_value.order_by.return_value.offset.assert_called_with(offset_mock.return_value) # noqa E501

        select_mock.return_value.where.return_value.order_by.return_value.offset.return_value.limit.assert_called_once() # noqa E501
        select_mock.return_value.where.return_value.order_by.return_value.offset.return_value.limit.assert_called_with(limit_mock.return_value) # noqa E501

        async_result_mock.unique.return_value.scalars.return_value.all.assert_called_once() # noqa E501

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test__entity_manager_update(self, commit_mock, flush_mock):
        """Test update method without flush and commit."""
        dummy_mock = MagicMock()

        result = await self.entity_manager.update(dummy_mock)
        self.assertIsNone(result)

        self.session_mock.merge.assert_called_once()
        self.session_mock.merge.assert_called_with(dummy_mock)

        flush_mock.assert_called_once()
        commit_mock.assert_not_called()

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test__entity_manager_update_flush_true(self, commit_mock,
                                                     flush_mock):
        """Test update method with flush set to True."""
        dummy_mock = MagicMock()

        result = await self.entity_manager.update(dummy_mock, flush=True)
        self.assertIsNone(result)

        self.session_mock.merge.assert_called_once()
        self.session_mock.merge.assert_called_with(dummy_mock)

        flush_mock.assert_called_once()
        commit_mock.assert_not_called()

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test__entity_manager_update_flush_false(self, commit_mock,
                                                      flush_mock):
        """Test update method with flush set to False."""
        dummy_mock = MagicMock()

        result = await self.entity_manager.update(dummy_mock, flush=False)
        self.assertIsNone(result)

        self.session_mock.merge.assert_called_once()
        self.session_mock.merge.assert_called_with(dummy_mock)

        flush_mock.assert_not_called()
        commit_mock.assert_not_called()

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test__entity_manager_update_commit_true(self, commit_mock,
                                                      flush_mock):
        """Test update method with commit set to True."""
        dummy_mock = MagicMock()

        result = await self.entity_manager.update(dummy_mock, commit=True)
        self.assertIsNone(result)

        self.session_mock.merge.assert_called_once()
        self.session_mock.merge.assert_called_with(dummy_mock)

        flush_mock.assert_called_once()
        commit_mock.assert_called_once()

    @patch("app.managers.entity_manager.EntityManager.flush")
    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test__entity_manager_update_commit_false(self, commit_mock,
                                                       flush_mock):
        """Test update method with commit set to False."""
        dummy_mock = MagicMock()

        result = await self.entity_manager.update(dummy_mock, commit=False)
        self.assertIsNone(result)

        self.session_mock.merge.assert_called_once()
        self.session_mock.merge.assert_called_with(dummy_mock)

        flush_mock.assert_called_once()
        commit_mock.assert_not_called()

    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test__entity_manager_delete(self, commit_mock):
        """Test delete method without commit."""
        dummy_mock = MagicMock()

        result = await self.entity_manager.delete(dummy_mock)
        self.assertIsNone(result)

        self.session_mock.delete.assert_called_once()
        self.session_mock.delete.assert_called_with(dummy_mock)

        commit_mock.assert_not_called()

    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test__entity_manager_delete_commit_true(self, commit_mock):
        """Test delete method with commit set to True."""
        dummy_mock = MagicMock()

        result = await self.entity_manager.delete(dummy_mock, commit=True)
        self.assertIsNone(result)

        self.session_mock.delete.assert_called_once()
        self.session_mock.delete.assert_called_with(dummy_mock)

        commit_mock.assert_called_once()

    @patch("app.managers.entity_manager.EntityManager.commit")
    async def test__entity_manager_delete_commit_false(self, commit_mock):
        """Test delete method with commit set to False."""
        dummy_mock = MagicMock()

        result = await self.entity_manager.delete(dummy_mock, commit=False)
        self.assertIsNone(result)

        self.session_mock.delete.assert_called_once()
        self.session_mock.delete.assert_called_with(dummy_mock)

        commit_mock.assert_not_called()

    @patch("app.managers.entity_manager.EntityManager.delete")
    @patch("app.managers.entity_manager.EntityManager.select_all")
    async def test__delete_all(self, select_all_mock, delete_mock):
        """Test delete_all method for deleting multiple entities."""
        from app.managers.entity_manager import DELETE_ALL_BATCH_SIZE

        dummy_class_mock = MagicMock()
        entity_1, entity_2, entity_3 = MagicMock(), MagicMock(), MagicMock()
        select_all_mock.side_effect = [[entity_1, entity_2], [entity_3], []]

        result = await self.entity_manager.delete_all(
            dummy_class_mock, name__eq="dummy")
        self.assertIsNone(result)

        self.assertEqual(select_all_mock.call_count, 3)
        self.assertListEqual(select_all_mock.call_args_list, [
            call(dummy_class_mock, name__eq="dummy",
                 order_by="id", order="asc",
                 offset=0, limit=DELETE_ALL_BATCH_SIZE),
            call(dummy_class_mock, name__eq="dummy",
                 order_by="id", order="asc",
                 offset=DELETE_ALL_BATCH_SIZE, limit=DELETE_ALL_BATCH_SIZE),
            call(dummy_class_mock, name__eq="dummy",
                 order_by="id", order="asc",
                 offset=DELETE_ALL_BATCH_SIZE * 2,
                 limit=DELETE_ALL_BATCH_SIZE)])

        self.assertEqual(delete_mock.call_count, 3)
        self.assertListEqual(delete_mock.call_args_list, [
            call(entity_1, commit=False),
            call(entity_2, commit=False),
            call(entity_3, commit=False),
        ])

    @patch("app.managers.entity_manager.EntityManager.delete")
    @patch("app.managers.entity_manager.EntityManager.select_all")
    async def test__delete_all_commit_true(self, select_all_mock, delete_mock):
        """Test delete_all method with commit set to True."""
        from app.managers.entity_manager import DELETE_ALL_BATCH_SIZE

        dummy_class_mock = MagicMock()
        entity_1, entity_2, entity_3 = MagicMock(), MagicMock(), MagicMock()
        select_all_mock.side_effect = [[entity_1, entity_2], [entity_3], []]

        result = await self.entity_manager.delete_all(
            dummy_class_mock, commit=True, name__eq="dummy")
        self.assertIsNone(result)

        self.assertEqual(select_all_mock.call_count, 3)
        self.assertListEqual(select_all_mock.call_args_list, [
            call(dummy_class_mock, name__eq="dummy",
                 order_by="id", order="asc",
                 offset=0, limit=DELETE_ALL_BATCH_SIZE),
            call(dummy_class_mock, name__eq="dummy",
                 order_by="id", order="asc",
                 offset=DELETE_ALL_BATCH_SIZE, limit=DELETE_ALL_BATCH_SIZE),
            call(dummy_class_mock, name__eq="dummy",
                 order_by="id", order="asc",
                 offset=DELETE_ALL_BATCH_SIZE * 2,
                 limit=DELETE_ALL_BATCH_SIZE)])

        self.assertEqual(delete_mock.call_count, 3)
        self.assertListEqual(delete_mock.call_args_list, [
            call(entity_1, commit=True),
            call(entity_2, commit=True),
            call(entity_3, commit=True),
        ])

    @patch("app.managers.entity_manager.EntityManager.delete")
    @patch("app.managers.entity_manager.EntityManager.select_all")
    async def test__delete_all_commit_false(self, select_all_mock,
                                            delete_mock):
        """Test delete_all method with commit set to False."""
        from app.managers.entity_manager import DELETE_ALL_BATCH_SIZE

        dummy_class_mock = MagicMock()
        entity_1, entity_2, entity_3 = MagicMock(), MagicMock(), MagicMock()
        select_all_mock.side_effect = [[entity_1, entity_2], [entity_3], []]

        result = await self.entity_manager.delete_all(
            dummy_class_mock, commit=False, name__eq="dummy")
        self.assertIsNone(result)

        self.assertEqual(select_all_mock.call_count, 3)
        self.assertListEqual(select_all_mock.call_args_list, [
            call(dummy_class_mock, name__eq="dummy",
                 order_by="id", order="asc",
                 offset=0, limit=DELETE_ALL_BATCH_SIZE),
            call(dummy_class_mock, name__eq="dummy",
                 order_by="id", order="asc",
                 offset=DELETE_ALL_BATCH_SIZE, limit=DELETE_ALL_BATCH_SIZE),
            call(dummy_class_mock, name__eq="dummy",
                 order_by="id", order="asc",
                 offset=DELETE_ALL_BATCH_SIZE * 2,
                 limit=DELETE_ALL_BATCH_SIZE)])

        self.assertEqual(delete_mock.call_count, 3)
        self.assertListEqual(delete_mock.call_args_list, [
            call(entity_1, commit=False),
            call(entity_2, commit=False),
            call(entity_3, commit=False),
        ])

    @patch("app.managers.entity_manager.EntityManager._where")
    @patch("app.managers.entity_manager.func")
    @patch("app.managers.entity_manager.select")
    async def test__count_all(self, select_mock, func_mock, where_mock):
        """Test count_all method for counting entities."""
        dummy_class_mock = MagicMock(id=1)
        async_result_mock = MagicMock()
        async_result_mock.unique.return_value.scalars.return_value.one_or_none.return_value = 123 # noqa E501
        self.session_mock.execute.return_value = async_result_mock
        kwargs = {"name__eq": "dummy"}

        result = await self.entity_manager.count_all(
            dummy_class_mock, **kwargs)
        self.assertEqual(result, 123)

        func_mock.count.assert_called_once()
        func_mock.count.assert_called_with(dummy_class_mock.id)

        where_mock.assert_called_once()
        where_mock.assert_called_with(dummy_class_mock, **kwargs)

        select_mock.assert_called_once()
        select_mock.assert_called_with(func_mock.count.return_value)

        select_mock.return_value.where.assert_called_once()
        select_mock.return_value.where.assert_called_with(
            *where_mock.return_value)

        async_result_mock.unique.return_value.scalars.return_value.one_or_none.assert_called_once() # noqa E501

    @patch("app.managers.entity_manager.EntityManager._where")
    @patch("app.managers.entity_manager.func")
    @patch("app.managers.entity_manager.select")
    async def test__count_all_none(self, select_mock, func_mock, where_mock):
        """Test count_all method when no entities are counted."""
        dummy_class_mock = MagicMock(id=1)
        async_result_mock = MagicMock()
        async_result_mock.unique.return_value.scalars.return_value.one_or_none.return_value = None # noqa E501
        self.session_mock.execute.return_value = async_result_mock
        kwargs = {"name__eq": "dummy"}

        result = await self.entity_manager.count_all(
            dummy_class_mock, **kwargs)
        self.assertEqual(result, 0)

        func_mock.count.assert_called_once()
        func_mock.count.assert_called_with(dummy_class_mock.id)

        where_mock.assert_called_once()
        where_mock.assert_called_with(dummy_class_mock, **kwargs)

        select_mock.assert_called_once()
        select_mock.assert_called_with(func_mock.count.return_value)

        select_mock.return_value.where.assert_called_once()
        select_mock.return_value.where.assert_called_with(
            *where_mock.return_value)

        async_result_mock.unique.return_value.scalars.return_value.one_or_none.assert_called_once() # noqa E501

    @patch("app.managers.entity_manager.EntityManager._where")
    @patch("app.managers.entity_manager.func")
    @patch("app.managers.entity_manager.select")
    async def test__sum_all(self, select_mock, func_mock, where_mock):
        """Test sum_all method for summing values of a column."""
        dummy_class_mock = MagicMock(name="dummy", number=1)
        async_result_mock = MagicMock()
        async_result_mock.unique.return_value.scalars.return_value.one_or_none.return_value = 123 # noqa E501
        self.session_mock.execute.return_value = async_result_mock
        kwargs = {"name__eq": "dummy"}

        result = await self.entity_manager.sum_all(
            dummy_class_mock, "number", **kwargs)
        self.assertEqual(result, 123)

        func_mock.sum.assert_called_once()
        func_mock.sum.assert_called_with(dummy_class_mock.number)

        where_mock.assert_called_once()
        where_mock.assert_called_with(dummy_class_mock, **kwargs)

        select_mock.assert_called_once()
        select_mock.assert_called_with(func_mock.sum.return_value)

        select_mock.return_value.where.assert_called_once()
        select_mock.return_value.where.assert_called_with(
            *where_mock.return_value)

        async_result_mock.unique.return_value.scalars.return_value.one_or_none.assert_called_once() # noqa E501

    @patch("app.managers.entity_manager.EntityManager._where")
    @patch("app.managers.entity_manager.func")
    @patch("app.managers.entity_manager.select")
    async def test__sum_all_none(self, select_mock, func_mock, where_mock):
        """Test sum_all method when no values are summed."""
        dummy_class_mock = MagicMock(name="dummy", number=1)
        async_result_mock = MagicMock()
        async_result_mock.unique.return_value.scalars.return_value.one_or_none.return_value = None # noqa E501
        self.session_mock.execute.return_value = async_result_mock
        kwargs = {"name__eq": "dummy"}

        result = await self.entity_manager.sum_all(dummy_class_mock, "number",
                                                   **kwargs)
        self.assertEqual(result, 0)

        func_mock.sum.assert_called_once()
        func_mock.sum.assert_called_with(dummy_class_mock.number)

        where_mock.assert_called_once()
        where_mock.assert_called_with(dummy_class_mock, **kwargs)

        select_mock.assert_called_once()
        select_mock.assert_called_with(func_mock.sum.return_value)

        select_mock.return_value.where.assert_called_once()
        select_mock.return_value.where.assert_called_with(
            *where_mock.return_value)

        async_result_mock.unique.return_value.scalars.return_value.one_or_none.assert_called_once() # noqa E501

    @patch("app.managers.entity_manager.text")
    async def test_lock_all(self, text_mock):
        """Test lock_all method for locking tables."""
        dummy_class_mock = MagicMock(__tablename__="dummies")
        text_mock.return_value = "LOCK TABLE dummies IN ACCESS EXCLUSIVE MODE;"

        result = await self.entity_manager.lock_all(dummy_class_mock)
        self.assertIsNone(result)

        self.session_mock.execute.assert_called_once()
        self.session_mock.execute.assert_called_with(text_mock.return_value)

        text_mock.assert_called_once()
        text_mock.assert_called_with(
            "LOCK TABLE dummies IN ACCESS EXCLUSIVE MODE;")

    async def test__flush(self):
        """Test flush method."""
        result = await self.entity_manager.flush()
        self.assertIsNone(result)
        self.session_mock.flush.assert_called_once()

    async def test__commit(self):
        """Test commit method."""
        result = await self.entity_manager.commit()
        self.assertIsNone(result)
        self.session_mock.commit.assert_called_once()

    async def test__rollback(self):
        """Test rollback method."""
        result = await self.entity_manager.rollback()
        self.assertIsNone(result)
        self.session_mock.rollback.assert_called_once()

    async def test__where(self):
        """Test _where method for building filter conditions."""
        (in_mock, eq_mock, ne_mock, ge_mock, le_mock, gt_mock, lt_mock,
         like_mock, ilike_mock) = (
            MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock(),
            MagicMock(), MagicMock(), MagicMock(), MagicMock())
        column_mock = MagicMock(
            in_=in_mock, __eq__=eq_mock, __ne__=ne_mock, __ge__=ge_mock,
            __le__=le_mock, __gt__=gt_mock, __lt__=lt_mock, like=like_mock,
            ilike=ilike_mock)
        dummy_class_mock = MagicMock(column=column_mock)
        kwargs = {
            "column__in": "1, 2",
            "column__eq": "3",
            "column__ne": "4",
            "column__ge": "5",
            "column__le": "6",
            "column__gt": "7",
            "column__lt": "8",
            "column__like": "dummy",
            "column__ilike": "dummy",
        }

        result = self.entity_manager._where(dummy_class_mock, **kwargs)
        self.assertListEqual(result, [
            in_mock.return_value,
            eq_mock.return_value,
            ne_mock.return_value,
            ge_mock.return_value,
            le_mock.return_value,
            gt_mock.return_value,
            lt_mock.return_value,
            like_mock.return_value,
            ilike_mock.return_value,
        ])

        in_mock.assert_called_once()
        in_mock.assert_called_with([
            x.strip() for x in kwargs["column__in"].split(",")])

        eq_mock.assert_called_once()
        eq_mock.assert_called_with(kwargs["column__eq"])

        ne_mock.assert_called_once()
        ne_mock.assert_called_with(kwargs["column__ne"])

        ge_mock.assert_called_once()
        ge_mock.assert_called_with(kwargs["column__ge"])

        le_mock.assert_called_once()
        le_mock.assert_called_with(kwargs["column__le"])

        gt_mock.assert_called_once()
        gt_mock.assert_called_with(kwargs["column__gt"])

        lt_mock.assert_called_once()
        lt_mock.assert_called_with(kwargs["column__lt"])

        like_mock.assert_called_once()
        like_mock.assert_called_with("%" + kwargs["column__like"] + "%")

        ilike_mock.assert_called_once()
        ilike_mock.assert_called_with("%" + kwargs["column__ilike"] + "%")

    @patch("app.managers.entity_manager.asc")
    async def test__order_by_asc(self, asc_mock):
        """Test _order_by method for ascending order."""
        column_mock = MagicMock()
        dummy_class_mock = MagicMock(column=column_mock)
        kwargs = {"order_by": "column", "order": "asc"}
        result = self.entity_manager._order_by(dummy_class_mock, **kwargs)

        self.assertEqual(result, asc_mock.return_value)
        asc_mock.assert_called_once()
        asc_mock.assert_called_with(column_mock)

    @patch("app.managers.entity_manager.desc")
    async def test__order_by_desc(self, desc_mock):
        """Test _order_by method for descending order."""
        column_mock = MagicMock()
        dummy_class_mock = MagicMock(column=column_mock)
        kwargs = {"order_by": "column", "order": "desc"}

        result = self.entity_manager._order_by(dummy_class_mock, **kwargs)
        self.assertEqual(result, desc_mock.return_value)

        desc_mock.assert_called_once()
        desc_mock.assert_called_with(column_mock)

    async def test__offset(self):
        """Test _offset method for setting offset."""
        kwargs = {"offset": 123}
        result = self.entity_manager._offset(**kwargs)
        self.assertEqual(result, 123)

    async def test__limit(self):
        """Test _limit method for setting limit."""
        kwargs = {"limit": 123}
        result = self.entity_manager._limit(**kwargs)
        self.assertEqual(result, 123)


if __name__ == '__main__':
    unittest.main()
