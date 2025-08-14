"""
Database structure and persistence helpers for Workday Strategic Sourcing API Simulation.
"""

import json
from typing import Dict, Any
import os

# ---------------------------------------------------------------------------------------
# In-Memory Database Structure
# ---------------------------------------------------------------------------------------
DB: Dict[str, Any] = {
    'attachments': {},
    'awards': {'award_line_items': [], 'awards': []},
    'contracts': {'award_line_items': [],
                'awards': {},
                'contract_types': {},
                'contracts': {}},
    'events': {'bid_line_items': {},
                'bids': {},
                'event_templates': {},
                'events': {},
                'line_items': {},
                'worksheets': {}},
    'fields': {'field_groups': {}, 'field_options': {}, 'fields': {}},
    'payments': {'payment_currencies': [],
                'payment_currency_id_counter': "",
                'payment_term_id_counter': "",
                'payment_terms': [],
                'payment_type_id_counter': "",
                'payment_types': []},
    'projects': {'project_types': {}, 'projects': {}},
    'reports': {'contract_milestone_reports_entries': [],
                'contract_milestone_reports_schema': {},
                'contract_reports_entries': [],
                'contract_reports_schema': {},
                'event_reports': [],
                'event_reports_1_entries': [],
                'event_reports_entries': [],
                'event_reports_schema': {},
                'performance_review_answer_reports_entries': [],
                'performance_review_answer_reports_schema': {},
                'performance_review_reports_entries': [],
                'performance_review_reports_schema': {},
                'project_milestone_reports_entries': [],
                'project_milestone_reports_schema': {},
                'project_reports_1_entries': [],
                'project_reports_entries': [],
                'project_reports_schema': {},
                'savings_reports_entries': [],
                'savings_reports_schema': {},
                'supplier_reports_entries': [],
                'supplier_reports_schema': {},
                'supplier_review_reports_entries': [],
                'supplier_review_reports_schema': {},
                'suppliers': []},
    'scim': {'resource_types': [],
            'schemas': [],
            'service_provider_config': {},
            'users': []},
    'spend_categories': {},
    'suppliers': {'contact_types': {},
                'supplier_companies': {},
                'supplier_company_segmentations': {},
                'supplier_contacts': {}}}

# -------------------------------------------------------------------
# Persistence Helpers
# -------------------------------------------------------------------
def save_state(filepath: str) -> None:
    """Saves the current state of the API to a JSON file."""
    with open(filepath, "w") as f:
        json.dump(DB, f)


def load_state(filepath: str) -> object:
    """Loads the API state from a JSON file."""
    try:
        with open(filepath, "r") as f:
            global DB
            state = json.load(f)
        # Instead of reassigning DB, update it in place:
        DB.clear()
        DB.update(state)
        
    except FileNotFoundError:
        pass 

