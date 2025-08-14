import unittest
from stripe.balance import retrieve_balance
from stripe.SimulationEngine.db import DB
from stripe.SimulationEngine.models import Balance,BalanceAmountBySourceType
from common_utils.base_case import BaseTestCaseWithErrorHandler


class TestRetrieveBalance(BaseTestCaseWithErrorHandler):

    def setUp(self):
        self.DB = DB  # Assign global DB to self.DB
        self.DB.clear()  # Clears everything from the global DB instance

        # Initialize default balance structure for this test instance's view of DB
        # This structure is based on the Pydantic Balance model and the function's docstring.
        self.DB['balance'] = {
            "object": "balance",
            "available": [],
            "pending": [],
            "livemode": False
        }

    def test_retrieve_empty_balance(self):
        # The DB is already set up for an empty balance in self.setUp.
        expected_balance = Balance()

        retrieved_balance_dict = retrieve_balance()
        # Convert retrieved dict to a Balance model for validation
        retrieved_balance = Balance(**retrieved_balance_dict)

        # Verify model validation passes
        self.assertEqual(retrieved_balance.model_dump(), expected_balance.model_dump())

    def test_retrieve_balance_with_available_funds_single_currency(self):
        available_fund = BalanceAmountBySourceType(amount=10000, currency="usd", source_types={"card": 10000})
        balance_model = Balance(available=[available_fund])
        
        self.DB['balance'] = balance_model.model_dump()

        retrieved_balance_dict = retrieve_balance()
        # Convert retrieved dict to a Balance model for validation
        retrieved_balance = Balance(**retrieved_balance_dict)

        self.assertEqual(retrieved_balance.model_dump(), balance_model.model_dump())
        self.assertEqual(retrieved_balance.available[0].source_types, {"card": 10000})

    def test_retrieve_balance_with_available_funds_multiple_currencies(self):
        available_funds = [
            BalanceAmountBySourceType(amount=10000, currency="usd", source_types={"card": 10000}),
            BalanceAmountBySourceType(amount=5000, currency="eur", source_types={"bank_account": 5000})
        ]
        balance_model = Balance(available=available_funds)
        
        self.DB['balance'] = balance_model.model_dump()

        retrieved_balance_dict = retrieve_balance()
        retrieved_balance = Balance(**retrieved_balance_dict)

        self.assertEqual(retrieved_balance.model_dump(), balance_model.model_dump())

    def test_retrieve_balance_with_pending_funds_single_currency(self):
        pending_fund = BalanceAmountBySourceType(amount=2000, currency="gbp", source_types={"fpx": 2000})
        balance_model = Balance(pending=[pending_fund])
        
        self.DB['balance'] = balance_model.model_dump()

        retrieved_balance_dict = retrieve_balance()
        retrieved_balance = Balance(**retrieved_balance_dict)

        self.assertEqual(retrieved_balance.model_dump(), balance_model.model_dump())
        self.assertEqual(retrieved_balance.pending[0].source_types, {"fpx": 2000})

    def test_retrieve_balance_with_pending_funds_multiple_currencies_and_optional_source_types(self):
        # This test covers one item with source_types and one without (will be None)
        pending_funds = [
            BalanceAmountBySourceType(amount=2000, currency="gbp", source_types={"fpx": 2000}),
            BalanceAmountBySourceType(amount=3000, currency="jpy")  # source_types will be None
        ]
        balance_model = Balance(pending=pending_funds)
        
        self.DB['balance'] = balance_model.model_dump()

        retrieved_balance_dict = retrieve_balance()
        retrieved_balance = Balance(**retrieved_balance_dict)

        self.assertEqual(retrieved_balance.model_dump(), balance_model.model_dump())
        self.assertEqual(retrieved_balance.pending[0].source_types, {"fpx": 2000})
        self.assertIsNone(retrieved_balance.pending[1].source_types)

    def test_retrieve_balance_with_both_available_and_pending_funds(self):
        available_fund = BalanceAmountBySourceType(amount=10000, currency="usd", source_types={"card": 10000})
        pending_fund = BalanceAmountBySourceType(amount=2000, currency="gbp")  # source_types will be None
        
        balance_model = Balance(
            available=[available_fund],
            pending=[pending_fund]
        )
        
        self.DB['balance'] = balance_model.model_dump()

        retrieved_balance_dict = retrieve_balance()
        retrieved_balance = Balance(**retrieved_balance_dict)

        self.assertEqual(retrieved_balance.model_dump(), balance_model.model_dump())

    def test_retrieve_balance_livemode_true(self):
        available_fund = BalanceAmountBySourceType(amount=100, currency="usd")
        balance_model = Balance(
            available=[available_fund],
            livemode=True
        )
        
        self.DB['balance'] = balance_model.model_dump()

        retrieved_balance_dict = retrieve_balance()
        retrieved_balance = Balance(**retrieved_balance_dict)

        self.assertEqual(retrieved_balance.model_dump(), balance_model.model_dump())
        self.assertTrue(retrieved_balance.livemode)

    def test_retrieve_balance_with_source_types_explicitly_none(self):
        # This test covers items where source_types is explicitly None.
        available_fund = BalanceAmountBySourceType(amount=7000, currency="cad", source_types=None)
        pending_fund = BalanceAmountBySourceType(amount=1500, currency="aud", source_types=None)
        
        balance_model = Balance(
            available=[available_fund],
            pending=[pending_fund]
        )
        
        self.DB['balance'] = balance_model.model_dump()

        retrieved_balance_dict = retrieve_balance()
        retrieved_balance = Balance(**retrieved_balance_dict)

        self.assertEqual(retrieved_balance.model_dump(), balance_model.model_dump())
        self.assertIsNone(retrieved_balance.available[0].source_types)
        self.assertIsNone(retrieved_balance.pending[0].source_types)

    def test_retrieve_balance_with_source_types_empty_dict(self):
        # This test covers items where source_types is an empty dictionary.
        available_fund = BalanceAmountBySourceType(amount=8000, currency="nzd", source_types={})
        
        balance_model = Balance(available=[available_fund])
        
        self.DB['balance'] = balance_model.model_dump()

        retrieved_balance_dict = retrieve_balance()
        retrieved_balance = Balance(**retrieved_balance_dict)

        self.assertEqual(retrieved_balance.model_dump(), balance_model.model_dump())
        self.assertEqual(retrieved_balance.available[0].source_types, {})
    


if __name__ == '__main__':
    unittest.main()