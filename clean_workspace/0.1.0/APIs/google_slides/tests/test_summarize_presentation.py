import unittest
from typing import List, Dict, Any

from ..SimulationEngine.db import DB
from ..SimulationEngine.models import (
    PresentationModel, PageModel, SlideProperties,
    TextRun, TextElement, Shape, FontSize, Size, Dimension, Transform, PageProperties, BackgroundColor, OpaqueColor, RgbColor,SlideProperties
)
from ..SimulationEngine.custom_errors import NotFoundError, ValidationError
from ..presentations import summarize_presentation

from common_utils.base_case import BaseTestCaseWithErrorHandler


class TestSummarizePresentation(BaseTestCaseWithErrorHandler):

    def setUp(self):
        DB.clear()
        DB['users'] = {
            "me": {
                "files": {},
                "about": {
                    "user": {
                        "emailAddress": "me@example.com",
                        "displayName": "Me"
                    }
                }
            }
        }

    def _text_element(self, text: str) -> TextElement:
        return TextElement(textRun=TextRun(content=text))

    def _shape(self, text: str) -> Shape:
        return Shape(
            shapeType="TEXT_BOX",
            text={"textElements": [self._text_element(text)]}
        )

    def _slide(self, object_id: str, texts: List[str], notes: List[str] = None) -> PageModel:
        page_elements = [{"shape": self._shape(t)} for t in texts]
        # notes_elements = [{"shape": self._shape(n)} for n in (notes or [])]

        return PageModel(
            objectId=object_id,
            pageType="SLIDE",
            pageElements=page_elements,
            revisionId="rev-001",
            pageProperties=PageProperties(
                backgroundColor=BackgroundColor(
                    opaqueColor=OpaqueColor(
                        rgbColor=RgbColor(red=1, green=1, blue=1)
                    )
                )
            ),
            slideProperties=SlideProperties(
                masterObjectId="master-001",
                layoutObjectId="layout-001",
                isSkipped=False
            )
        )

    def _setup_presentation(self, presentation_id: str, title: str, slides: List[PageModel], revision_id: str = "rev-001"):
        model = PresentationModel(
            presentationId=presentation_id,
            title=title,
            revisionId=revision_id,
            slides=slides
        )
        print(model.presentationId)
        DB['users']['me']['files'][presentation_id] = model.model_dump(mode='json')
        DB['users']['me']['files'][presentation_id]['mimeType'] = 'application/vnd.google-apps.presentation'

    def test_basic_summary(self):
        pid = "pres-001"
        slide = self._slide("slide-1", ["Intro", "to", "AI"])
        self._setup_presentation(pid, "AI Presentation", [slide])

        result = summarize_presentation(pid)

        self.assertEqual(result["title"], "AI Presentation")
        self.assertEqual(result["slideCount"], 1)
        self.assertEqual(result["slides"][0]["content"], "Intro to AI")
        self.assertNotIn("notes", result["slides"][0])

    # def test_summary_with_notes(self):
    #     pid = "pres-002"
    #     slide = self._slide("slide-2", ["Slide content"], notes=["Note A", "Note B"])
    #     self._setup_presentation(pid, "With Notes", [slide])

    #     result = summarize_presentation(pid, include_notes=True)
    #     self.assertIn("notes", result["slides"][0])
    #     self.assertEqual(result["slides"][0]["notes"], "Note A Note B")

    def test_invalid_none_presentation_id(self):
        self.assert_error_behavior(
            func_to_call=summarize_presentation,
            expected_exception_type=ValidationError,
            expected_message="presentationId cannot be None.",
            presentationId=None
        )

    def test_presentation_not_found(self):
        self.assert_error_behavior(
            func_to_call=summarize_presentation,
            expected_exception_type=NotFoundError,
            expected_message="Presentation with ID 'not-there' not found or is not a presentation file.",
            presentationId="not-there"
        )


    def test_wrong_mime_type(self):
        DB['users']['me']['files']['bad-id'] = {
            "mimeType": "application/pdf"
        }
        self.assert_error_behavior(
            func_to_call=summarize_presentation,
            expected_exception_type=NotFoundError,
            expected_message="Presentation with ID 'bad-id' not found or is not a presentation file.",
            presentationId="bad-id"
        )

    def test_empty_presentation(self):
        pid = "empty"
        self._setup_presentation(pid, "Empty Pres", [])
        result = summarize_presentation(pid)

        self.assertEqual(result["slideCount"], 0)
        self.assertEqual(result["summary"], "This presentation contains no slides.")
