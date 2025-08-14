import json
import os


DB = {
    "files": [
        {
            "fileKey": "1SORSDcBJjENuSp0rTi9dQ",
            "name": "Purity UI Dashboard - Chakra UI Dashboard",
            "lastModified": "2024-05-10T12:35:00Z",
            "thumbnailUrl": "https://example.com/thumbnails/02380234.png",
            "version": "1234567890",
            "role": "owner",
            "editorType": "figma",
            "linkAccess": "view",
            "schemaVersion": 0,
            "projectId": "project_alpha_design_system",
            "annotation_categories": [
                {
                    "id": "cat_ux_feedback_purity",
                    "name": "UX Feedback",
                    "color": {"r": 0.98, "g": 0.6, "b": 0, "a": 1}
                },
                {
                    "id": "cat_dev_note_purity",
                    "name": "Developer Note",
                    "color": {"r": 0.2, "g": 0.5, "b": 0.9, "a": 1}
                }
            ],
            "default_connector_id": "CONN:INTRO:001",
            "document": {
                "id": "0:0",
                "name": "Document",
                "type": "DOCUMENT",
                "scrollBehavior": "SCROLLS",
                "currentPageId":"1516:368",
                "children": [
                    {
                        "id": "1516:368",
                        "name": "👋 Introduction Page",
                        "type": "CANVAS",
                        "scrollBehavior": "SCROLLS",
                        "backgroundColor": {
                            "r": 0.9607843160629272,
                            "g": 0.9647058844566345,
                            "b": 0.9803921580314636,
                            "a": 1,
                        },
                        "prototypeStartNodeID": "1516:9022",
                        "flowStartingPoints": [
                            {
                                "nodeId": "1516:9022",
                                "name": "Start Here",
                                "scale": 1,
                                "rotation": 0,
                            }
                        ],
                        "prototypeDevice": {
                            "type": "APPLE_IPHONE_13_PRO_GRAPHITE",
                            "rotation": "NONE",
                            "size": {"width": 390, "height": 844},
                            "presetIdentifier": "APPLE_IPHONE_13_PRO_GRAPHITE",
                        },
                        "exportSettings": [
                            {
                                "suffix": "",
                                "format": "PNG",
                                "constraint": {"type": "SCALE", "value": 1},
                                "contentsOnly": True,
                            }
                        ],
                        "children": [
                            {
                                "id": "1516:9022",
                                "name": "Main Dashboard Screen",
                                "type": "FRAME",
                                "visible": True,
                                "locked": False,
                                "opacity": 1,
                                "rotation": 0,
                                "blendMode": "PASS_THROUGH",
                                "isMask": False,
                                "isFixed": False,
                                "absoluteBoundingBox": {
                                    "x": -2000,
                                    "y": -574,
                                    "width": 1440,
                                    "height": 1024,
                                },
                                "absoluteRenderBounds": {
                                    "x": -2000,
                                    "y": -574,
                                    "width": 1440,
                                    "height": 1024,
                                },
                                "constraints": {
                                    "vertical": "TOP",
                                    "horizontal": "LEFT",
                                },
                                "fills": [
                                    {
                                        "type": "SOLID",
                                        "visible": True,
                                        "opacity": 1,
                                        "blendMode": "NORMAL",
                                        "color": {"r": 1, "g": 1, "b": 1, "a": 1},
                                        "boundVariables": {
                                            "color": {
                                                "id": "V:987/654",
                                                "type": "VARIABLE_ALIAS",
                                            }
                                        },
                                    }
                                ],
                                "strokes": [],
                                "strokeWeight": 1,
                                "strokeAlign": "INSIDE",
                                "cornerRadius": 0,
                                "topLeftRadius": 0,
                                "topRightRadius": 0,
                                "bottomRightRadius": 0,
                                "bottomLeftRadius": 0,
                                "effects": [],
                                "layoutAlign": "INHERIT",
                                "layoutGrow": 0,
                                "styles": {
                                    "fills": "S:151:37,Purity UI Dashboard - Chakra UI Dashboard"
                                },
                                "exportSettings": [],
                                "prototypeInteractions": [],
                                "boundVariables": {
                                    "width": {
                                        "id": "V:987/111",
                                        "type": "VARIABLE_ALIAS",
                                    },
                                    "height": {
                                        "id": "V:987/222",
                                        "type": "VARIABLE_ALIAS",
                                    },
                                },
                                "clipsContent": True,
                                "background": [
                                    {
                                        "type": "SOLID",
                                        "visible": True,
                                        "opacity": 1,
                                        "blendMode": "NORMAL",
                                        "color": {"r": 1, "g": 1, "b": 1, "a": 1},
                                    }
                                ],
                                "layoutMode": "VERTICAL",
                                "layoutWrap": "NO_WRAP",
                                "primaryAxisSizingMode": "AUTO",
                                "counterAxisSizingMode": "AUTO",
                                "primaryAxisAlignItems": "MIN",
                                "counterAxisAlignItems": "MIN",
                                "paddingLeft": 20,
                                "paddingRight": 20,
                                "paddingTop": 20,
                                "paddingBottom": 20,
                                "itemSpacing": 16,
                                "itemReverseZIndex": False,
                                "strokesIncludedInLayout": False,
                                "layoutGrids": [
                                    {
                                        "pattern": "COLUMNS",
                                        "sectionSize": 100,
                                        "visible": False,
                                        "color": {
                                            "r": 0.5,
                                            "g": 0.5,
                                            "b": 0.5,
                                            "a": 0.2,
                                        },
                                        "alignment": "STRETCH",
                                        "gutterSize": 20,
                                        "offset": 0,
                                        "count": 12,
                                    }
                                ],
                                "children": [
                                    {
                                        "id": "1516:9023",
                                        "name": "Page Title",
                                        "type": "TEXT",
                                        "annotations": [
                                            {
                                                "annotationId": "anno_title_feedback_001",
                                                "labelMarkdown": "Consider increasing font size for better readability on larger screens.",
                                                "categoryId": "cat_ux_feedback_purity",
                                                "properties": [
                                                    {"type": "severity", "value": "medium"},
                                                    {"type": "author", "value": "jane.doe@example.com"}
                                                ]
                                            }
                                        ],
                                        "visible": True,
                                        "locked": False,
                                        "opacity": 1,
                                        "rotation": 0,
                                        "blendMode": "PASS_THROUGH",
                                        "isMask": False,
                                        "absoluteBoundingBox": {
                                            "x": -1980,
                                            "y": -554,
                                            "width": 250,
                                            "height": 38,
                                        },
                                        "absoluteRenderBounds": {
                                            "x": -1980.5,
                                            "y": -554.2,
                                            "width": 250.9,
                                            "height": 38.4,
                                        },
                                        "constraints": {
                                            "vertical": "TOP",
                                            "horizontal": "LEFT",
                                        },
                                        "fills": [
                                            {
                                                "type": "SOLID",
                                                "blendMode": "NORMAL",
                                                "color": {
                                                    "r": 0.11372549086809158,
                                                    "g": 0.12941177189350128,
                                                    "b": 0.16078431904315948,
                                                    "a": 1,
                                                },
                                            }
                                        ],
                                        "strokes": [],
                                        "strokeWeight": 1,
                                        "strokeAlign": "OUTSIDE",
                                        "effects": [],
                                        "layoutAlign": "STRETCH",
                                        "layoutGrow": 0,
                                        "styles": {
                                            "text": "S:511:2004,Purity UI Dashboard - Chakra UI Dashboard",
                                            "fills": "S:1:123,Purity UI Dashboard - Chakra UI Dashboard",
                                        },
                                        "boundVariables": {
                                            "characters": {
                                                "id": "V:987/321",
                                                "type": "VARIABLE_ALIAS",
                                            }
                                        },
                                        "characters": "Dashboard Overview",
                                        "style": {
                                            "fontFamily": "Helvetica Neue",
                                            "fontPostScriptName": "HelveticaNeue-Bold",
                                            "fontWeight": 700,
                                            "fontSize": 32,
                                            "textAlignHorizontal": "LEFT",
                                            "textAlignVertical": "TOP",
                                            "letterSpacing": 0,
                                            "lineHeightPx": 38.400001525878906,
                                            "lineHeightPercent": 100,
                                            "lineHeightPercentFontSize": 120,
                                            "lineHeightUnit": "INTRINSIC_%",
                                            "textCase": "ORIGINAL",
                                            "textDecoration": "NONE",
                                            "textAutoResize": "WIDTH_AND_HEIGHT",
                                            "textTruncation": "ENDING",
                                            "maxLines": None,
                                        },
                                        "characterStyleOverrides": [],
                                        "styleOverrideTable": {},
                                        "lineTypes": ["NONE"],
                                        "lineIndentations": [0],
                                    },
                                    {
                                        "id": "I1517:9056;130:5121",
                                        "name": "Button Primary",
                                        "type": "INSTANCE",
                                        "visible": True,
                                        "locked": False,
                                        "opacity": 1,
                                        "absoluteBoundingBox": {
                                            "x": -1980,
                                            "y": -490,
                                            "width": 150,
                                            "height": 48,
                                        },
                                        "constraints": {
                                            "vertical": "TOP",
                                            "horizontal": "LEFT",
                                        },
                                        "componentId": "C:130:5000,Purity UI Dashboard - Chakra UI Dashboard",
                                        "componentProperties": {
                                            "State": {
                                                "value": "Default",
                                                "type": "VARIANT",
                                            },
                                            "Size": {
                                                "value": "Large",
                                                "type": "VARIANT",
                                            },
                                        },
                                        "overrides": [],
                                        "isExposedInstance": False,
                                        "exposedInstances": [],
                                        "strokesIncludedInLayout": True,
                                        "layoutAlign": "INHERIT",
                                        "layoutGrow": 0,
                                    },
                                    {
                                        "id": "VEC:101:2",
                                        "name": "Decorative Line",
                                        "type": "VECTOR",
                                        "visible": True,
                                        "rotation": 0,
                                        "absoluteBoundingBox": {
                                            "x": -1980,
                                            "y": -420,
                                            "width": 1400,
                                            "height": 1,
                                        },
                                        "blendMode": "PASS_THROUGH",
                                        "fills": [],
                                        "strokes": [
                                            {
                                                "type": "SOLID",
                                                "color": {
                                                    "r": 0.8,
                                                    "g": 0.8,
                                                    "b": 0.8,
                                                    "a": 1,
                                                },
                                            }
                                        ],
                                        "strokeWeight": 1,
                                        "strokeAlign": "CENTER",
                                        "strokeCap": "NONE",
                                        "strokeJoin": "MITER",
                                        "strokeDashes": [],
                                        "strokeMiterAngle": 4,
                                        "strokeGeometry": [
                                            {
                                                "path": "M0 0.5L1400 0.5",
                                                "windingRule": "NONZERO",
                                            }
                                        ],
                                    },
                                    {
                                        "id": "SEC:202:5",
                                        "name": "User Stats Section",
                                        "type": "SECTION",
                                        "visible": True,
                                        "children": [],
                                        "fills": [
                                            {
                                                "type": "SOLID",
                                                "color": {
                                                    "r": 0.9,
                                                    "g": 0.9,
                                                    "b": 0.95,
                                                    "a": 0.3,
                                                },
                                            }
                                        ],
                                        "absoluteBoundingBox": {
                                            "x": -1980,
                                            "y": -400,
                                            "width": 1400,
                                            "height": 200,
                                        },
                                        "devStatus": {"type": "READY_FOR_DEV"},
                                    },
                                ],
                            },
                            {
                                "id": "CONN:INTRO:001",
                                "name": "Title to Button Flow",
                                "type": "CONNECTOR",
                                "visible": True,
                                "opacity": 1,
                                "absoluteBoundingBox": {"x": -1980, "y": -525, "width": 0, "height": 35}, # Example: Vertical line
                                "fills": [],
                                "strokes": [{"type": "SOLID", "visible": True, "color": {"r": 0.1, "g": 0.4, "b": 0.8, "a": 1}}],
                                "strokeWeight": 2,
                                "strokeCap": "ARROW_EQUILATERAL", # Arrow at the end
                                "strokeGeometry": [{"path": "M0 0L0 35", "windingRule": "NONZERO"}],
                                "connectorStart": {
                                    "endpointNodeId": "1516:9023", # Page Title
                                    "magnet": "BOTTOM_CENTER"
                                },
                                "connectorEnd": {
                                    "endpointNodeId": "I1517:9056;130:5121", # Button Primary
                                    "magnet": "TOP_CENTER"
                                },
                                "children": []
                            }
                        ],
                    }
                ],
            },
            "globalVars": {
                "styles": {
                    "S:151:37,Purity UI Dashboard - Chakra UI Dashboard": {
                        "key": "s1s2s3s4s5s6s7s8s9s0s1s2s3s4s5s6s7s8s9s0",
                        "name": "Background/Primary-Canvas",
                        "styleType": "FILL",
                        "remote": False,
                        "description": "Primary background color for canvases",
                        "root": {
                            "type": "SOLID",
                            "color": {"r": 1, "g": 1, "b": 1, "a": 1},
                        },
                    },
                    "S:511:2004,Purity UI Dashboard - Chakra UI Dashboard": {
                        "key": "t1t2t3t4t5t6t7t8t9t0t1t2t3t4t5t6t7t8t9t0",
                        "name": "Typography/H1-Bold",
                        "styleType": "TEXT",
                        "remote": False,
                        "description": "Main heading style",
                        "root": {
                            "fontFamily": "Helvetica Neue",
                            "fontPostScriptName": "HelveticaNeue-Bold",
                            "fontWeight": 700,
                            "fontSize": 32,
                            "textAlignHorizontal": "LEFT",
                            "textAlignVertical": "TOP",
                            "letterSpacing": 0,
                            "lineHeightPx": 38.4,
                            "lineHeightPercent": 100,
                            "lineHeightUnit": "INTRINSIC_%",
                            "textCase": "ORIGINAL",
                        },
                    },
                    "S:1:123,Purity UI Dashboard - Chakra UI Dashboard": {
                        "key": "f1f2f3f4f5f6f7f8f9f0f1f2f3f4f5f6f7f8f9f0",
                        "name": "Text/Color-Primary-Dark",
                        "styleType": "FILL",
                        "remote": True,
                        "description": "Primary dark text color",
                        "root": {
                            "type": "SOLID",
                            "color": {
                                "r": 0.11372549086809158,
                                "g": 0.12941177189350128,
                                "b": 0.16078431904315948,
                                "a": 1,
                            },
                        },
                    },
                },
                "variables": {
                    "V:987/654": {
                        "id": "V:987/654",
                        "name": "Background/Surface-Default",
                        "key": "bgSurfaceDefaultKey",
                        "variableCollectionId": "VC:987",
                        "resolvedType": "COLOR",
                        "valuesByMode": {
                            "M:987/1": {"r": 1, "g": 1, "b": 1, "a": 1},
                            "M:987/2": {"r": 0.1, "g": 0.1, "b": 0.1, "a": 1},
                        },
                        "remote": False,
                        "description": "Default surface background color",
                        "hiddenFromPublishing": False,
                        "scopes": ["ALL_SCOPES", "fills"],
                        "codeSyntax": {
                            "WEB": "var(--color-bg-surface-default)",
                            "ANDROID": "R.color.bg_surface_default",
                            "IOS": "Color.bgSurfaceDefault",
                        },
                    },
                    "V:987/321": {
                        "id": "V:987/321",
                        "name": "Content/PageTitle-Text",
                        "key": "contentPageTitleTextKey",
                        "variableCollectionId": "VC:987",
                        "resolvedType": "STRING",
                        "valuesByMode": {"M:987/1": "Dashboard Overview"},
                        "remote": False,
                        "description": "Text for page titles",
                        "hiddenFromPublishing": False,
                        "scopes": ["TEXT_CONTENT"],
                        "codeSyntax": {},
                    },
                    "V:987/111": {
                        "id": "V:987/111",
                        "name": "Layout/PageWidth-Desktop",
                        "key": "layoutPageWidthDesktopKey",
                        "variableCollectionId": "VC:987",
                        "resolvedType": "FLOAT",
                        "valuesByMode": {"M:987/1": 1440},
                        "remote": False,
                        "description": "Standard page width for desktop",
                        "hiddenFromPublishing": False,
                        "scopes": ["WIDTH_HEIGHT"],
                        "codeSyntax": {},
                    },
                    "V:987/222": {
                        "id": "V:987/222",
                        "name": "Layout/PageHeight-Desktop",
                        "key": "layoutPageHeightDesktopKey",
                        "variableCollectionId": "VC:987",
                        "resolvedType": "FLOAT",
                        "valuesByMode": {"M:987/1": 1024},
                        "remote": False,
                        "description": "Standard page height for desktop",
                        "hiddenFromPublishing": False,
                        "scopes": ["WIDTH_HEIGHT"],
                        "codeSyntax": {},
                    },
                },
                "variableCollections": {
                    "VC:987": {
                        "id": "VC:987",
                        "name": "Brand Tokens",
                        "key": "brandTokensKey",
                        "modes": [
                            {"modeId": "M:987/1", "name": "Light Mode"},
                            {"modeId": "M:987/2", "name": "Dark Mode"},
                        ],
                        "defaultModeId": "M:987/1",
                        "remote": False,
                        "hiddenFromPublishing": False,
                        "variableIds": [
                            "V:987/654",
                            "V:987/321",
                            "V:987/111",
                            "V:987/222",
                        ],
                    }
                },
            },
            "components": { 
                "C:130:5000,Purity UI Dashboard - Chakra UI Dashboard": {
                    "key": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0",
                    "name": "Button/Primary",
                    "description": "Main call-to-action button",
                    "remote": False,
                    "documentationLinks": [],
                    "componentSetId": "CS:130:4999,Purity UI Dashboard - Chakra UI Dashboard",
                }
            },
            "componentSets": { 
                "CS:130:4999,Purity UI Dashboard - Chakra UI Dashboard": {
                    "key": "z9y8x7w6v5u4t3s2r1q0p9o8n7m6l5k4j3i2h1g0",
                    "name": "Button",
                    "description": "Button component with variants for state and size.",
                    "documentationLinks": [],
                }
            },
        },
        {
            "fileKey": "1SOAWRcMJaBDuKp0rQi9dE",
            "name": "Vision UI Dashboard React - MUI Dashboard (Free Version)",
            "lastModified": "2025-02-18T09:15:00Z",
            "thumbnailUrl": "https://example.com/thumbnails/123.png",
            "version": "9876543210",
            "role": "editor",
            "editorType": "figma",
            "linkAccess": "edit",
            "schemaVersion": 0,
            "projectId": "project_bravo_application",
            "annotation_categories": [
                {
                    "id": "cat_visual_bug_vision",
                    "name": "Visual Bug",
                    "color": {"r": 1.0, "g": 0.2, "b": 0.2, "a": 1}
                },
                {
                    "id": "cat_accessibility_vision",
                    "name": "Accessibility Note",
                    "color": {"r": 0.5, "g": 0.2, "b": 0.8, "a": 1}
                }
            ],
            "default_connector_id": "VEC:VISION:CONNECTOR_STYLE_GUIDE",
            "document": {
                "id": "0:0", # Document ID can be the same "0:0" for different files as it's local to the file
                "name": "Document",
                "type": "DOCUMENT",
                "scrollBehavior": "SCROLLS",
                "children": [
                    {
                        "id": "1601:6435",
                        "name": "👋 Introduction Page",
                        "type": "CANVAS",
                        "scrollBehavior": "SCROLLS",
                        "backgroundColor": {
                            "r": 0.0784313753247261,
                            "g": 0.09019608050584793,
                            "b": 0.1411764770746231,
                            "a": 1,
                        },
                        "prototypeStartNodeID": None,
                        "flowStartingPoints": [],
                        "prototypeDevice": {
                            "type": "PRESET",
                            "rotation": "NONE",
                            "size": {"width": 1920, "height": 1080},
                            "presetIdentifier": "DESKTOP_1920x1080",
                        },
                        "exportSettings": [],
                        "children": [
                            {
                                "id": "1601:6440",
                                "name": "Useful Links - Vision UI React",
                                "type": "FRAME",
                                "visible": True,
                                "locked": True,
                                "opacity": 1,
                                "rotation": 0,
                                "blendMode": "PASS_THROUGH",
                                "isMask": False,
                                "isFixed": False,
                                "absoluteBoundingBox": {
                                    "x": 50,
                                    "y": 50,
                                    "width": 1280,
                                    "height": 720,
                                },
                                "absoluteRenderBounds": {
                                    "x": 50,
                                    "y": 50,
                                    "width": 1280,
                                    "height": 720,
                                },
                                "constraints": {
                                    "vertical": "TOP",
                                    "horizontal": "LEFT",
                                },
                                "fills": [
                                    {
                                        "type": "SOLID",
                                        "visible": True,
                                        "opacity": 1,
                                        "blendMode": "NORMAL",
                                        "color": {
                                            "r": 0.10588235408067703,
                                            "g": 0.12156862765550613,
                                            "b": 0.1882352977991104,
                                            "a": 1,
                                        },
                                    }
                                ],
                                "strokes": [],
                                "strokeWeight": 1,
                                "strokeAlign": "INSIDE",
                                "cornerRadius": 15,
                                "topLeftRadius": 15,
                                "topRightRadius": 15,
                                "bottomRightRadius": 0, 
                                "bottomLeftRadius": 0,  
                                "effects": [
                                    {
                                        "type": "DROP_SHADOW",
                                        "visible": True,
                                        "radius": 20,
                                        "color": {"r": 0, "g": 0, "b": 0, "a": 0.1},
                                        "blendMode": "NORMAL",
                                        "offset": {"x": 0, "y": 10},
                                        "spread": 0,
                                        "showShadowBehindNode": False,
                                    }
                                ],
                                "layoutAlign": "INHERIT",
                                "layoutGrow": 0,
                                "exportSettings": [],
                                "prototypeInteractions": [],
                                "boundVariables": {},
                                "clipsContent": True,
                                "layoutMode": "VERTICAL",
                                "layoutWrap": "NO_WRAP",
                                "primaryAxisSizingMode": "AUTO",
                                "counterAxisSizingMode": "AUTO",
                                "primaryAxisAlignItems": "CENTER",
                                "counterAxisAlignItems": "CENTER",
                                "paddingLeft": 40,
                                "paddingRight": 40,
                                "paddingTop": 30,
                                "paddingBottom": 30,
                                "itemSpacing": 24,
                                "children": [
                                    {
                                        "id": "1601:6590",
                                        "name": "braden-collum-CBcS51cGoSw-unsplash 1",
                                        "type": "RECTANGLE",
                                        "visible": True,
                                        "locked": False,
                                        "opacity": 1,
                                        "rotation": 0.05235987755982988,
                                        "blendMode": "PASS_THROUGH",
                                        "isMask": False,
                                        "absoluteBoundingBox": {
                                            "x": 100,
                                            "y": 100,
                                            "width": 300,
                                            "height": 200,
                                        },
                                        "absoluteRenderBounds": {
                                            "x": 98,
                                            "y": 99,
                                            "width": 304,
                                            "height": 202,
                                        },
                                        "constraints": {
                                            "vertical": "TOP",
                                            "horizontal": "LEFT",
                                        },
                                        "fills": [
                                            {
                                                "type": "IMAGE",
                                                "visible": True,
                                                "opacity": 1,
                                                "blendMode": "NORMAL",
                                                "scaleMode": "FILL",
                                                "imageRef": "a6990ea68074fc32804032a8c8fa22fe4c8b4b3b",
                                                "imageTransform": [
                                                    [1, 0, 0],
                                                    [0, 1, 0],
                                                ],
                                                "scalingFactor": 0.5,
                                                "filters": {
                                                    "exposure": 0,
                                                    "contrast": 0.1,
                                                    "saturation": -0.2,
                                                    "temperature": 0,
                                                    "tint": 0,
                                                    "highlights": 0,
                                                    "shadows": 0,
                                                },
                                            }
                                        ],
                                        "strokes": [
                                            {
                                                "type": "SOLID",
                                                "visible": True,
                                                "color": {
                                                    "r": 1,
                                                    "g": 1,
                                                    "b": 1,
                                                    "a": 0.5,
                                                },
                                            }
                                        ],
                                        "strokeWeight": 2,
                                        "strokeAlign": "OUTSIDE",
                                        "cornerRadius": 10, 
                                        "topLeftRadius": 10,
                                        "topRightRadius": 5,
                                        "bottomRightRadius": 10,
                                        "bottomLeftRadius": 5,
                                        "effects": [],
                                    },
                                    {
                                        "id": "1602:7001",
                                        "name": "Welcome Message",
                                        "type": "TEXT",
                                        "annotations": [
                                             {
                                                "annotationId": "anno_welcome_access_002",
                                                "labelMarkdown": "Check color contrast for WCAG AA compliance.",
                                                "categoryId": "cat_accessibility_vision",
                                                "properties": [
                                                    {"type": "standard", "value": "WCAG 2.1 AA"},
                                                    {"type": "author", "value": "access@example.com"}
                                                ]
                                            }
                                        ],
                                        "visible": True,
                                        "opacity": 1,
                                        "blendMode": "PASS_THROUGH",
                                        "absoluteBoundingBox": {
                                            "x": 100,
                                            "y": 320,
                                            "width": 400,
                                            "height": 50,
                                        },
                                        "constraints": {
                                            "vertical": "TOP",
                                            "horizontal": "LEFT",
                                        },
                                        "fills": [
                                            {
                                                "type": "SOLID",
                                                "color": {
                                                    "r": 1,
                                                    "g": 1,
                                                    "b": 1,
                                                    "a": 1,
                                                },
                                            }
                                        ],
                                        "strokes": [],
                                        "strokeWeight": 1,
                                        "strokeAlign": "OUTSIDE",
                                        "styles": {"text": "VUI_S:Text:Heading1"},
                                        "characters": "Welcome to Vision UI",
                                        "style": {
                                            "fontFamily": "Roboto",
                                            "fontPostScriptName": "Roboto-Bold",
                                            "fontWeight": 700,
                                            "fontSize": 24,
                                            "textAlignHorizontal": "LEFT",
                                            "textAlignVertical": "CENTER",
                                            "letterSpacing": 0.5,
                                            "lineHeightPx": 36,
                                            "lineHeightUnit": "PIXELS",
                                            "textCase": "UPPERCASE",
                                            "textDecoration": "NONE",
                                            "textAutoResize": "HEIGHT",
                                        },
                                    },
                                    {
                                        "id": "I1605:120;15:2801",
                                        "name": "Login Button",
                                        "type": "INSTANCE",
                                        "visible": True,
                                        "absoluteBoundingBox": {
                                            "x": 100,
                                            "y": 390,
                                            "width": 180,
                                            "height": 44,
                                        },
                                        "constraints": {
                                            "vertical": "TOP",
                                            "horizontal": "LEFT",
                                        },
                                        "componentId": "VUI_C:LoginButton",
                                        "componentProperties": {
                                            "variant": {
                                                "value": "Gradient",
                                                "type": "VARIANT",
                                            },
                                            "iconVisible": {
                                                "value": True,
                                                "type": "BOOLEAN",
                                            },
                                        },
                                        "overrides": [
                                            {
                                                "id": "15:2802",
                                                "overriddenFields": ["characters"],
                                            }
                                        ],
                                        "boundVariables": {
                                            "visible": {
                                                "id": "VUI_VAR:showLoginButton",
                                                "type": "VARIABLE_ALIAS",
                                            }
                                        },
                                    },
                                ],
                            }
                        ],
                    }
                ],
            },
            "globalVars": { 
                 "styles": {
                    "VUI_S:Text:Heading1": {
                        "key": "keyForVUI_TextStyleHeading1",
                        "name": "Text Styles/H1 - Bold White",
                        "styleType": "TEXT",
                        "remote": False,
                        "description": "Main heading style for dark backgrounds",
                        "root": {
                            "fontFamily": "Roboto",
                            "fontPostScriptName": "Roboto-Bold",
                            "fontWeight": 700,
                            "fontSize": 24,
                            "textAlignHorizontal": "LEFT",
                            "textAlignVertical": "CENTER",
                            "letterSpacing": 0.5,
                            "lineHeightPx": 36,
                            "lineHeightUnit": "PIXELS",
                            "textCase": "UPPERCASE",
                            "textDecoration": "NONE",
                            "textAutoResize": "HEIGHT",
                        },
                    },
                    "VUI_S:Fill:PrimaryGradient": {
                        "key": "keyForVUI_FillPrimaryGradient",
                        "name": "Fills/Primary Gradient",
                        "styleType": "FILL",
                        "remote": False,
                        "description": "Primary brand gradient",
                        "root": {
                            "type": "GRADIENT_LINEAR",
                            "visible": True,
                            "opacity": 1,
                            "blendMode": "NORMAL",
                            "gradientStops": [
                                {
                                    "position": 0,
                                    "color": {
                                        "r": 0.047,
                                        "g": 0.482,
                                        "b": 0.988,
                                        "a": 1,
                                    },
                                },
                                {
                                    "position": 1,
                                    "color": {"r": 0.2, "g": 0.6, "b": 1, "a": 1},
                                },
                            ],
                            "gradientTransform": [[1, 0, 0], [0, 1, 0]],
                        },
                    },
                },
                "variables": {
                    "VUI_VAR:showLoginButton": {
                        "id": "VUI_VAR:showLoginButton",
                        "name": "Feature Flags/showLoginButton",
                        "key": "ffShowLoginButtonKey",
                        "variableCollectionId": "VUI_VC:FeatureFlags",
                        "resolvedType": "BOOLEAN",
                        "valuesByMode": {"ModeA": True, "ModeB": False},
                        "remote": False,
                        "description": "Controls visibility of the login button",
                        "hiddenFromPublishing": False,
                        "scopes": ["ALL_SCOPES"],
                        "codeSyntax": {},
                    },
                    "VUI_VAR:ThemePrimaryColor": {
                        "id": "VUI_VAR:ThemePrimaryColor",
                        "name": "Theme/Primary Color",
                        "key": "themePrimaryColorKey",
                        "variableCollectionId": "VUI_VC:ThemeColors",
                        "resolvedType": "COLOR",
                        "valuesByMode": {
                            "Default": {"r": 0.047, "g": 0.482, "b": 0.988, "a": 1}
                        },
                        "remote": False,
                        "description": "Main primary color for the theme",
                        "hiddenFromPublishing": False,
                        "scopes": ["fills", "strokes"],
                        "codeSyntax": {
                            "WEB": "--vui-color-primary",
                            "IOS": "VUIColor.primary",
                        },
                    },
                },
                "variableCollections": {
                    "VUI_VC:FeatureFlags": {
                        "id": "VUI_VC:FeatureFlags",
                        "name": "Feature Flags",
                        "key": "featureFlagsCollectionKey",
                        "modes": [
                            {"modeId": "ModeA", "name": "Default"},
                            {"modeId": "ModeB", "name": "Experimental"},
                        ],
                        "defaultModeId": "ModeA",
                        "remote": False,
                        "hiddenFromPublishing": True,
                        "variableIds": ["VUI_VAR:showLoginButton"],
                    },
                    "VUI_VC:ThemeColors": {
                        "id": "VUI_VC:ThemeColors",
                        "name": "Theme Colors",
                        "key": "themeColorsCollectionKey",
                        "modes": [{"modeId": "Default", "name": "Default"}],
                        "defaultModeId": "Default",
                        "remote": False,
                        "hiddenFromPublishing": False,
                        "variableIds": ["VUI_VAR:ThemePrimaryColor"],
                    },
                },
            },
            "components": { 
                "VUI_C:LoginButton": {
                    "key": "keyForVUI_LoginButtonComponent",
                    "name": "Shared/Button/Login",
                    "description": "Standard login button for Vision UI",
                    "remote": False,
                    "documentationLinks": [],
                    "componentSetId": "VUI_CS:Buttons",
                }
            },
            "componentSets": { 
                "VUI_CS:Buttons": {
                    "key": "keyForVUI_ButtonComponentSet",
                    "name": "Shared/Button",
                    "description": "All button variants for Vision UI",
                    "documentationLinks": [],
                }
            },
        },
    ],
    "current_selection_node_ids": ["1516:9023", "I1517:9056;130:5121"], 

    "projects": [
        {
            "projectId": "project_alpha_design_system",
            "name": "Project Alpha (Design System)"
        },
        {
            "projectId": "project_bravo_application",
            "name": "Project Bravo (Main Application)"
        }
    ],
    "current_file_key": "1SORSDcBJjENuSp0rTi9dQ",
    "current_figma_channel": "general_updates_channel", 
}

def save_state(filepath: str) -> None:
    """Save the current state to a JSON file.

    Args:
        filepath: Path to save the state file.
    """
    with open(filepath, "w") as f:
        json.dump(DB, f)


def load_state(filepath: str) -> None:
    """Load state from a JSON file.

    Args:
        filepath: Path to load the state file from.
    """
    global DB
    with open(filepath, "r") as f:
        new_data = json.load(f)
        DB.clear()
        DB.update(new_data)

