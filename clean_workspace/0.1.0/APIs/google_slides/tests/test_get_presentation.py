import unittest
import copy
from datetime import datetime, timezone
import uuid # Keep for _validate_uuid if it's still used in other tests

from google_slides.SimulationEngine import utils 
from google_slides.SimulationEngine.db import DB
from google_slides.SimulationEngine import custom_errors # Import the module
from google_slides.presentations import get_presentation 
from common_utils.base_case import BaseTestCaseWithErrorHandler
from google_slides.SimulationEngine.models import PresentationModel
# Assuming models are not directly used in this test file, but were in setup for batch_update
# from google_slides.SimulationEngine import models 

class TestGetPresentation(BaseTestCaseWithErrorHandler):
    def setUp(self):
        self._original_DB_state = copy.deepcopy(DB)
        self.user_id = "me"
        utils._ensure_user(self.user_id) 
        DB.clear()

        DB.update({
              "users": {
                "me": {
                  "about": {
                    "kind": "drive#about",
                    "storageQuota": {
                      "limit": "0",
                      "usageInDrive": "0",
                      "usageInDriveTrash": "0",
                      "usage": "0"
                    },
                    "driveThemes": False,
                    "canCreateDrives": False,
                    "importFormats": {},
                    "exportFormats": {},
                    "appInstalled": False,
                    "user": {
                      "displayName": "",
                      "kind": "drive#user",
                      "me": True,
                      "permissionId": "",
                      "emailAddress": ""
                    },
                    "folderColorPalette": "",
                    "maxImportSizes": {},
                    "maxUploadSize": "0"
                  },
                  "files": {
                    "pres1": {
                      "id": "pres1",
                      "driveId": "",
                      "name": "Project Plan",
                      "mimeType": "application/vnd.google-apps.presentation",
                      "createdTime": "2025-03-01T10:00:00Z",
                      "modifiedTime": "2025-03-10T10:00:00Z",
                      "trashed": False,
                      "starred": False,
                      "parents": [
                        "drive-1"
                      ],
                      "owners": [
                        "john.doe@gmail.com"
                      ],
                      "size": "102400",
                      "permissions": [
                        {
                          "id": "permission-1",
                          "role": "owner",
                          "type": "user",
                          "emailAddress": "john.doe@gmail.com"
                        }
                      ],
                      "presentationId": "pres1",
                      "title": "Test Presentation 1",
                      "slides": [
                        {
                          "objectId": "slide1_page1",
                          "pageType": "SLIDE",
                          "pageProperties": {
                            "backgroundColor": {
                              "opaqueColor": {
                                "rgbColor": {
                                  "red": 1.0,
                                  "green": 0.0,
                                  "blue": 0.0
                                }
                              }
                            }
                          },
                          "slideProperties": {
                            "masterObjectId": "master1",
                            "layoutObjectId": "layout_for_slide1"
                          },
                          "pageElements": [
                            {
                              "objectId": "element1_slide1",
                              "size": {
                                "width": {
                                  "magnitude": 200,
                                  "unit": "PT"
                                },
                                "height": {
                                  "magnitude": 100,
                                  "unit": "PT"
                                }
                              },
                              "transform": {
                                "scaleX": 1.0,
                                "translateY": 50.0
                              },
                              "shape": {
                                "shapeType": "RECTANGLE",
                                "text": {}
                              }
                            },
                            {
                              "objectId": "element2_slide1_text",
                              "size": {
                                "width": {
                                  "magnitude": 300,
                                  "unit": "PT"
                                },
                                "height": {
                                  "magnitude": 150,
                                  "unit": "PT"
                                }
                              },
                              "transform": {
                                "scaleX": 1.0,
                                "translateY": 200.0
                              },
                              "shape": {
                                "shapeType": "TEXT_BOX",
                                "text": {
                                  "textElements": [
                                    {
                                      "textRun": {
                                        "content": "Hello ",
                                        "style": {
                                          "fontFamily": "Calibri",
                                          "fontSize": {
                                            "magnitude": 12,
                                            "unit": "PT"
                                          }
                                        }
                                      }
                                    },
                                    {
                                      "textRun": {
                                        "content": "World!",
                                        "style": {
                                          "fontFamily": "Times New Roman",
                                          "fontSize": {
                                            "magnitude": 14,
                                            "unit": "PT"
                                          }
                                        }
                                      }
                                    }
                                  ]
                                }
                              }
                            }
                          ],
                          "revisionId": "rev_slide1"
                        },
                        {
                          "objectId": "slide_minimal",
                          "pageType": "SLIDE",
                          "pageProperties": {
                            "backgroundColor": {
                              "opaqueColor": {
                                "rgbColor": {
                                  "red": 0.95,
                                  "green": 0.95,
                                  "blue": 0.95
                                }
                              }
                            }
                          },
                          "pageElements": [],
                          "revisionId": "rev_slide_minimal",
                          "slideProperties": {
                            "masterObjectId": "master1",
                            "layoutObjectId": "layout_for_slide1"
                          }
                        }
                      ],
                      "masters": [
                        {
                          "objectId": "master_new1",
                          "pageType": "MASTER",
                          "pageProperties": {
                            "backgroundColor": {
                              "opaqueColor": {
                                "rgbColor": {
                                  "red": 0.95,
                                  "green": 0.95,
                                  "blue": 0.95
                                }
                              }
                            }
                          },
                          "masterProperties": {
                            "displayName": "Master Title Placeholder"
                          },
                          "pageElements": [
                            {
                              "objectId": "master_textbox1",
                              "size": {
                                "width": {
                                  "magnitude": 400,
                                  "unit": "PT"
                                },
                                "height": {
                                  "magnitude": 100,
                                  "unit": "PT"
                                }
                              },
                              "transform": {
                                "scaleX": 1.0,
                                "scaleY": 1.0,
                                "translateX": 50.0,
                                "translateY": 50.0,
                                "unit": "PT"
                              },
                              "shape": {
                                "shapeType": "TEXT_BOX",
                                "text": {
                                  "textElements": [
                                    {
                                      "textRun": {
                                        "content": "Master Title Placeholder",
                                        "style": {
                                          "fontFamily": "Arial",
                                          "fontSize": {
                                            "magnitude": 24,
                                            "unit": "PT"
                                          },
                                          "bold": True
                                        }
                                      }
                                    }
                                  ]
                                }
                              }
                            }
                          ],
                          "revisionId": "rev_master_new1"
                        }
                      ],
                      "layouts": [
                        {
                          "objectId": "layout_basic_title_content",
                          "pageType": "LAYOUT",
                          "layoutProperties": {"displayName": "Basic Title and Content"},
                          "pageProperties": {
                            "backgroundColor": {
                              "opaqueColor": {
                                "rgbColor": {
                                  "red": 1.0,
                                  "green": 1.0,
                                  "blue": 1.0
                                }
                              }
                            }
                          },
                          "pageElements": [
                            {
                              "objectId": "title_placeholder_layout",
                              "size": {
                                "width": {
                                  "magnitude": 500,
                                  "unit": "PT"
                                },
                                "height": {
                                  "magnitude": 60,
                                  "unit": "PT"
                                }
                              },
                              "transform": {
                                "scaleX": 1.0,
                                "scaleY": 1.0,
                                "translateX": 40.0,
                                "translateY": 40.0,
                                "unit": "PT"
                              },
                              "shape": {
                                "shapeType": "TEXT_BOX"
                              },
                            },
                            {
                              "objectId": "body_placeholder_layout",
                              "size": {
                                "width": {
                                  "magnitude": 500,
                                  "unit": "PT"
                                },
                                "height": {
                                  "magnitude": 300,
                                  "unit": "PT"
                                }
                              },
                              "transform": {
                                "scaleX": 1.0,
                                "scaleY": 1.0,
                                "translateX": 40.0,
                                "translateY": 120.0,
                                "unit": "PT"
                              },
                              "shape": {
                                "shapeType": "TEXT_BOX"
                              },
                            }
                          ],
                          "revisionId": "rev_layout_basic"
                        }
                      ],
                      "pageSize": {
                        "width": {
                          "magnitude": 9144000,
                          "unit": "EMU"
                        },
                        "height": {
                          "magnitude": 5143500,
                          "unit": "EMU"
                        }
                      },
                      "locale": "",
                      "revisionId": "pres_rev_xyz123_uuid"
                    },
                    'file-1':
                            {
                                "id": "file-1",
                                "name": "Test File 1",
                                "mimeType": "application/pdf",
                                "createdTime": "2025-03-01T10:00:00Z",
                                "modifiedTime": "2025-03-10T10:00:00Z",
                                "trashed": False,
                                "starred": False,
                                "parents": [
                                    "drive-1"
                                ],
                                "owners": [
                                    "john.doe@gmail.com"
                                ],
                                "size": "102400",
                                "permissions": [
                                    {
                                        "id": "permission-1",
                                        "role": "owner",
                                        "type": "user",
                                        "emailAddress": "john.doe@gmail.com"
                                    }
                                ]
                            }
                    }
                },
                "drives": {},
                "comments": {},
                "replies": {},
                "labels": {},
                "accessproposals": {},
                "counters": {
                  "file": 0,
                  "drive": 0,
                  "comment": 0,
                  "reply": 0,
                  "label": 0,
                  "accessproposal": 0,
                  "revision": 0
                }
              }
            })

        # --- Define source data for primary test presentations ---
        self.full_presentation_id = "pres1" 
        self.full_presentation_data = {
            "presentationId": self.full_presentation_id, 
            "title": "Test Presentation 1",
            "slides": [
                    {
                        "objectId": "slide1_page1",
                        "pageType": "SLIDE",
                        "pageProperties": {
                        "backgroundColor": {
                            "opaqueColor": {
                            "rgbColor": {
                                "red": 1.0,
                                "green": 0.0,
                                "blue": 0.0
                            }
                            }
                        }
                        },
                        "slideProperties": {
                        "masterObjectId": "master1",
                        "layoutObjectId": "layout_for_slide1"
                        },
                        "pageElements": [
                        {
                            "objectId": "element1_slide1",
                            "size": {
                            "width": {
                                "magnitude": 200,
                                "unit": "PT"
                            },
                            "height": {
                                "magnitude": 100,
                                "unit": "PT"
                            }
                            },
                            "transform": {
                            "scaleX": 1.0,
                            "translateY": 50.0
                            },
                            "shape": {
                            "shapeType": "RECTANGLE",
                            "text": {}
                            }
                        },
                        {
                            "objectId": "element2_slide1_text",
                            "size": {
                            "width": {
                                "magnitude": 300,
                                "unit": "PT"
                            },
                            "height": {
                                "magnitude": 150,
                                "unit": "PT"
                            }
                            },
                            "transform": {
                            "scaleX": 1.0,
                            "translateY": 200.0
                            },
                            "shape": {
                            "shapeType": "TEXT_BOX",
                            "text": {
                                "textElements": [
                                {
                                    "textRun": {
                                    "content": "Hello ",
                                    "style": {
                                        "fontFamily": "Calibri",
                                        "fontSize": {
                                        "magnitude": 12,
                                        "unit": "PT"
                                        }
                                    }
                                    }
                                },
                                {
                                    "textRun": {
                                    "content": "World!",
                                    "style": {
                                        "fontFamily": "Times New Roman",
                                        "fontSize": {
                                        "magnitude": 14,
                                        "unit": "PT"
                                        }
                                    }
                                    }
                                }
                                ]
                            }
                            }
                        }
                        ],
                        "revisionId": "rev_slide1"
                    },
                    {
                        "objectId": "slide_minimal",
                        "pageType": "SLIDE",
                        "pageProperties": {
                        "backgroundColor": {
                            "opaqueColor": {
                            "rgbColor": {
                                "red": 0.95,
                                "green": 0.95,
                                "blue": 0.95
                            }
                            }
                        }
                        },
                        "pageElements": [],
                        "revisionId": "rev_slide_minimal",
                        "slideProperties": {
                        "masterObjectId": "master1",
                        "layoutObjectId": "layout_for_slide1"
                        }
                    }
                    ],
                    "masters": [
                    {
                        "objectId": "master_new1",
                        "pageType": "MASTER",
                        "pageProperties": {
                        "backgroundColor": {
                            "opaqueColor": {
                            "rgbColor": {
                                "red": 0.95,
                                "green": 0.95,
                                "blue": 0.95
                            }
                            }
                        }
                        },
                        "masterProperties": {
                        "displayName": "Master Title Placeholder"
                        },
                        "pageElements": [
                        {
                            "objectId": "master_textbox1",
                            "size": {
                            "width": {
                                "magnitude": 400,
                                "unit": "PT"
                            },
                            "height": {
                                "magnitude": 100,
                                "unit": "PT"
                            }
                            },
                            "transform": {
                            "scaleX": 1.0,
                            "scaleY": 1.0,
                            "translateX": 50.0,
                            "translateY": 50.0,
                            "unit": "PT"
                            },
                            "shape": {
                            "shapeType": "TEXT_BOX",
                            "text": {
                                "textElements": [
                                {
                                    "textRun": {
                                    "content": "Master Title Placeholder",
                                    "style": {
                                        "fontFamily": "Arial",
                                        "fontSize": {
                                        "magnitude": 24,
                                        "unit": "PT"
                                        },
                                        "bold": True
                                    }
                                    }
                                }
                                ]
                            }
                            }
                        }
                        ],
                        "revisionId": "rev_master_new1"
                    }
                    ],
                    "layouts": [
                    {
                        "objectId": "layout_basic_title_content",
                        "pageType": "LAYOUT",
                        "layoutProperties": {"displayName": "Basic Title and Content"},
                        "pageProperties": {
                        "backgroundColor": {
                            "opaqueColor": {
                            "rgbColor": {
                                "red": 1.0,
                                "green": 1.0,
                                "blue": 1.0
                            }
                            }
                        }
                        },
                        "pageElements": [
                        {
                            "objectId": "title_placeholder_layout",
                            "size": {
                            "width": {
                                "magnitude": 500,
                                "unit": "PT"
                            },
                            "height": {
                                "magnitude": 60,
                                "unit": "PT"
                            }
                            },
                            "transform": {
                            "scaleX": 1.0,
                            "scaleY": 1.0,
                            "translateX": 40.0,
                            "translateY": 40.0,
                            "unit": "PT"
                            },
                            "shape": {
                            "shapeType": "TEXT_BOX"
                            },
                        },
                        {
                            "objectId": "body_placeholder_layout",
                            "size": {
                            "width": {
                                "magnitude": 500,
                                "unit": "PT"
                            },
                            "height": {
                                "magnitude": 300,
                                "unit": "PT"
                            }
                            },
                            "transform": {
                            "scaleX": 1.0,
                            "scaleY": 1.0,
                            "translateX": 40.0,
                            "translateY": 120.0,
                            "unit": "PT"
                            },
                            "shape": {
                            "shapeType": "TEXT_BOX"
                            },
                        }
                        ],
                        "revisionId": "rev_layout_basic"
                    }
                    ],
                    "pageSize": {
                    "width": {
                        "magnitude": 9144000,
                        "unit": "EMU"
                    },
                    "height": {
                        "magnitude": 5143500,
                        "unit": "EMU"
                    }
                    },
                    "locale": "",
                    "revisionId": "pres_rev_xyz123_uuid"
                    }
        self.full_presentation_slides_data = PresentationModel.model_validate(self.full_presentation_data).model_dump()

    def test_get_full_presentation_no_fields(self):
        presentation = get_presentation(presentationId=self.full_presentation_id)
        self.assertEqual(presentation, self.full_presentation_slides_data)

    def test_get_full_presentation_fields_none(self):
        presentation = get_presentation(presentationId=self.full_presentation_id, fields=None)
        self.assertEqual(presentation, self.full_presentation_slides_data)

    def test_get_full_presentation_fields_empty_string(self):
        presentation = get_presentation(presentationId=self.full_presentation_id, fields="")
        self.assertEqual(presentation, self.full_presentation_slides_data)

    # def test_get_minimal_presentation_no_fields(self):
    #     presentation = get_presentation(presentationId=self.min_presentation_id)
    #     self.assertEqual(presentation, self.expected_minimal_presentation_no_fields)

    def test_get_presentation_field_title_only(self):
        expected = {
            "presentationId": self.full_presentation_id,
            "title": "Test Presentation 1"
        }
        presentation = get_presentation(presentationId=self.full_presentation_id, fields="title")
        self.assertEqual(presentation, expected)

    def test_get_presentation_field_revision_id_only(self):
        expected = {
            "presentationId": self.full_presentation_id,
            "revisionId": "pres_rev_xyz123_uuid"
        }
        presentation = get_presentation(presentationId=self.full_presentation_id, fields="revisionId")
        self.assertEqual(presentation, expected)

    def test_get_presentation_fields_multiple_toplevel(self):
        expected = {
            "presentationId": self.full_presentation_id,
            "title": "Test Presentation 1",
            "revisionId": "pres_rev_xyz123_uuid"
        }
        presentation = get_presentation(presentationId=self.full_presentation_id, fields="title,revisionId")
        self.assertEqual(presentation, expected)
        
    def test_get_presentation_fields_multiple_toplevel_with_spaces(self):
        expected = {
            "presentationId": self.full_presentation_id,
            "title": "Test Presentation 1",
            "revisionId": "pres_rev_xyz123_uuid"
        }
        presentation = get_presentation(presentationId=self.full_presentation_id, fields="title, revisionId")
        self.assertEqual(presentation, expected)

    def test_get_presentation_field_pagesize_full(self):
        expected = {
            "presentationId": self.full_presentation_id,
            "pageSize": self.full_presentation_slides_data["pageSize"]
        }
        presentation = get_presentation(presentationId=self.full_presentation_id, fields="pageSize")
        self.assertEqual(presentation, expected)

    def test_get_presentation_field_slides_full_structure(self):
        expected = {
            "presentationId": self.full_presentation_id,
            "slides": self.full_presentation_slides_data["slides"]
        }
        presentation = get_presentation(presentationId=self.full_presentation_id, fields="slides")
        self.assertEqual(presentation, expected)

    def test_get_presentation_field_masters_full_structure(self):
        expected = {
            "presentationId": self.full_presentation_id,
            "masters": self.full_presentation_slides_data["masters"]
        }
        presentation = get_presentation(presentationId=self.full_presentation_id, fields="masters")
        self.assertEqual(presentation, expected)

    def test_get_presentation_field_masters_displayname_and_layouts_objectid(self):
        # This test implies fields="masters.displayName,layouts.objectId"
        # which the current get_presentation handles as InvalidInputError due to nested paths.
        # To test multiple top-level fields:
        response_masters_layouts = get_presentation(presentationId=self.full_presentation_id, fields="masters,layouts")
        expected_masters_layouts = {
            "presentationId": self.full_presentation_id,
            "masters": self.full_presentation_slides_data["masters"],
            "layouts": self.full_presentation_slides_data["layouts"]
        }
        self.assertEqual(response_masters_layouts, expected_masters_layouts)


    def test_get_presentation_all_fields_explicitly(self):
        fields_str = "title,pageSize,slides,masters,layouts,notesMaster,locale,revisionId" # presentationId is always included
        presentation = get_presentation(presentationId=self.full_presentation_id, fields=fields_str)
        self.assertEqual(presentation, self.full_presentation_slides_data)

    # --- Error Cases ---

    def test_get_presentation_not_found(self):
        self.assert_error_behavior(
            get_presentation,
            expected_exception_type=custom_errors.NotFoundError,
            expected_message="Presentation with ID 'nonExistentPresId' not found or is not a presentation file.",
            presentationId="nonExistentPresId"
        )

    def test_get_presentation_invalid_id_type_none(self):
        self.assert_error_behavior(
            get_presentation,
            expected_exception_type=custom_errors.InvalidInputError, 
            expected_message="presentationId must be a string.", # Corrected expected message
            presentationId=None 
        )

    def test_get_presentation_invalid_id_type_int(self):
        self.assert_error_behavior(
            get_presentation,
            expected_exception_type=custom_errors.InvalidInputError, # Corrected
            expected_message="presentationId must be a string.",
            presentationId=123 
        )
    
    def test_get_presentation_empty_id_string(self):
        self.assert_error_behavior(
            get_presentation,
            expected_exception_type=custom_errors.InvalidInputError, # Corrected from NotFoundError
            expected_message="presentationId must be a non-empty string.",
            presentationId=""
        )

    def test_get_presentation_invalid_fields_type_int(self):
        self.assert_error_behavior(
            get_presentation,
            expected_exception_type=custom_errors.InvalidInputError, # Corrected
            expected_message="fields must be a string if provided.",
            presentationId=self.full_presentation_id,
            fields=123 
        )

    def test_get_presentation_invalid_fields_type_list(self): # Added this test
        self.assert_error_behavior(
            get_presentation,
            expected_exception_type=custom_errors.InvalidInputError, # Corrected
            expected_message="fields must be a string if provided.",
            presentationId=self.full_presentation_id,
            fields=["title", "slides"] 
        )

    # Tests for invalid field strings - these should expect InvalidInputError
    def test_get_presentation_invalid_fields_unknown_toplevel_field(self):
        self.assert_error_behavior(
            get_presentation,
            expected_exception_type=custom_errors.InvalidInputError,
            expected_message="The 'fields' parameter is malformed or specifies an invalid field path.",
            presentationId=self.full_presentation_id,
            fields="nonExistentField"
        )

    def test_get_presentation_invalid_fields_unknown_toplevel_field_in_list(self):
        self.assert_error_behavior(
            get_presentation,
            expected_exception_type=custom_errors.InvalidInputError,
            expected_message="The 'fields' parameter is malformed or specifies an invalid field path.",
            presentationId=self.full_presentation_id,
            fields="title,nonExistentField,slides"
        )
    
    # Tests for nested fields (currently expected to fail with InvalidInputError due to simple field parsing)
    def test_get_presentation_field_pagesize_width_only(self):
        self.assert_error_behavior(
            get_presentation,
            expected_exception_type=custom_errors.InvalidInputError,
            expected_message="The 'fields' parameter is malformed or specifies an invalid field path.",
            presentationId=self.full_presentation_id,
            fields="pageSize.width" 
        )

    def test_get_presentation_field_pagesize_height_magnitude_only(self):
        self.assert_error_behavior(
            get_presentation,
            expected_exception_type=custom_errors.InvalidInputError,
            expected_message="The 'fields' parameter is malformed or specifies an invalid field path.",
            presentationId=self.full_presentation_id,
            fields="pageSize.height.magnitude"
        )
        
    def test_get_presentation_field_slides_objectid_only(self):
        self.assert_error_behavior(
            get_presentation,
            expected_exception_type=custom_errors.InvalidInputError,
            expected_message="The 'fields' parameter is malformed or specifies an invalid field path.",
            presentationId=self.full_presentation_id, 
            fields="slides.objectId"
        )

    def test_get_presentation_field_slides_objectid_and_pagetype(self):
        self.assert_error_behavior(
            get_presentation,
            expected_exception_type=custom_errors.InvalidInputError,
            expected_message="The 'fields' parameter is malformed or specifies an invalid field path.",
            presentationId=self.full_presentation_id, 
            fields="slides.objectId,slides.pageType"
        )

    def test_get_presentation_field_slides_slideproperties_full(self):
         self.assert_error_behavior(
            get_presentation,
            expected_exception_type=custom_errors.InvalidInputError,
            expected_message="The 'fields' parameter is malformed or specifies an invalid field path.",
            presentationId=self.full_presentation_id, 
            fields="slides.slideProperties"
        )

    def test_get_presentation_field_slides_slideproperties_notespage_only(self):
        self.assert_error_behavior(
            get_presentation,
            expected_exception_type=custom_errors.InvalidInputError,
            expected_message="The 'fields' parameter is malformed or specifies an invalid field path.",
            presentationId=self.full_presentation_id, 
            fields="slides.slideProperties.notesPage"
        )
        
    def test_get_presentation_field_slides_slideproperties_notespage_objectid(self):
        self.assert_error_behavior(
            get_presentation,
            expected_exception_type=custom_errors.InvalidInputError,
            expected_message="The 'fields' parameter is malformed or specifies an invalid field path.",
            presentationId=self.full_presentation_id, 
            fields="slides.slideProperties.notesPage.objectId"
        )

    def test_get_presentation_field_slides_nonexistent_prop_in_slideproperties(self):
        self.assert_error_behavior(
            get_presentation,
            expected_exception_type=custom_errors.InvalidInputError,
            expected_message="The 'fields' parameter is malformed or specifies an invalid field path.",
            presentationId=self.full_presentation_id, 
            fields="slides.slideProperties.customData"
        )

    def test_get_presentation_field_masters_objectid_only(self):
        self.assert_error_behavior(
            get_presentation,
            expected_exception_type=custom_errors.InvalidInputError,
            expected_message="The 'fields' parameter is malformed or specifies an invalid field path.",
            presentationId=self.full_presentation_id, 
            fields="masters.objectId"
        )
    
    def test_get_presentation_fields_for_empty_slide_properties_in_db(self):
        self.assert_error_behavior(
            get_presentation,
            expected_exception_type=custom_errors.InvalidInputError,
            expected_message="The 'fields' parameter is malformed or specifies an invalid field path.",
            presentationId=self.full_presentation_id,
            fields="slides.slideProperties.notesPage"
        )

    def test_get_presentation_invalid_fields_unknown_nested_field(self):
        self.assert_error_behavior(
            get_presentation,
            expected_exception_type=custom_errors.InvalidInputError,
            expected_message="The 'fields' parameter is malformed or specifies an invalid field path.",
            presentationId=self.full_presentation_id,
            fields="slides.nonExistentProperty"
        )
        
    def test_get_presentation_invalid_fields_unknown_deeply_nested_field(self):
        self.assert_error_behavior(
            get_presentation,
            expected_exception_type=custom_errors.InvalidInputError,
            expected_message="The 'fields' parameter is malformed or specifies an invalid field path.",
            presentationId=self.full_presentation_id,
            fields="pageSize.width.nonExistentSubProperty"
        )

    def test_get_presentation_invalid_fields_malformed_double_dot(self):
         self.assert_error_behavior(
            get_presentation,
            expected_exception_type=custom_errors.InvalidInputError,
            expected_message="The 'fields' parameter is malformed or specifies an invalid field path.",
            presentationId=self.full_presentation_id,
            fields="slides..objectId"
        )

    def test_get_presentation_invalid_fields_malformed_trailing_dot(self):
         self.assert_error_behavior(
            get_presentation,
            expected_exception_type=custom_errors.InvalidInputError,
            expected_message="The 'fields' parameter is malformed or specifies an invalid field path.",
            presentationId=self.full_presentation_id,
            fields="slides."
        )
        
    def test_get_presentation_invalid_fields_malformed_leading_dot(self):
         self.assert_error_behavior(
            get_presentation,
            expected_exception_type=custom_errors.InvalidInputError,
            expected_message="The 'fields' parameter is malformed or specifies an invalid field path.",
            presentationId=self.full_presentation_id,
            fields=".title"
        )
        
    def test_get_presentation_invalid_fields_malformed_double_comma(self):
         self.assert_error_behavior(
            get_presentation,
            expected_exception_type=custom_errors.InvalidInputError,
            expected_message="The 'fields' parameter is malformed or specifies an invalid field path.",
            presentationId=self.full_presentation_id,
            fields="title,,slides"
        )
        
    def test_get_presentation_invalid_fields_mixed_valid_and_malformed(self):
         self.assert_error_behavior(
            get_presentation,
            expected_exception_type=custom_errors.InvalidInputError,
            expected_message="The 'fields' parameter is malformed or specifies an invalid field path.",
            presentationId=self.full_presentation_id,
            fields="title,slides..objectId"
        )

    def test_get_presentation_fields_requesting_subproperty_of_scalar(self):
         self.assert_error_behavior(
            get_presentation,
            expected_exception_type=custom_errors.InvalidInputError,
            expected_message="The 'fields' parameter is malformed or specifies an invalid field path.",
            presentationId=self.full_presentation_id,
            fields="title.subproperty" 
        )

    def test_get_presentation_fields_requesting_subproperty_of_list_item_incorrectly(self):
         self.assert_error_behavior(
            get_presentation,
            expected_exception_type=custom_errors.InvalidInputError,
            expected_message="The 'fields' parameter is malformed or specifies an invalid field path.",
            presentationId=self.full_presentation_id,
            fields="slides.masters" 
        )