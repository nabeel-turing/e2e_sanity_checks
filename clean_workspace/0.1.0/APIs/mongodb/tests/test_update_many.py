# APIs/mongodb/tests/test_update_many.py
"""
High-coverage tests for data_operations.update_many.

* Exercises all success & error paths
* Verifies every rule in UpdateManyInput (Pydantic)
* update_many itself ends up at 100 % branch / line coverage
"""

import unittest
from unittest.mock import patch

import mongomock
from pymongo.errors import OperationFailure, WriteError
from pydantic import ValidationError

from ..data_operations import update_many
from ..SimulationEngine.custom_errors import InvalidQueryError, InvalidUpdateError

PATCH_CONN = "mongodb.data_operations.utils.get_active_connection"


class TestUpdateManyOperation(unittest.TestCase):
    # ------------------------------------------------------------ #
    #       shared in-memory Mongo and connection patch            #
    # ------------------------------------------------------------ #
    @classmethod
    def setUpClass(cls):
        cls._mongo = mongomock.MongoClient()
        cls._patcher = patch(PATCH_CONN, return_value=cls._mongo)
        cls._patcher.start()

    @classmethod
    def tearDownClass(cls):
        cls._patcher.stop()

    DB = "itest_db"
    COLL = "ut_coll"

    def _coll(self):
        return self._mongo[self.DB][self.COLL]

    def setUp(self):
        self._coll().delete_many({})
        self._coll().insert_many(
            [
                {"_id": 1, "counter": 0, "tag": "a"},
                {"_id": 2, "counter": 0, "tag": "b"},
                {"_id": 3, "counter": 0, "tag": "b"},
            ]
        )

    # ------------------------------------------------------------ #
    #                        success paths                         #
    # ------------------------------------------------------------ #
    def test_increment_two_docs(self):
        res = update_many(
            self.DB, self.COLL, filter={"tag": "b"}, update={"$inc": {"counter": 1}}
        )
        self.assertEqual(
            res["content"][0]["text"], "Matched 2 document(s). Modified 2 document(s)."
        )
        self.assertTrue(
            all(d["counter"] == 1 for d in self._coll().find({"tag": "b"}))
        )

    def test_match_but_no_modify(self):
        msg = update_many(
            self.DB, self.COLL, filter={"tag": "a"}, update={"$set": {"counter": 0}}
        )["content"][0]["text"]
        self.assertEqual(msg, "Matched 1 document(s).")

    def test_no_match(self):
        msg = update_many(
            self.DB, self.COLL, filter={"tag": "zzz"}, update={"$set": {"flag": True}}
        )["content"][0]["text"]
        self.assertEqual(msg, "No documents matched the filter.")

    def test_upsert(self):
        res = update_many(
            self.DB,
            self.COLL,
            filter={"tag": "new"},
            update={"$set": {"tag": "new", "counter": 7}},
            upsert=True,
        )
        self.assertIn("Upserted 1 document with id:", res["content"][0]["text"])
        self.assertEqual(self._coll().count_documents({"tag": "new"}), 1)

    # ------------------------------------------------------------ #
    #                client-side validation errors                 #
    # ------------------------------------------------------------ #
    def test_empty_update_dict(self):
        with self.assertRaises(InvalidUpdateError) as ctx:
            update_many(self.DB, self.COLL, update={}, filter={})
        self.assertIn("update cannot be empty", str(ctx.exception))

    # ------------------------------------------------------------ #
    #                server-side / wrapper error paths             #
    # ------------------------------------------------------------ #
    def _raise_and_expect(self, exc, exp_cls, substr):
        with patch.object(self._coll(), "update_many", side_effect=exc):
            with self.assertRaises(exp_cls) as caught:
                update_many(self.DB, self.COLL, update={"$set": {"x": 1}}, filter={})
        if substr:
            self.assertIn(substr, str(caught.exception))

    def test_invalid_filter_error_code_2(self):
        self._raise_and_expect(
            OperationFailure("BadValue", code=2),
            InvalidQueryError,
            "Invalid 'filter' document",
        )

    def test_invalid_update_error_code_9(self):
        self._raise_and_expect(
            OperationFailure("Unknown modifier: $bad", code=9),
            InvalidUpdateError,
            "Invalid 'update' document",
        )

    def test_write_error_immutable_field(self):
        self._raise_and_expect(
            WriteError("immutable field", code=66),
            InvalidUpdateError,
            "immutable field",
        )

    def test_generic_operation_failure(self):
        self._raise_and_expect(
            OperationFailure("weird", code=80),
            InvalidUpdateError,
            "Update operation failed",
        )

    # ------------------------------------------------------------ #
    #                pydantic field-level validation               #
    # ------------------------------------------------------------ #
    def _expect_validation_error(self, **kwargs):
        with self.assertRaises(ValidationError):
            update_many(**kwargs)

    def test_db_name_empty(self):
        self._expect_validation_error(
            database="", collection=self.COLL, update={"$set": {"x": 1}}
        )

    def test_db_name_too_long(self):
        self._expect_validation_error(
            database="x" * 64, collection=self.COLL, update={"$set": {"x": 1}}
        )

    def test_collection_name_empty(self):
        self._expect_validation_error(
            database=self.DB, collection="", update={"$set": {"x": 1}}
        )

    def test_collection_name_too_long(self):
        self._expect_validation_error(
            database=self.DB, collection="y" * 256, update={"$set": {"x": 1}}
        )

    def test_filter_not_a_dict(self):
        self._expect_validation_error(
            database=self.DB, collection=self.COLL, filter=["not", "dict"], update={"$set": {"x": 1}}
        )

    # ------------------------------------------------------------ #
    #          missing-argument (python‐level) safeguard           #
    # ------------------------------------------------------------ #
    def test_missing_required_argument(self):
        with self.assertRaises(TypeError):
            update_many(collection=self.COLL, update={"$set": {"x": 1}})


if __name__ == "__main__":
    unittest.main()