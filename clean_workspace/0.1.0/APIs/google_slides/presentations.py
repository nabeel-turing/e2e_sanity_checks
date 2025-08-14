# google_slides/presentations.py
from typing import List, Dict, Any, Optional, Callable, Tuple
import uuid
import copy 

from google_slides.SimulationEngine.db import DB
from google_slides.SimulationEngine import utils
from google_slides.SimulationEngine import models 
from google_slides.SimulationEngine.custom_errors import InvalidInputError, NotFoundError, ConcurrencyError
from typing import Dict, Any, List, Optional 

from .SimulationEngine.db import DB
from .SimulationEngine.utils import _extract_text_from_elements, _ensure_user
from .SimulationEngine.models import PresentationModel

from typing import Optional, List, Dict, Any, Set 
import uuid

from google_slides.SimulationEngine.db import DB
from google_slides.SimulationEngine import utils 
from google_slides.SimulationEngine.custom_errors import *
from google_slides.SimulationEngine.models import  PresentationModel,Size, Dimension, TextContent
from google_slides.SimulationEngine.models import PageModel

from typing import Dict, Any, List, Optional 

from .SimulationEngine.db import DB
from .SimulationEngine.utils import _extract_text_from_elements, _ensure_user
from .SimulationEngine.custom_errors import *

from typing import Optional, List, Dict, Any, Set 
import uuid

from google_slides.SimulationEngine.db import DB
from google_slides.SimulationEngine import utils 

