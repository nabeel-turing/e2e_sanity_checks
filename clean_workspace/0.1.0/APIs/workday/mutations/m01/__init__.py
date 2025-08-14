from .Attachments import fetch_attachment_by_external_id, fetch_attachment_by_internal_id, find_all_attachments_by_id_filter, get_attachments_by_id_list, modify_attachment_by_external_id, modify_attachment_by_internal_id, remove_attachment_by_external_id, remove_attachment_by_internal_id, upload_new_attachment
from .Awards import fetch_award_line_item_by_id, find_awards_by_criteria, get_line_items_for_award
from .BidLineItemById import fetch_bid_line_item_details
from .BidLineItems import retrieve_line_items_for_bid
from .BidLineItemsDescribe import get_bid_line_item_schema_fields
from .BidLineItemsList import retrieve_all_bid_line_items_with_filter
from .BidsById import fetch_bid_details_by_id
from .BidsDescribe import get_bid_schema_fields
from .ContactTypeByExternalId import modify_contact_category_by_external_id, remove_contact_category_by_external_id
from .ContactTypeById import delete_contact_category_by_id, update_contact_category_by_id
from .ContactTypes import register_new_contact_type, retrieve_all_contact_types
from .ContractAward import fetch_contract_award_details, fetch_contract_award_line_item_details, get_line_items_for_contract_award, retrieve_all_contract_awards
from .ContractMilestoneReports import fetch_contract_milestone_schema, get_all_contract_milestone_entries
from .ContractReports import fetch_contract_report_schema, retrieve_contract_report_data
from .Contracts import describe_contract_object_fields, fetch_contract_by_external_id, fetch_contract_by_internal_id, fetch_contract_type_by_external_id, fetch_contract_type_by_internal_id, find_contracts_with_filters, modify_contract_by_external_id, modify_contract_by_internal_id, modify_contract_type_by_external_id, modify_contract_type_by_internal_id, register_new_contract, register_new_contract_type, remove_contract_by_external_id, remove_contract_by_internal_id, remove_contract_type_by_external_id, remove_contract_type_by_internal_id, retrieve_all_contract_types
from .EventBids import retrieve_bids_for_event
from .EventReports import fetch_event_report_schema, get_all_event_report_entries, get_entries_for_event_report, get_my_event_report_entries
from .EventSupplierCompanies import assign_suppliers_to_event_by_id, unassign_suppliers_from_event_by_id
from .EventSupplierCompaniesExternalId import assign_suppliers_to_event_by_external_id, unassign_suppliers_from_event_by_external_id
from .EventSupplierContacts import assign_contacts_to_event_by_id, unassign_contacts_from_event_by_id
from .EventSupplierContactsExternalId import assign_contacts_to_event_by_external_ids, unassign_contacts_from_event_by_external_ids
from .EventTemplates import fetch_event_template_details, get_all_event_templates
from .EventWorksheetById import fetch_event_worksheet_details
from .EventWorksheetLineItemById import fetch_worksheet_line_item_details, modify_worksheet_line_item_details, remove_worksheet_line_item
from .EventWorksheetLineItems import add_line_item_to_event_worksheet, add_multiple_line_items_to_worksheet, get_line_items_for_event_worksheet
from .EventWorksheets import retrieve_worksheets_for_event
from .Events import fetch_event_details_by_id, find_events_by_criteria, modify_event_details_by_id, register_new_event, remove_event_by_id
from .FieldByExternalId import fetch_field_by_external_id, modify_field_by_external_id, remove_field_by_external_id
from .FieldById import modify_field_properties_by_id, remove_field_by_internal_id, retrieve_field_properties_by_id
from .FieldGroupById import fetch_field_group_details, modify_field_group_by_identifier, remove_field_group_from_system
from .FieldGroups import register_new_field_group, retrieve_all_field_groups
from .FieldOptionById import modify_field_options_by_id, remove_field_options_by_id
from .FieldOptions import add_options_to_field
from .FieldOptionsByFieldId import retrieve_options_for_field
from .Fields import define_new_custom_field, get_custom_fields_with_filter
from .PaymentCurrencies import get_all_payment_currencies, register_new_payment_currency
from .PaymentCurrenciesExternalId import modify_currency_by_external_ref, remove_currency_by_external_ref
from .PaymentCurrenciesId import modify_currency_by_internal_id, remove_currency_by_internal_id
from .PaymentTerms import get_all_payment_terms, register_new_payment_term
from .PaymentTermsExternalId import modify_payment_term_by_external_ref, remove_payment_term_by_external_ref
from .PaymentTermsId import modify_payment_term_by_id, remove_payment_term_by_id
from .PaymentTypes import get_all_payment_types, register_new_payment_type
from .PaymentTypesExternalId import modify_payment_method_by_external_ref, remove_payment_method_by_external_ref
from .PaymentTypesId import modify_payment_type_by_id, remove_payment_type_by_id
from .PerformanceReviewAnswerReports import fetch_performance_review_answer_schema, get_all_performance_review_answer_entries
from .PerformanceReviewReports import fetch_performance_review_schema, get_all_performance_review_entries
from .ProjectByExternalId import fetch_project_by_external_id, modify_project_by_external_id, remove_project_by_external_id
from .ProjectById import fetch_project_by_internal_id, modify_project_by_internal_id, remove_project_by_internal_id
from .ProjectMilestoneReports import fetch_project_milestone_schema, get_all_project_milestone_entries
from .ProjectRelationshipsSupplierCompanies import assign_companies_to_project, unassign_companies_from_project
from .ProjectRelationshipsSupplierCompaniesExternalId import link_suppliers_to_project_by_external_ref, unlink_suppliers_from_project_by_external_ref
from .ProjectRelationshipsSupplierContacts import assign_contacts_to_project_by_internal_id, unassign_contacts_from_project_by_internal_id
from .ProjectRelationshipsSupplierContactsExternalId import assign_contacts_to_project_by_external_refs, unassign_contacts_from_project_by_external_refs
from .ProjectReports import fetch_project_report_schema, get_entries_for_project_report, get_my_project_report_entries
from .ProjectTypeById import fetch_project_category_by_id
from .ProjectTypes import get_all_project_types
from .Projects import find_projects_with_filters, register_new_project
from .ProjectsDescribe import describe_project_object_fields
from .ResourceTypeById import fetch_scim_resource_metadata
from .ResourceTypes import fetch_scim_resource_type_by_name, get_all_scim_resource_types
from .SavingsReports import fetch_savings_report_schema, get_all_savings_report_entries
from .SchemaById import fetch_scim_schema_by_uri
from .Schemas import retrieve_all_scim_schemas
from .ServiceProviderConfig import fetch_scim_provider_configuration
from .SpendCategories import register_new_spend_category, retrieve_all_spend_categories
from .SpendCategoryByExternalId import fetch_spend_category_by_external_id, modify_spend_category_by_external_id, remove_spend_category_by_external_id
from .SpendCategoryById import fetch_spend_category_by_internal_id, modify_spend_category_by_internal_id, remove_spend_category_by_internal_id
from .SupplierCompanies import get_all_supplier_companies, register_new_supplier_company
from .SupplierCompaniesDescribe import list_supplier_company_field_names
from .SupplierCompanyByExternalId import fetch_supplier_company_by_external_ref, modify_supplier_company_by_external_ref, remove_supplier_company_by_external_ref
from .SupplierCompanyById import fetch_supplier_company_by_id, modify_supplier_company_by_id, remove_supplier_company_by_id
from .SupplierCompanyContactById import fetch_company_contact_by_ids, modify_company_contact_by_ids, remove_company_contact_by_ids
from .SupplierCompanyContacts import get_contacts_for_company_by_external_id
from .SupplierCompanyContactsByExternalId import find_company_contacts_by_external_id
from .SupplierCompanySegmentations import establish_supplier_segmentation, retrieve_supplier_segmentation_list
from .SupplierContactByExternalId import fetch_supplier_contact_by_external_ref, modify_supplier_contact_by_external_ref, remove_supplier_contact_by_external_ref
from .SupplierContactById import fetch_supplier_contact_by_internal_id, modify_supplier_contact_details, remove_supplier_contact_by_id
from .SupplierContacts import register_new_supplier_contact
from .SupplierReports import fetch_supplier_report_schema, get_all_supplier_report_entries
from .SupplierReviewReports import fetch_supplier_review_schema, get_all_supplier_review_entries
from .Suppliers import fetch_supplier_details_by_id, retrieve_all_suppliers_from_db
from .UserById import disable_scim_user_account, fetch_scim_user_details, overwrite_scim_user_details, patch_scim_user_attributes
from .Users import find_scim_users, provision_new_scim_user

