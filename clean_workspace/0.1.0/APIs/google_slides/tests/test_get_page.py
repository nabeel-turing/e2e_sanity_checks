import unittest
import copy
from datetime import datetime # Not strictly used in DB setup if using ISO strings, but good practice if needed.
from typing import Dict, Any
# CRITICAL IMPORT FOR CUSTOM ERRORS (excluding Pydantic's ValidationError):
from ..SimulationEngine import custom_errors
from ..SimulationEngine.db import DB
from ..presentations import get_page
from common_utils.base_case import BaseTestCaseWithErrorHandler
from pydantic import ValidationError
# Assume BaseTestCaseWithErrorHandler is globally available
# Assume get_page function is globally available
# Assume DB dictionary is globally available

class TestGetPage(BaseTestCaseWithErrorHandler):

    def setUp(self):
        self._original_DB_state = copy.deepcopy(DB)
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
                      "driveId": "My-Drive-ID",
                      "name": "Test Presentation 1",
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
                              "opaqueColor": ""
                            }
                          },
                          "pageElements": [],
                          "revisionId": "rev_slide_minimal"
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
                      "notesMaster": [
                        {
                          "objectId": "notes_master1",
                          "pageType": "NOTES_MASTER",
                          "pageProperties": {
                            "backgroundColor": {
                              "opaqueColor": {
                                "rgbColor": {
                                  "red": 0.98,
                                  "green": 0.98,
                                  "blue": 0.98
                                }
                              }
                            }
                          },
                          "pageElements": [
                            {
                              "objectId": "slide_image_placeholder",
                              "size": {
                                "width": {
                                  "magnitude": 400,
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
                                "translateX": 50.0,
                                "translateY": 50.0,
                                "unit": "PT"
                              },
                              "shape": {
                                "shapeType": "RECTANGLE"
                              },
                              "placeholder": {
                                "type": "SLIDE_IMAGE",
                                "index": 0
                              }
                            },
                            {
                              "objectId": "body_placeholder_notes",
                              "size": {
                                "width": {
                                  "magnitude": 500,
                                  "unit": "PT"
                                },
                                "height": {
                                  "magnitude": 150,
                                  "unit": "PT"
                                }
                              },
                              "transform": {
                                "scaleX": 1.0,
                                "scaleY": 1.0,
                                "translateX": 50.0,
                                "translateY": 400.0,
                                "unit": "PT"
                              },
                              "shape": {
                                "shapeType": "TEXT_BOX"
                              },
                              "placeholder": {
                                "type": "BODY",
                                "index": 0
                              }
                            }
                          ],
                          "revisionId": "rev_notes_master1"
                        }
                      ],
                      "revisionId": "rev_pres1"
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
    def tearDown(self):
        DB.clear()
        DB.update(self._original_DB_state)

    def test_get_slide_page_success(self):
        presentation_id = "pres1"
        page_object_id = "slide1_page1"

        page_details = get_page(presentationId=presentation_id, pageObjectId=page_object_id)

        self.assertIsInstance(page_details, dict)
        self.assertEqual(page_details['objectId'], page_object_id)
        self.assertEqual(page_details['pageType'], "SLIDE")
        self.assertEqual(page_details['revisionId'], "rev_slide1")
        self.assertEqual(page_details['pageProperties'], {
            "backgroundColor": {
                "opaqueColor": {"rgbColor": {"red": 1.0, "green": 0.0, "blue": 0.0},
                                'themeColor': None}
            }
        })
        self.assertEqual(page_details['slideProperties'], {
            "masterObjectId": "master1",
            "layoutObjectId": "layout_for_slide1",
            "isSkipped":False,
            "notesPage":None
        })
        self.assertEqual(page_details['notesProperties'], None)
        self.assertEqual(page_details['masterProperties'], None)
        self.assertEqual(page_details['layoutProperties'], None)
        self.assertEqual(len(page_details['pageElements']), 2)
        self.assertEqual(page_details['pageElements'][0]['objectId'], "element1_slide1")
        self.assertEqual(page_details['pageElements'][1]['shape']['text']['textElements'][0]['textRun']['content'], "Hello ")

    def test_get_notes_master_page_success(self):
            presentation_id = "pres1"
            page_object_id = "notes_master1"

            page_details = get_page(presentationId=presentation_id, pageObjectId=page_object_id)

            self.assertIsInstance(page_details, dict)
            self.assertEqual(page_details['objectId'], page_object_id)
            self.assertEqual(page_details['pageType'], "NOTES_MASTER")
            self.assertEqual(page_details['revisionId'], "rev_notes_master1")
            self.assertEqual(page_details['pageProperties'], {
                "backgroundColor": {
                    "opaqueColor": {"rgbColor": {"red": 0.98, "green": 0.98, "blue": 0.98},
                                    'themeColor': None}
                }
            })


    def test_get_master_page_success(self):
        presentation_id = "pres1"
        page_object_id = "master_new1"

        page_details = get_page(presentationId=presentation_id, pageObjectId=page_object_id)

        self.assertIsInstance(page_details, dict)
        self.assertEqual(page_details['objectId'], page_object_id)
        self.assertEqual(page_details['pageType'], "MASTER")
        self.assertEqual(page_details['revisionId'], "rev_master_new1")
        self.assertEqual(page_details['pageProperties'], {
            "backgroundColor": {
                "opaqueColor": {"rgbColor": {"red": 0.95, "green": 0.95, "blue": 0.95},
                                'themeColor': None}
            }
        })
        self.assertEqual(page_details['masterProperties'], {"displayName": "Master Title Placeholder"})
        self.assertEqual(len(page_details['pageElements']), 1)
        self.assertEqual(page_details['pageElements'][0]['shape']['shapeType'], "TEXT_BOX")
        self.assertEqual(
            page_details['pageElements'][0]['shape']['text']['textElements'][0]['textRun']['content'],
            "Master Title Placeholder"
        )

    def test_get_layout_page_success(self):
        presentation_id = "pres1"
        page_object_id = "layout_basic_title_content"

        page_details = get_page(presentationId=presentation_id, pageObjectId=page_object_id)

        self.assertIsInstance(page_details, dict)
        self.assertEqual(page_details['objectId'], page_object_id)
        self.assertEqual(page_details['pageType'], "LAYOUT")
        self.assertEqual(page_details['revisionId'], "rev_layout_basic")
        self.assertEqual(page_details['layoutProperties']['displayName'], "Basic Title and Content")
        self.assertEqual(page_details['pageProperties'], {
            "backgroundColor": {
                "opaqueColor": {"rgbColor": {"red": 1.0, "green": 1.0, "blue": 1.0},
                                'themeColor': None}
            }
        })
        
    def test_get_page_presentation_not_found(self):
        self.assert_error_behavior(
            get_page,
            custom_errors.NotFoundError,
            "Presentation with ID 'nonexistent_pres_id' not found.",
            presentationId="nonexistent_pres_id",
            pageObjectId="any_page_id"
        )

    def test_get_page_page_object_not_found(self):
        # This ID should not exist in slides, notesPages, or layouts
        self.assert_error_behavior(
            get_page,
            custom_errors.NotFoundError,
            "Page with object ID 'completely_nonexistent_page_id' not found in presentation 'pres1'.",
            presentationId="pres1",
            pageObjectId="completely_nonexistent_page_id"
        )

    def test_get_page_invalid_presentation_id_type(self):
        self.assert_error_behavior(
            get_page,
            custom_errors.InvalidInputError,
            "presentationId must be a non-empty string.",
            presentationId=12345,
            pageObjectId="any_page_id"
        )

    def test_get_page_empty_presentation_id(self):
        self.assert_error_behavior(
            get_page,
            custom_errors.InvalidInputError,
            "presentationId must be a non-empty string.",
            presentationId="",
            pageObjectId="any_page_id"
        )

    def test_get_page_invalid_page_object_id_type(self):
        self.assert_error_behavior(
            get_page,
            custom_errors.InvalidInputError,
            "pageObjectId must be a non-empty string.",
            presentationId="pres1",
            pageObjectId=67890
        )

    def test_get_page_empty_page_object_id(self):
        self.assert_error_behavior(
            get_page,
            custom_errors.InvalidInputError,
            "pageObjectId must be a non-empty string.",
            presentationId="pres1",
            pageObjectId=""
        )

    def test_not_a_presentation(self):
        self.assert_error_behavior(
            get_page,
            custom_errors.NotFoundError,
            "File with ID 'file-1' is not a Google Slides presentation.",
            presentationId="file-1",
            pageObjectId="any_page_id"
        )

if __name__ == '__main__':
    unittest.main()