def batch_update_presentation(presentationId: str, requests: List[Dict[str, Any]], writeControl: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Apply a batch of updates to a Google Slides presentation.

    This function applies a series of specified update operations to a Google Slides
    presentation in a single batch request. It allows for various modifications
    such as creating slides, adding shapes, inserting text, deleting objects,
    updating styles, and managing object groups, as defined by the list of `requests`.

    Args:
        presentationId (str): The ID of the presentation to update.
        requests (List[Dict[str, Any]]): A list of update requests to apply. Each object
            in the array must be one of the specified request types. Each request
            object typically has a single key identifying the type of request (e.g.,
            'createSlide'), and its value is a dictionary containing the parameters
            for that request. The supported request types and their structures are:
            - CreateSlideRequest: Corresponds to a dictionary with a 'createSlide' key.
                'createSlide' (Dict[str, Any]): Creates a new slide.
                    'objectId' (Optional[str]): A user-supplied object ID. If specified,
                        must be unique (5-50 chars, pattern [a-zA-Z0-9_][a-zA-Z0-9_-:]*).
                        If empty, a unique ID is generated.
                    'insertionIndex' (Optional[int]): Optional zero-based index where to
                        insert the slides. If unspecified, created at the end.
                    'slideLayoutReference' (Optional[Dict[str, Any]]): Layout reference
                        of the slide. If unspecified, uses a predefined BLANK layout.
                        One of 'predefinedLayout' or 'layoutId' must be provided if
                        'slideLayoutReference' itself is provided.
                        'predefinedLayout' (Optional[str]): A predefined layout type.
                            Enum: ["BLANK", "CAPTION_ONLY", "TITLE", "TITLE_AND_BODY",
                            "TITLE_AND_TWO_COLUMNS", "TITLE_ONLY", "SECTION_HEADER",
                            "SECTION_TITLE_AND_DESCRIPTION", "ONE_COLUMN_TEXT",
                            "MAIN_POINT", "BIG_NUMBER", "PREDEFINED_LAYOUT_UNSPECIFIED"].
                        'layoutId' (Optional[str]): Layout ID of one of the layouts in
                            the presentation.
                    'placeholderIdMappings' (Optional[List[Dict[str, Any]]]): Optional list
                        of object ID mappings from layout placeholders to slide placeholders.
                        Used only when 'slideLayoutReference' is specified. Each item is a
                        dictionary:
                        'objectId' (Optional[str]): User-supplied object ID for the new
                            placeholder on the slide (5-50 chars, pattern
                            [a-zA-Z0-9_][a-zA-Z0-9_-:]*). If empty, a unique ID is generated.
                        One of 'layoutPlaceholder' or 'layoutPlaceholderObjectId' must be provided.
                        'layoutPlaceholder' (Optional[Dict[str, Any]]): The placeholder on a
                            layout to be applied to a slide.
                            'type' (str): The type of the placeholder. Enum: ["TITLE",
                                "BODY", "CENTERED_TITLE", "SUBTITLE", "DATE_AND_TIME",
                                "FOOTER", "HEADER", "OBJECT", "CHART", "TABLE", "CLIP_ART",
                                "PICTURE", "SLIDE_IMAGE", "SLIDE_NUMBER"].
                            'index' (int): The index of the placeholder. Usually 0.
                        'layoutPlaceholderObjectId' (Optional[str]): The object ID of the
                            placeholder on a layout.
            - CreateShapeRequest: Corresponds to a dictionary with a 'createShape' key.
                'createShape' (Dict[str, Any]): Creates a new shape.
                    'objectId' (Optional[str]): Optional user-supplied object ID for the
                        shape (5-50 chars, pattern [a-zA-Z0-9_][a-zA-Z0-9_-:]*).
                        If empty, a unique ID is generated.
                    'elementProperties' (Optional[Dict[str, Any]]): Element properties
                        for the shape.
                        'pageObjectId' (Optional[str]): The object ID of the page where
                            the element is located.
                        'size' (Optional[Dict[str, Any]]): The size of the page element.
                            'width' (Optional[Dict[str, Any]]): Width dimension.
                                'magnitude' (Optional[float]): Magnitude of the dimension.
                                'unit' (Optional[str]): Unit of the dimension. Enum: ["EMU", "PT"].
                            'height' (Optional[Dict[str, Any]]): Height dimension.
                                'magnitude' (Optional[float]): Magnitude of the dimension.
                                'unit' (Optional[str]): Unit of the dimension. Enum: ["EMU", "PT"].
                        'transform' (Optional[Dict[str, Any]]): The transform of the
                            page element.
                            'scaleX' (Optional[float]): The X scaling factor.
                            'scaleY' (Optional[float]): The Y scaling factor.
                            'shearX' (Optional[float]): The X shearing factor.
                            'shearY' (Optional[float]): The Y shearing factor.
                            'translateX' (Optional[float]): The X translation.
                            'translateY' (Optional[float]): The Y translation.
                            'unit' (Optional[str]): Unit for translate. Enum: ["EMU", "PT"].
                    'shapeType' (str): The type of shape to create. Enum:
                        ["TYPE_UNSPECIFIED", "TEXT_BOX", "RECTANGLE", "ROUND_RECTANGLE",
                        "ELLIPSE", "ARC", "BENT_CONNECTOR_2", "BENT_CONNECTOR_3",
                        "BENT_CONNECTOR_4", "BENT_CONNECTOR_5", "CURVED_CONNECTOR_2",
                        "CURVED_CONNECTOR_3", "CURVED_CONNECTOR_4", "CURVED_CONNECTOR_5",
                        "LINE", "STRAIGHT_CONNECTOR_1", "TRIANGLE", "RIGHT_TRIANGLE",
                        "PARALLELOGRAM", "TRAPEZOID", "DIAMOND", "PENTAGON", "HEXAGON",
                        "HEPTAGON", "OCTAGON", "STAR_5", "ARROW_EAST", "ARROW_NORTH_EAST",
                        "ARROW_NORTH", "SPEECH", "CLOUD", "NOTCHED_RIGHT_ARROW"].
            - InsertTextRequest: Corresponds to a dictionary with an 'insertText' key.
                'insertText' (Dict[str, Any]): Inserts text into a shape or table cell.
                    'objectId' (str): Object ID of the shape or table.
                    'cellLocation' (Optional[Dict[str, Any]]): Optional table cell
                        location if inserting into a table.
                        'rowIndex' (Optional[int]): 0-based row index.
                        'columnIndex' (Optional[int]): 0-based column index.
                    'text' (str): The text to insert.
                    'insertionIndex' (Optional[int]): Optional 0-based index where text
                        will be inserted in Unicode code units.
            - ReplaceAllTextRequest: Corresponds to a dictionary with a 'replaceAllText' key.
                'replaceAllText' (Dict[str, Any]): Replaces all instances of specified text.
                    'replaceText' (str): The text that will replace matched text.
                    'containsText' (Dict[str, Any]): Criteria for matching text.
                        'text' (str): The text to search for.
                        'matchCase' (Optional[bool]): Indicates if the search should be
                            case sensitive. Defaults to False.
                        'searchByRegex' (Optional[bool]): Optional. True if the find value
                            should be treated as a regular expression. Defaults to False.
                    'pageObjectIds' (Optional[List[str]]): Optional. Limits matches to
                        page elements only on the given page IDs.
            - DeleteObjectRequest: Corresponds to a dictionary with a 'deleteObject' key.
                'deleteObject' (Dict[str, Any]): Deletes a page or page element.
                    'objectId' (str): Object ID of the page or page element to delete.
            - DeleteTextRequest: Corresponds to a dictionary with a 'deleteText' key.
                'deleteText' (Dict[str, Any]): Deletes text from a shape or table cell.
                    'objectId' (str): Object ID of the shape or table.
                    'cellLocation' (Optional[Dict[str, Any]]): Optional table cell location.
                        'rowIndex' (Optional[int]): 0-based row index.
                        'columnIndex' (Optional[int]): 0-based column index.
                    'textRange' (Dict[str, Any]): The range of text to delete.
                        'type' (str): The type of range. Enum: ["ALL", "FIXED_RANGE",
                            "FROM_START_INDEX", "RANGE_TYPE_UNSPECIFIED"].
                        'startIndex' (Optional[int]): Optional 0-based start index for
                            FIXED_RANGE and FROM_START_INDEX.
                        'endIndex' (Optional[int]): Optional 0-based end index for
                            FIXED_RANGE.
            - UpdateTextStyleRequest: Corresponds to a dictionary with an 'updateTextStyle' key.
                'updateTextStyle' (Dict[str, Any]): Updates the styling of text within a
                    Shape or Table.
                    'objectId' (str): Object ID of the shape or table with the text to be styled.
                    'cellLocation' (Optional[Dict[str, Any]]): Optional table cell location.
                        'rowIndex' (Optional[int]): 0-based row index.
                        'columnIndex' (Optional[int]): 0-based column index.
                    'style' (Dict[str, Any]): The TextStyle to apply.
                        'bold' (Optional[bool]): Whether the text is bold.
                        'italic' (Optional[bool]): Whether the text is italic.
                        'underline' (Optional[bool]): Whether the text is underlined.
                        'strikethrough' (Optional[bool]): Whether the text is struck through.
                        'fontFamily' (Optional[str]): The font family.
                        'fontSize' (Optional[Dict[str, Any]]): The font size.
                            'magnitude' (Optional[float]): The magnitude of the font size.
                            'unit' (Optional[str]): The unit of the font size. Enum: ["PT"].
                        'foregroundColor' (Optional[Dict[str, Any]]): Color of the text.
                            Structure defined by Google Slides API OptionalColor.
                    'textRange' (Dict[str, Any]): The range of text to style.
                        'type' (str): The type of range. Enum: ["ALL", "FIXED_RANGE",
                            "FROM_START_INDEX", "RANGE_TYPE_UNSPECIFIED"].
                        'startIndex' (Optional[int]): Optional start index.
                        'endIndex' (Optional[int]): Optional end index.
                    'fields' (str): Field mask (e.g., 'bold,fontSize') specifying which
                        style fields to update. Use '*' for all fields.
            - GroupObjectsRequest: Corresponds to a dictionary with a 'groupObjects' key.
                'groupObjects' (Dict[str, Any]): Groups page elements.
                    'groupObjectId' (Optional[str]): Optional user-supplied ID for the
                        new group (5-50 chars, pattern [a-zA-Z0-9_][a-zA-Z0-9_-:]*).
                    'childrenObjectIds' (List[str]): Object IDs of the page elements to
                        group (at least 2, on the same page, not already in another group).
            - UngroupObjectsRequest: Corresponds to a dictionary with an 'ungroupObjects' key.
                'ungroupObjects' (Dict[str, Any]): Ungroups objects.
                    'objectIds' (List[str]): Object IDs of the groups to ungroup (at least 1).
                        Groups must not be inside other groups and all on the same page.
            - UpdatePageElementAltTextRequest: Corresponds to a dictionary with an
              'updatePageElementAltText' key.
                'updatePageElementAltText' (Dict[str, Any]): Updates alt text of a page element.
                    'objectId' (str): Object ID of the page element.
                    'title' (Optional[str]): Optional. The new alt text title. If unset,
                        existing value is maintained.
                    'description' (Optional[str]): Optional. The new alt text description.
                        If unset, existing value is maintained.
            - UpdateSlidePropertiesRequest: Corresponds to a dictionary with an
              'updateSlideProperties' key.
                'updateSlideProperties' (Dict[str, Any]): Updates properties of a slide.
                    'objectId' (str): Object ID of the slide.
                    'slideProperties' (Dict[str, Any]): The SlideProperties to update.
                        'masterObjectId' (Optional[str]): The object ID of the master slide.
                        'layoutObjectId' (Optional[str]): The object ID of the layout slide.
                        'isSkipped' (Optional[bool]): Whether the slide is skipped in
                            show mode.
                        'notesPage' (Optional[Dict[str, Any]]): Notes page properties.
                            Structure defined by Google Slides API NotesPage.
                    'fields' (str): Field mask (e.g., 'isSkipped,notesPage.notesPageProperties')
                        specifying which slide properties to update. Use '*' for all.
            (Note: For a complete list and details of all request types and their
            parameters, refer to the Google Slides API documentation.)
        writeControl (Optional[Dict[str, Any]]): Optional. Provides control over how
            write requests are executed.
            'requiredRevisionId' (Optional[str]): The revision ID of the presentation
                required for this update. If the current revision is different, the
                request will fail.
            'targetRevisionId' (Optional[str]): Deprecated: Use requiredRevisionId.

    Returns:
        Dict[str, Any]: A dictionary representing the batch update response, with the
            following keys:
            'presentationId' (str): The ID of the presentation that was updated.
            'replies' (List[Dict[str, Any]]): A list of replies, one for each request in the
                batch, in the order of the original requests. The structure of each reply
                dictionary varies based on the type of request it corresponds to.
                For example, a reply for a 'createSlide' request could be
                `{'createSlide': {'objectId': 'new_slide_id'}}`.
            'writeControl' (Dict[str, Any]): Contains the new write control information for
                the presentation.
                'requiredRevisionId' (str): The revision ID of the presentation after the
                                            batch update.

    Raises:
        NotFoundError: If the presentation with the given 'presentation_id' does not exist.
        InvalidInputError: If the 'requests' list is malformed, contains invalid update
                           operations, or 'write_control' is invalid.
        ConcurrencyError: If a write control conflict occurs (e.g., the provided
                          revision ID in 'write_control' does not match the current
                          revision of the presentation).
        ValidationError: If input arguments fail validation.
    """
    if not isinstance(presentationId, str):
        raise InvalidInputError("Presentation ID must be a string.")
    if not presentationId:
        raise InvalidInputError("Presentation ID cannot be empty.")
        
    user_id_for_utils = "me" 
    utils._ensure_user(user_id_for_utils)

    drive_file_entry = DB['users'][user_id_for_utils]['files'].get(presentationId, None)
    if not drive_file_entry or drive_file_entry.get("mimeType") != "application/vnd.google-apps.presentation":
        raise NotFoundError(f"Presentation with ID '{presentationId}' not found or is not a presentation.")

    original_copy = copy.deepcopy(drive_file_entry)
    presentation_data_to_modify = models.PresentationModel.model_validate(drive_file_entry).model_dump()

    if writeControl:
        try:
            validated_wc = models.WriteControlRequest(**writeControl) 
            required_rev_id = validated_wc.requiredRevisionId or validated_wc.targetRevisionId            
            current_rev_id = presentation_data_to_modify.get('revisionId')
            if required_rev_id and current_rev_id != required_rev_id:
                raise ConcurrencyError(
                    f"Required revision ID '{required_rev_id}' does not match current revision ID '{current_rev_id}'."
                )
        except ConcurrencyError: raise
        except Exception as e: 
            raise InvalidInputError(f"Invalid writeControl: {e}")

    replies: List[Dict[str, Any]] = []

    if not isinstance(requests, list):
        raise InvalidInputError("Requests payload must be a list.")

    REQUEST_PROCESSORS: Dict[str, Tuple[Callable, str]] = {
    "createSlide": (utils._handle_create_slide, "CreateSlideRequestModel"),
    "createShape": (utils._handle_create_shape, "CreateShapeRequestModel"),
    "insertText": (utils._handle_insert_text, "InsertTextRequestModel"),
    "replaceAllText": (utils._handle_replace_all_text, "ReplaceAllTextRequestModel"),
    "deleteObject": (utils._handle_delete_object, "DeleteObjectRequestModel"),
    "deleteText": (utils._handle_delete_text, "DeleteTextRequestModel"),
    # "duplicateObject": (utils._handle_duplicate_object, "DuplicateObjectRequestModel"),
    "updateTextStyle": (utils._handle_update_text_style, "UpdateTextStyleRequestModel"),
    "groupObjects": (utils._handle_group_objects, "GroupObjectsRequestModel"),
    "ungroupObjects": (utils._handle_ungroup_objects, "UngroupObjectsRequestModel"),
    "updatePageElementAltText": (utils._handle_update_page_element_alt_text, "UpdatePageElementAltTextRequestModel"),
    "updateSlideProperties": (utils._handle_update_slide_properties, "UpdateSlidePropertiesRequestModel"),
    }
    
    for i, request_item_dict in enumerate(requests):
        if not isinstance(request_item_dict, dict) or len(request_item_dict) != 1:
            drive_file_entry = original_copy 
            raise InvalidInputError(
                f"Request at index {i} is malformed: must be a dictionary with a single key."
            )
        
        request_type_key = list(request_item_dict.keys())[0]
        raw_params_dict = request_item_dict.get(request_type_key) 
        if not isinstance(raw_params_dict, dict): # Ensure params part is a dict
            drive_file_entry = original_copy 
            raise InvalidInputError(f"Parameters for request '{request_type_key}' at index {i} must be a dictionary.")


        if request_type_key not in REQUEST_PROCESSORS:
            drive_file_entry = original_copy 
            raise InvalidInputError(f"Unsupported request type: '{request_type_key}' at index {i}.")

        handler_func, _ = REQUEST_PROCESSORS[request_type_key] # Pydantic model name string not needed here directly
        
        try:
            reply = handler_func(presentation_data_to_modify, raw_params_dict, user_id_for_utils)
            replies.append(reply)
        except Exception as e:
            drive_file_entry = original_copy 
            if isinstance(e, (NotFoundError, InvalidInputError, ConcurrencyError)):
                raise
            raise InvalidInputError(f"Error processing request at index {i} (type: {request_type_key}): {type(e).__name__} - {str(e)}")


    drive_file_entry['updateTime'] = utils.get_current_timestamp_iso()
    new_revision_id = str(uuid.uuid4()) 
    drive_file_entry['revisionId'] = new_revision_id
    
    drive_file_entry['version'] = new_revision_id
    drive_file_entry['modifiedTime'] = utils.get_current_timestamp_iso()

    return {
        "presentationId": presentationId,
        "replies": replies,
        "writeControl": {"requiredRevisionId": new_revision_id}
    }


def summarize_presentation(presentationId : str, include_notes: bool = False) -> Dict[str, Any]:
    """Extract text content from all slides in a presentation for summarization purposes.

    This function processes a presentation, identified by `presentationId`, to extract
    all text content from its slides. The primary purpose of this extraction is to
    gather text for summarization. If the `include_notes` parameter is set to true,
    speaker notes associated with the slides are also included in the extracted content.
    The function returns a dictionary detailing the extracted text, including the
    presentation's ID, a list of text elements per slide (with optional speaker notes),
    and a fully concatenated string of all text suitable for summarization.

    Args:
        presentationId (str): The ID of the presentation to summarize.
        include_notes (bool): Whether to include speaker notes in the summary (default: False).

    Returns:
        Dict[str, Any]: A dictionary summarizing the text content of the presentation. Includes the following keys:
            title (str): The title of the presentation, or "Untitled Presentation" if missing.
            slideCount (int): The total number of slides processed from the presentation.
            lastModified (str): A string indicating the revision ID (e.g., "Revision <id>") or "Unknown" if not available.
            slides (List[dict]): A list of slide-level summaries, where each item contains:
                slideNumber (int): The 1-based index of the slide in the presentation.
                slideId (str): The object ID of the slide.
                content (str): The extracted text content from shapes and text elements on the slide.
                notes (Optional[str]): Speaker notes text, only included if `include_notes` is True and notes are present.

    Raises:
        NotFoundError: If the presentation with the given 'presentation_id' does not exist.
        ValidationError: If input arguments fail validation.
    """
    if presentationId is None:
        raise ValidationError("presentationId cannot be None.")
    
    user_id_for_access = "me" 
    _ensure_user(user_id_for_access) 

    user_files = DB.get('users', {}).get(user_id_for_access, {}).get('files', {})
    drive_file_entry = user_files.get(presentationId)

    if not drive_file_entry or drive_file_entry.get("mimeType") != "application/vnd.google-apps.presentation":
        raise NotFoundError(f"Presentation with ID '{presentationId}' not found or is not a presentation file.")
    
    presentation = PresentationModel.model_validate(drive_file_entry).model_dump(mode='json')

    if not presentation['slides']:
        return {
                    "title": presentation['title'] or "Untitled Presentation",
                    "slideCount": 0,
                    "summary": "This presentation contains no slides."
                }

    slides_content = []
    for index, slide in enumerate(presentation['slides']):
        slide_number = index + 1
        slide_id = slide['objectId'] or f"slide_{slide_number}"

        slide_text = _extract_text_from_elements(slide['pageElements'])
        slide_text_str = " ".join(slide_text)

        notes_text_str = ""
        if include_notes and slide['slideProperties'] and slide['slideProperties']['notesPage']:
            notes_elements = slide['slideProperties']['notesPage']['pageElements']
            notes_text = _extract_text_from_elements(notes_elements)
            notes_text_str = " ".join(notes_text).strip()

        slide_info = {
            "slideNumber": slide_number,
            "slideId": slide_id,
            "content": slide_text_str
        }

        if include_notes and notes_text_str:
            slide_info["notes"] = notes_text_str

        slides_content.append(slide_info)

    summary = {
        "title": presentation['title'] or "Untitled Presentation",
        "slideCount": len(slides_content),
        "lastModified": f"Revision {presentation['revisionId']}" if presentation['revisionId'] else "Unknown",
        "slides": slides_content
    }

    return summary






def get_page(presentationId: str, pageObjectId: str) -> Dict[str, Any]:
    """
    Get details about a specific page (slide) in a presentation.

    This function gets details about a specific page (slide) in a presentation.

    Args:
        presentationId (str): The ID of the presentation.
        pageObjectId (str): The object ID of the page (slide) to retrieve.

    Returns:
        Dict[str, Any]: Detailed information about a specific page (slide). Contains the following keys:
            objectId (str)
            pageType (str)
            revisionId (str)
            pageProperties (dict)
                backgroundColor (dict)
                    opaqueColor (dict)
                        rgbColor (dict)
                            red (float)
                            green (float)
                            blue (float)
            notesProperties (dict, optional)
                speakerNotesObjectId (str)
            slideProperties (dict, optional)
                masterObjectId (str)
                layoutObjectId (str)
            layoutProperties (dict, optional)
                masterObjectId (str)
                name (str)
                displayName (str)
            masterProperties (dict, optional)
                displayName (str)
            pageElements (list of dict)
                objectId (str)
                size (dict)
                    width (dict)
                        magnitude (float)
                        unit (str)
                    height (dict)
                        magnitude (float)
                        unit (str)
                transform (dict)
                    scaleX (float)
                    scaleY (float)
                    translateX (float)
                    translateY (float)
                    unit (str)
                shape (dict)
                    shapeType (str)
                    text (dict)
                        textElements (list of dict)
                            textRun (dict)
                                content (str)
                                style (dict)
                                    fontFamily (str)
                                    fontSize (dict)
                                        magnitude (float)
                                        unit (str)

    Raises:
        PermissionDeniedError: If the authenticated user does not have permission to access the specified presentation or page.
        NotFoundError: If the presentation with 'presentation_id' or the page with 'page_object_id' does not exist within that presentation.
        InvalidInputError: If 'presentation_id' or 'page_object_id' are malformed.

    """
    if not presentationId or not isinstance(presentationId, str):
        raise InvalidInputError("presentationId must be a non-empty string.")
    if not pageObjectId or not isinstance(pageObjectId, str):
        raise InvalidInputError("pageObjectId must be a non-empty string.")

    user_data = DB.get('users', {}).get('me', {})
    if not user_data:
        raise NotFoundError("User data not found.")

    user_files = user_data.get('files', {})
    if presentationId not in user_files:
        raise NotFoundError(f"Presentation with ID '{presentationId}' not found.")

    presentation_data = user_files[presentationId]
    if presentation_data.get("mimeType") != "application/vnd.google-apps.presentation":
        raise NotFoundError(f"File with ID '{presentationId}' is not a Google Slides presentation.")

    # Search through slides, masters, layouts, and notesMaster
    for section in ['slides','layouts','masters']:
        for page in presentation_data.get(section, []):
            if isinstance(page, dict) and page.get('objectId') == pageObjectId:
                model = PageModel.model_validate(page)
                return model.model_dump()

    if 'notesMaster' in presentation_data:
        for slide in presentation_data['notesMaster']:
            if slide.get('objectId') == pageObjectId:
                page = slide
                model = PageModel.model_validate(page)
                return model.model_dump()

    raise NotFoundError(f"Page with object ID '{pageObjectId}' not found in presentation '{presentationId}'.")
  
  
def get_presentation(presentationId: str, fields: Optional[str] = None) -> Dict[str, Any]:
    """Get details about a Google Slides presentation.

        This function retrieves details about a Google Slides presentation. The
        `presentationId` argument specifies which presentation to fetch. An optional
        `fields` argument can be used as a mask to specify which parts of the
        presentation data should be included in the response, allowing for more
        targeted data retrieval.

        Args:
            presentationId (str): The ID of the presentation to retrieve.
            fields (Optional[str]): Optional. A mask specifying which fields to include
                in the response (e.g., 'slides,pageSize').

        Returns:
            Dict[str, Any]: A dictionary representing a Google Slides presentation with the following structure:
                presentationId (str): The unique ID of the presentation.
                title (Optional[str]): The title of the presentation.
                pageSize (Optional[dict]): The size of the presentation pages.
                    width (dict): Contains magnitude (float) and unit (str) for page width.
                    height (dict): Contains magnitude (float) and unit (str) for page height.
                slides (List[dict]): A list of slide pages with the following keys:
                    objectId (str): Unique ID of the slide.
                    pageType (str): Page type, must be "SLIDE".
                    revisionId (str): Revision ID of the slide.
                    pageProperties (dict): Background color and other page-level properties.
                        backgroundColor (dict): Background color info.
                            opaqueColor (dict): Color container.
                                rgbColor (dict): RGB color values with red, green, blue (float each).
                    slideProperties (dict): Properties specific to slides.
                        masterObjectId (Optional[str]): Reference to master slide.
                        layoutObjectId (Optional[str]): Reference to layout slide.
                        isSkipped (Optional[bool]): Indicates whether the slide is skipped.
                        notesPage (Optional[dict]): Associated notes page, if any.
                    layoutProperties (None): Must not be present for SLIDE type.
                    masterProperties (None): Must not be present for SLIDE type.
                    notesProperties (None): Must not be present for SLIDE type.
                    pageElements (List[dict]): Elements on the page, each containing:
                        objectId (str): Unique ID of the element.
                        size (Optional[dict]): Width and height dimensions.
                            width (dict): magnitude (float), unit (str).
                            height (dict): magnitude (float), unit (str).
                        transform (Optional[dict]): Position and scale transformations.
                            scaleX, scaleY, translateX, translateY (float), unit (str).
                        shape (Optional[dict]): Shape information, if applicable.
                            shapeType (str): Type of shape (e.g., TEXT_BOX).
                            text (Optional[dict]): Text content.
                                textElements (List[dict]): Text segments.
                                    textRun (dict): Contains content and style.
                                        content (str): Text string.
                                        style (dict): Styling info.
                                            fontFamily (str): Font name.
                                            fontSize (dict): magnitude (float), unit (str).
                masters (List[dict]): List of master slides with structure like `slides`, but must have `masterProperties` and exclude other conflicting fields.
                layouts (List[dict]): List of layout slides with structure like `slides`, but must have `layoutProperties` and exclude other conflicting fields.
                notesMaster (Optional[dict]): A special page representing the notes master; structured like a slide but with pageType "NOTES_MASTER".
                locale (Optional[str]): The presentation locale (e.g., "en-US").
                revisionId (Optional[str]): Revision ID representing the version of the presentation.


        Raises:
            NotFoundError: If the presentation with the given 'presentation_id' does
                not exist.
            InvalidInputError: If the 'fields' parameter is malformed or specifies
                an invalid field path.
            ValidationError: If input arguments fail validation.
        """
    # Input validation
    if not isinstance(presentationId, str):
        raise InvalidInputError("presentationId must be a string.")
    if not presentationId.strip():
        raise InvalidInputError("presentationId must be a non-empty string.")
    if fields is not None and not isinstance(fields, str):
        raise InvalidInputError("fields must be a string if provided.")

    # --- Fetch Presentation Data ---
    user_id_for_access = "me" 
    if not DB.get('users', {}).get(user_id_for_access, {}).get('files'):
         utils._ensure_user(user_id_for_access)

    user_files = DB.get('users', {}).get(user_id_for_access, {}).get('files', {})
    drive_file_entry = user_files.get(presentationId)

    if not drive_file_entry :
        raise NotFoundError(f"Presentation with ID '{presentationId}' not found or is not a presentation file.") 
    
    if drive_file_entry.get("mimeType") != "application/vnd.google-apps.presentation":
        raise NotFoundError(f"Presentation with {presentationId} is not a presentation file.") 
    

    validated_result = PresentationModel.model_validate(drive_file_entry)
    full_result = validated_result.model_dump(mode="json")

    # --- MODIFIED 'fields' HANDLING ---
    # If fields is None OR an empty string (or whitespace only after strip), return all fields.
    if fields is None or fields == "" or not fields.strip():
        return full_result 
    
    # If fields is provided and not effectively empty, proceed to parse and validate.
    # (The previous `if not stripped_fields_input: raise InvalidInputError(...)` block is removed
    # because its condition is now covered by the `or not fields.strip()` above to return full_result)
    field_parts = fields.split(',') # No need to strip `fields` again, already handled.
    requested_field_names: Set[str] = set()

    if not field_parts: # Should generally not be hit if 'fields' was non-empty and non-whitespace
         raise InvalidInputError("The 'fields' parameter is malformed or specifies an invalid field path.")

    for part in field_parts:
        stripped_part = part.strip()
        if not stripped_part: 
            # This specifically catches cases like "title,,slides" or ",title"
            raise InvalidInputError("The 'fields' parameter is malformed or specifies an invalid field path.")
        requested_field_names.add(stripped_part)
    
    if not requested_field_names: # Should only be hit if input 'fields' was like "," (all parts empty)
        raise InvalidInputError("The 'fields' parameter is malformed or specifies an invalid field path.")
        
    valid_top_level_fields: Set[str] = {"title", "pageSize", "slides", "masters", "layouts","notesMaster","locale","revisionId"}
    final_result: Dict[str, Any] = {'presentationId': presentationId}

    for field_name in requested_field_names:
        if "." in field_name or field_name not in valid_top_level_fields: 
            raise InvalidInputError("The 'fields' parameter is malformed or specifies an invalid field path.")
        if field_name in full_result: 
            final_result[field_name] = full_result[field_name]
    
    return final_result
  
  

def create_presentation(title: str) -> Dict[str, Any]:
    """Create a new Google Slides presentation.

    This function creates a new Google Slides presentation using the provided title.
    An initial blank slide is typically created with the presentation.

    Args:
        title (str): The title of the presentation.

    Returns:
        Dict[str, Any]: A dictionary representing the newly created presentation, with the following structure:
            presentationId (str): A unique identifier (UUID) for the presentation.
            title (Optional[str]): The title of the presentation as provided by the user.
            pageSize (Optional[dict]): Returned as `None`.
            slides (List[dict]): Returned as `None`.
            masters (List[dict]): Returned as `None`.
            layouts (List[dict]): Returned as `None`.
            notesMaster (Optional[dict]): Returned as `None`.
            locale (Optional[str]): Returned as `None`.
            revisionId (Optional[str]): A UUID representing the revision of the presentation.
    Raises:
        InvalidInputError: If the provided input, such as the title, is invalid
            (e.g., empty, too long, or incorrect format).
    """

    # 1. Input Validation
    if not title or title.isspace():
        raise InvalidInputError("Presentation title cannot be empty or contain only whitespace.")

    # 2. Ensure user and DB structure for presentations
    utils._ensure_user(userId="me") 

    presentation_id = str(uuid.uuid4()) 
    current_iso_time = utils.get_current_timestamp_iso()
    presentation_revision_id = str(uuid.uuid4()) 

    presentation_obj = PresentationModel(
        presentationId=presentation_id, 
        title=title,
        revisionId=presentation_revision_id 
    )
    new_presentation_model_dict = presentation_obj.model_dump()

    # 5. Store the new presentation as a GDrive file entry
    drive_file_entry = utils._ensure_presentation_file(presentation=new_presentation_model_dict, userId="me")

    response_data = new_presentation_model_dict

    return response_data