_function_map = {
    'add_line_item_to_event_worksheet': 'workday.mutations.m01.EventWorksheetLineItems.add_line_item_to_event_worksheet',
    'add_multiple_line_items_to_worksheet': 'workday.mutations.m01.EventWorksheetLineItems.add_multiple_line_items_to_worksheet',
    'add_options_to_field': 'workday.mutations.m01.FieldOptions.add_options_to_field',
    'assign_companies_to_project': 'workday.mutations.m01.ProjectRelationshipsSupplierCompanies.assign_companies_to_project',
    'assign_contacts_to_event_by_external_ids': 'workday.mutations.m01.EventSupplierContactsExternalId.assign_contacts_to_event_by_external_ids',
    'assign_contacts_to_event_by_id': 'workday.mutations.m01.EventSupplierContacts.assign_contacts_to_event_by_id',
    'assign_contacts_to_project_by_external_refs': 'workday.mutations.m01.ProjectRelationshipsSupplierContactsExternalId.assign_contacts_to_project_by_external_refs',
    'assign_contacts_to_project_by_internal_id': 'workday.mutations.m01.ProjectRelationshipsSupplierContacts.assign_contacts_to_project_by_internal_id',
    'assign_suppliers_to_event_by_external_id': 'workday.mutations.m01.EventSupplierCompaniesExternalId.assign_suppliers_to_event_by_external_id',
    'assign_suppliers_to_event_by_id': 'workday.mutations.m01.EventSupplierCompanies.assign_suppliers_to_event_by_id',
    'define_new_custom_field': 'workday.mutations.m01.Fields.define_new_custom_field',
    'delete_contact_category_by_id': 'workday.mutations.m01.ContactTypeById.delete_contact_category_by_id',
    'describe_contract_object_fields': 'workday.mutations.m01.Contracts.describe_contract_object_fields',
    'describe_project_object_fields': 'workday.mutations.m01.ProjectsDescribe.describe_project_object_fields',
    'disable_scim_user_account': 'workday.mutations.m01.UserById.disable_scim_user_account',
    'establish_supplier_segmentation': 'workday.mutations.m01.SupplierCompanySegmentations.establish_supplier_segmentation',
    'fetch_attachment_by_external_id': 'workday.mutations.m01.Attachments.fetch_attachment_by_external_id',
    'fetch_attachment_by_internal_id': 'workday.mutations.m01.Attachments.fetch_attachment_by_internal_id',
    'fetch_award_line_item_by_id': 'workday.mutations.m01.Awards.fetch_award_line_item_by_id',
    'fetch_bid_details_by_id': 'workday.mutations.m01.BidsById.fetch_bid_details_by_id',
    'fetch_bid_line_item_details': 'workday.mutations.m01.BidLineItemById.fetch_bid_line_item_details',
    'fetch_company_contact_by_ids': 'workday.mutations.m01.SupplierCompanyContactById.fetch_company_contact_by_ids',
    'fetch_contract_award_details': 'workday.mutations.m01.ContractAward.fetch_contract_award_details',
    'fetch_contract_award_line_item_details': 'workday.mutations.m01.ContractAward.fetch_contract_award_line_item_details',
    'fetch_contract_by_external_id': 'workday.mutations.m01.Contracts.fetch_contract_by_external_id',
    'fetch_contract_by_internal_id': 'workday.mutations.m01.Contracts.fetch_contract_by_internal_id',
    'fetch_contract_milestone_schema': 'workday.mutations.m01.ContractMilestoneReports.fetch_contract_milestone_schema',
    'fetch_contract_report_schema': 'workday.mutations.m01.ContractReports.fetch_contract_report_schema',
    'fetch_contract_type_by_external_id': 'workday.mutations.m01.Contracts.fetch_contract_type_by_external_id',
    'fetch_contract_type_by_internal_id': 'workday.mutations.m01.Contracts.fetch_contract_type_by_internal_id',
    'fetch_event_details_by_id': 'workday.mutations.m01.Events.fetch_event_details_by_id',
    'fetch_event_report_schema': 'workday.mutations.m01.EventReports.fetch_event_report_schema',
    'fetch_event_template_details': 'workday.mutations.m01.EventTemplates.fetch_event_template_details',
    'fetch_event_worksheet_details': 'workday.mutations.m01.EventWorksheetById.fetch_event_worksheet_details',
    'fetch_field_by_external_id': 'workday.mutations.m01.FieldByExternalId.fetch_field_by_external_id',
    'fetch_field_group_details': 'workday.mutations.m01.FieldGroupById.fetch_field_group_details',
    'fetch_performance_review_answer_schema': 'workday.mutations.m01.PerformanceReviewAnswerReports.fetch_performance_review_answer_schema',
    'fetch_performance_review_schema': 'workday.mutations.m01.PerformanceReviewReports.fetch_performance_review_schema',
    'fetch_project_by_external_id': 'workday.mutations.m01.ProjectByExternalId.fetch_project_by_external_id',
    'fetch_project_by_internal_id': 'workday.mutations.m01.ProjectById.fetch_project_by_internal_id',
    'fetch_project_category_by_id': 'workday.mutations.m01.ProjectTypeById.fetch_project_category_by_id',
    'fetch_project_milestone_schema': 'workday.mutations.m01.ProjectMilestoneReports.fetch_project_milestone_schema',
    'fetch_project_report_schema': 'workday.mutations.m01.ProjectReports.fetch_project_report_schema',
    'fetch_savings_report_schema': 'workday.mutations.m01.SavingsReports.fetch_savings_report_schema',
    'fetch_scim_provider_configuration': 'workday.mutations.m01.ServiceProviderConfig.fetch_scim_provider_configuration',
    'fetch_scim_resource_metadata': 'workday.mutations.m01.ResourceTypeById.fetch_scim_resource_metadata',
    'fetch_scim_resource_type_by_name': 'workday.mutations.m01.ResourceTypes.fetch_scim_resource_type_by_name',
    'fetch_scim_schema_by_uri': 'workday.mutations.m01.SchemaById.fetch_scim_schema_by_uri',
    'fetch_scim_user_details': 'workday.mutations.m01.UserById.fetch_scim_user_details',
    'fetch_spend_category_by_external_id': 'workday.mutations.m01.SpendCategoryByExternalId.fetch_spend_category_by_external_id',
    'fetch_spend_category_by_internal_id': 'workday.mutations.m01.SpendCategoryById.fetch_spend_category_by_internal_id',
    'fetch_supplier_company_by_external_ref': 'workday.mutations.m01.SupplierCompanyByExternalId.fetch_supplier_company_by_external_ref',
    'fetch_supplier_company_by_id': 'workday.mutations.m01.SupplierCompanyById.fetch_supplier_company_by_id',
    'fetch_supplier_contact_by_external_ref': 'workday.mutations.m01.SupplierContactByExternalId.fetch_supplier_contact_by_external_ref',
    'fetch_supplier_contact_by_internal_id': 'workday.mutations.m01.SupplierContactById.fetch_supplier_contact_by_internal_id',
    'fetch_supplier_details_by_id': 'workday.mutations.m01.Suppliers.fetch_supplier_details_by_id',
    'fetch_supplier_report_schema': 'workday.mutations.m01.SupplierReports.fetch_supplier_report_schema',
    'fetch_supplier_review_schema': 'workday.mutations.m01.SupplierReviewReports.fetch_supplier_review_schema',
    'fetch_worksheet_line_item_details': 'workday.mutations.m01.EventWorksheetLineItemById.fetch_worksheet_line_item_details',
    'find_all_attachments_by_id_filter': 'workday.mutations.m01.Attachments.find_all_attachments_by_id_filter',
    'find_awards_by_criteria': 'workday.mutations.m01.Awards.find_awards_by_criteria',
    'find_company_contacts_by_external_id': 'workday.mutations.m01.SupplierCompanyContactsByExternalId.find_company_contacts_by_external_id',
    'find_contracts_with_filters': 'workday.mutations.m01.Contracts.find_contracts_with_filters',
    'find_events_by_criteria': 'workday.mutations.m01.Events.find_events_by_criteria',
    'find_projects_with_filters': 'workday.mutations.m01.Projects.find_projects_with_filters',
    'find_scim_users': 'workday.mutations.m01.Users.find_scim_users',
    'get_all_contract_milestone_entries': 'workday.mutations.m01.ContractMilestoneReports.get_all_contract_milestone_entries',
    'get_all_event_report_entries': 'workday.mutations.m01.EventReports.get_all_event_report_entries',
    'get_all_event_templates': 'workday.mutations.m01.EventTemplates.get_all_event_templates',
    'get_all_payment_currencies': 'workday.mutations.m01.PaymentCurrencies.get_all_payment_currencies',
    'get_all_payment_terms': 'workday.mutations.m01.PaymentTerms.get_all_payment_terms',
    'get_all_payment_types': 'workday.mutations.m01.PaymentTypes.get_all_payment_types',
    'get_all_performance_review_answer_entries': 'workday.mutations.m01.PerformanceReviewAnswerReports.get_all_performance_review_answer_entries',
    'get_all_performance_review_entries': 'workday.mutations.m01.PerformanceReviewReports.get_all_performance_review_entries',
    'get_all_project_milestone_entries': 'workday.mutations.m01.ProjectMilestoneReports.get_all_project_milestone_entries',
    'get_all_project_types': 'workday.mutations.m01.ProjectTypes.get_all_project_types',
    'get_all_savings_report_entries': 'workday.mutations.m01.SavingsReports.get_all_savings_report_entries',
    'get_all_scim_resource_types': 'workday.mutations.m01.ResourceTypes.get_all_scim_resource_types',
    'get_all_supplier_companies': 'workday.mutations.m01.SupplierCompanies.get_all_supplier_companies',
    'get_all_supplier_report_entries': 'workday.mutations.m01.SupplierReports.get_all_supplier_report_entries',
    'get_all_supplier_review_entries': 'workday.mutations.m01.SupplierReviewReports.get_all_supplier_review_entries',
    'get_attachments_by_id_list': 'workday.mutations.m01.Attachments.get_attachments_by_id_list',
    'get_bid_line_item_schema_fields': 'workday.mutations.m01.BidLineItemsDescribe.get_bid_line_item_schema_fields',
    'get_bid_schema_fields': 'workday.mutations.m01.BidsDescribe.get_bid_schema_fields',
    'get_contacts_for_company_by_external_id': 'workday.mutations.m01.SupplierCompanyContacts.get_contacts_for_company_by_external_id',
    'get_custom_fields_with_filter': 'workday.mutations.m01.Fields.get_custom_fields_with_filter',
    'get_entries_for_event_report': 'workday.mutations.m01.EventReports.get_entries_for_event_report',
    'get_entries_for_project_report': 'workday.mutations.m01.ProjectReports.get_entries_for_project_report',
    'get_line_items_for_award': 'workday.mutations.m01.Awards.get_line_items_for_award',
    'get_line_items_for_contract_award': 'workday.mutations.m01.ContractAward.get_line_items_for_contract_award',
    'get_line_items_for_event_worksheet': 'workday.mutations.m01.EventWorksheetLineItems.get_line_items_for_event_worksheet',
    'get_my_event_report_entries': 'workday.mutations.m01.EventReports.get_my_event_report_entries',
    'get_my_project_report_entries': 'workday.mutations.m01.ProjectReports.get_my_project_report_entries',
    'link_suppliers_to_project_by_external_ref': 'workday.mutations.m01.ProjectRelationshipsSupplierCompaniesExternalId.link_suppliers_to_project_by_external_ref',
    'list_supplier_company_field_names': 'workday.mutations.m01.SupplierCompaniesDescribe.list_supplier_company_field_names',
    'modify_attachment_by_external_id': 'workday.mutations.m01.Attachments.modify_attachment_by_external_id',
    'modify_attachment_by_internal_id': 'workday.mutations.m01.Attachments.modify_attachment_by_internal_id',
    'modify_company_contact_by_ids': 'workday.mutations.m01.SupplierCompanyContactById.modify_company_contact_by_ids',
    'modify_contact_category_by_external_id': 'workday.mutations.m01.ContactTypeByExternalId.modify_contact_category_by_external_id',
    'modify_contract_by_external_id': 'workday.mutations.m01.Contracts.modify_contract_by_external_id',
    'modify_contract_by_internal_id': 'workday.mutations.m01.Contracts.modify_contract_by_internal_id',
    'modify_contract_type_by_external_id': 'workday.mutations.m01.Contracts.modify_contract_type_by_external_id',
    'modify_contract_type_by_internal_id': 'workday.mutations.m01.Contracts.modify_contract_type_by_internal_id',
    'modify_currency_by_external_ref': 'workday.mutations.m01.PaymentCurrenciesExternalId.modify_currency_by_external_ref',
    'modify_currency_by_internal_id': 'workday.mutations.m01.PaymentCurrenciesId.modify_currency_by_internal_id',
    'modify_event_details_by_id': 'workday.mutations.m01.Events.modify_event_details_by_id',
    'modify_field_by_external_id': 'workday.mutations.m01.FieldByExternalId.modify_field_by_external_id',
    'modify_field_group_by_identifier': 'workday.mutations.m01.FieldGroupById.modify_field_group_by_identifier',
    'modify_field_options_by_id': 'workday.mutations.m01.FieldOptionById.modify_field_options_by_id',
    'modify_field_properties_by_id': 'workday.mutations.m01.FieldById.modify_field_properties_by_id',
    'modify_payment_method_by_external_ref': 'workday.mutations.m01.PaymentTypesExternalId.modify_payment_method_by_external_ref',
    'modify_payment_term_by_external_ref': 'workday.mutations.m01.PaymentTermsExternalId.modify_payment_term_by_external_ref',
    'modify_payment_term_by_id': 'workday.mutations.m01.PaymentTermsId.modify_payment_term_by_id',
    'modify_payment_type_by_id': 'workday.mutations.m01.PaymentTypesId.modify_payment_type_by_id',
    'modify_project_by_external_id': 'workday.mutations.m01.ProjectByExternalId.modify_project_by_external_id',
    'modify_project_by_internal_id': 'workday.mutations.m01.ProjectById.modify_project_by_internal_id',
    'modify_spend_category_by_external_id': 'workday.mutations.m01.SpendCategoryByExternalId.modify_spend_category_by_external_id',
    'modify_spend_category_by_internal_id': 'workday.mutations.m01.SpendCategoryById.modify_spend_category_by_internal_id',
    'modify_supplier_company_by_external_ref': 'workday.mutations.m01.SupplierCompanyByExternalId.modify_supplier_company_by_external_ref',
    'modify_supplier_company_by_id': 'workday.mutations.m01.SupplierCompanyById.modify_supplier_company_by_id',
    'modify_supplier_contact_by_external_ref': 'workday.mutations.m01.SupplierContactByExternalId.modify_supplier_contact_by_external_ref',
    'modify_supplier_contact_details': 'workday.mutations.m01.SupplierContactById.modify_supplier_contact_details',
    'modify_worksheet_line_item_details': 'workday.mutations.m01.EventWorksheetLineItemById.modify_worksheet_line_item_details',
    'overwrite_scim_user_details': 'workday.mutations.m01.UserById.overwrite_scim_user_details',
    'patch_scim_user_attributes': 'workday.mutations.m01.UserById.patch_scim_user_attributes',
    'provision_new_scim_user': 'workday.mutations.m01.Users.provision_new_scim_user',
    'register_new_contact_type': 'workday.mutations.m01.ContactTypes.register_new_contact_type',
    'register_new_contract': 'workday.mutations.m01.Contracts.register_new_contract',
    'register_new_contract_type': 'workday.mutations.m01.Contracts.register_new_contract_type',
    'register_new_event': 'workday.mutations.m01.Events.register_new_event',
    'register_new_field_group': 'workday.mutations.m01.FieldGroups.register_new_field_group',
    'register_new_payment_currency': 'workday.mutations.m01.PaymentCurrencies.register_new_payment_currency',
    'register_new_payment_term': 'workday.mutations.m01.PaymentTerms.register_new_payment_term',
    'register_new_payment_type': 'workday.mutations.m01.PaymentTypes.register_new_payment_type',
    'register_new_project': 'workday.mutations.m01.Projects.register_new_project',
    'register_new_spend_category': 'workday.mutations.m01.SpendCategories.register_new_spend_category',
    'register_new_supplier_company': 'workday.mutations.m01.SupplierCompanies.register_new_supplier_company',
    'register_new_supplier_contact': 'workday.mutations.m01.SupplierContacts.register_new_supplier_contact',
    'remove_attachment_by_external_id': 'workday.mutations.m01.Attachments.remove_attachment_by_external_id',
    'remove_attachment_by_internal_id': 'workday.mutations.m01.Attachments.remove_attachment_by_internal_id',
    'remove_company_contact_by_ids': 'workday.mutations.m01.SupplierCompanyContactById.remove_company_contact_by_ids',
    'remove_contact_category_by_external_id': 'workday.mutations.m01.ContactTypeByExternalId.remove_contact_category_by_external_id',
    'remove_contract_by_external_id': 'workday.mutations.m01.Contracts.remove_contract_by_external_id',
    'remove_contract_by_internal_id': 'workday.mutations.m01.Contracts.remove_contract_by_internal_id',
    'remove_contract_type_by_external_id': 'workday.mutations.m01.Contracts.remove_contract_type_by_external_id',
    'remove_contract_type_by_internal_id': 'workday.mutations.m01.Contracts.remove_contract_type_by_internal_id',
    'remove_currency_by_external_ref': 'workday.mutations.m01.PaymentCurrenciesExternalId.remove_currency_by_external_ref',
    'remove_currency_by_internal_id': 'workday.mutations.m01.PaymentCurrenciesId.remove_currency_by_internal_id',
    'remove_event_by_id': 'workday.mutations.m01.Events.remove_event_by_id',
    'remove_field_by_external_id': 'workday.mutations.m01.FieldByExternalId.remove_field_by_external_id',
    'remove_field_by_internal_id': 'workday.mutations.m01.FieldById.remove_field_by_internal_id',
    'remove_field_group_from_system': 'workday.mutations.m01.FieldGroupById.remove_field_group_from_system',
    'remove_field_options_by_id': 'workday.mutations.m01.FieldOptionById.remove_field_options_by_id',
    'remove_payment_method_by_external_ref': 'workday.mutations.m01.PaymentTypesExternalId.remove_payment_method_by_external_ref',
    'remove_payment_term_by_external_ref': 'workday.mutations.m01.PaymentTermsExternalId.remove_payment_term_by_external_ref',
    'remove_payment_term_by_id': 'workday.mutations.m01.PaymentTermsId.remove_payment_term_by_id',
    'remove_payment_type_by_id': 'workday.mutations.m01.PaymentTypesId.remove_payment_type_by_id',
    'remove_project_by_external_id': 'workday.mutations.m01.ProjectByExternalId.remove_project_by_external_id',
    'remove_project_by_internal_id': 'workday.mutations.m01.ProjectById.remove_project_by_internal_id',
    'remove_spend_category_by_external_id': 'workday.mutations.m01.SpendCategoryByExternalId.remove_spend_category_by_external_id',
    'remove_spend_category_by_internal_id': 'workday.mutations.m01.SpendCategoryById.remove_spend_category_by_internal_id',
    'remove_supplier_company_by_external_ref': 'workday.mutations.m01.SupplierCompanyByExternalId.remove_supplier_company_by_external_ref',
    'remove_supplier_company_by_id': 'workday.mutations.m01.SupplierCompanyById.remove_supplier_company_by_id',
    'remove_supplier_contact_by_external_ref': 'workday.mutations.m01.SupplierContactByExternalId.remove_supplier_contact_by_external_ref',
    'remove_supplier_contact_by_id': 'workday.mutations.m01.SupplierContactById.remove_supplier_contact_by_id',
    'remove_worksheet_line_item': 'workday.mutations.m01.EventWorksheetLineItemById.remove_worksheet_line_item',
    'retrieve_all_bid_line_items_with_filter': 'workday.mutations.m01.BidLineItemsList.retrieve_all_bid_line_items_with_filter',
    'retrieve_all_contact_types': 'workday.mutations.m01.ContactTypes.retrieve_all_contact_types',
    'retrieve_all_contract_awards': 'workday.mutations.m01.ContractAward.retrieve_all_contract_awards',
    'retrieve_all_contract_types': 'workday.mutations.m01.Contracts.retrieve_all_contract_types',
    'retrieve_all_field_groups': 'workday.mutations.m01.FieldGroups.retrieve_all_field_groups',
    'retrieve_all_scim_schemas': 'workday.mutations.m01.Schemas.retrieve_all_scim_schemas',
    'retrieve_all_spend_categories': 'workday.mutations.m01.SpendCategories.retrieve_all_spend_categories',
    'retrieve_all_suppliers_from_db': 'workday.mutations.m01.Suppliers.retrieve_all_suppliers_from_db',
    'retrieve_bids_for_event': 'workday.mutations.m01.EventBids.retrieve_bids_for_event',
    'retrieve_contract_report_data': 'workday.mutations.m01.ContractReports.retrieve_contract_report_data',
    'retrieve_field_properties_by_id': 'workday.mutations.m01.FieldById.retrieve_field_properties_by_id',
    'retrieve_line_items_for_bid': 'workday.mutations.m01.BidLineItems.retrieve_line_items_for_bid',
    'retrieve_options_for_field': 'workday.mutations.m01.FieldOptionsByFieldId.retrieve_options_for_field',
    'retrieve_supplier_segmentation_list': 'workday.mutations.m01.SupplierCompanySegmentations.retrieve_supplier_segmentation_list',
    'retrieve_worksheets_for_event': 'workday.mutations.m01.EventWorksheets.retrieve_worksheets_for_event',
    'unassign_companies_from_project': 'workday.mutations.m01.ProjectRelationshipsSupplierCompanies.unassign_companies_from_project',
    'unassign_contacts_from_event_by_external_ids': 'workday.mutations.m01.EventSupplierContactsExternalId.unassign_contacts_from_event_by_external_ids',
    'unassign_contacts_from_event_by_id': 'workday.mutations.m01.EventSupplierContacts.unassign_contacts_from_event_by_id',
    'unassign_contacts_from_project_by_external_refs': 'workday.mutations.m01.ProjectRelationshipsSupplierContactsExternalId.unassign_contacts_from_project_by_external_refs',
    'unassign_contacts_from_project_by_internal_id': 'workday.mutations.m01.ProjectRelationshipsSupplierContacts.unassign_contacts_from_project_by_internal_id',
    'unassign_suppliers_from_event_by_external_id': 'workday.mutations.m01.EventSupplierCompaniesExternalId.unassign_suppliers_from_event_by_external_id',
    'unassign_suppliers_from_event_by_id': 'workday.mutations.m01.EventSupplierCompanies.unassign_suppliers_from_event_by_id',
    'unlink_suppliers_from_project_by_external_ref': 'workday.mutations.m01.ProjectRelationshipsSupplierCompaniesExternalId.unlink_suppliers_from_project_by_external_ref',
    'update_contact_category_by_id': 'workday.mutations.m01.ContactTypeById.update_contact_category_by_id',
    'upload_new_attachment': 'workday.mutations.m01.Attachments.upload_new_attachment',
}
