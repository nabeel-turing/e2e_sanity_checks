
¶
/2. Requirements/Requirements for JIRA.xlsx.jsonapplication/jsonð{
  "id": "sheet_b9a1547be305a49ecadc24f4a0a750b7",
  "driveId": "",
  "name": "Requirements for JIRA.xlsx",
  "mimeType": "application/vnd.google-apps.spreadsheet",
  "createdTime": "2025-07-21T17:50:14Z",
  "modifiedTime": "2025-05-01T00:41:28Z",
  "parents": [],
  "owners": [
    "john.doe@gmail.com"
  ],
  "size": 0,
  "trashed": false,
  "starred": false,
  "properties": {
    "title": "Requirements for JIRA",
    "locale": "en_US",
    "timeZone": "UTC"
  },
  "sheets": [
    {
      "properties": {
        "sheetId": 1,
        "title": "Sheet1",
        "index": 0,
        "sheetType": "GRID",
        "gridProperties": {
          "rowCount": 1000,
          "columnCount": 26
        }
      }
    }
  ],
  "data": {
    "Sheet1!A1:E12": [
      [
        "Enhancement",
        "Add link in the App",
        "",
        "",
        "Notes"
      ],
      [
        "BA Assigned",
        "Gina Success, Alex Windsor",
        "",
        "",
        "- Need to check privacy requirements"
      ],
      [
        "Summary Description",
        "Add a link to the app that will take the CM's directly to the Claimants summary screen",
        "",
        "",
        ""
      ],
      [
        "Priority",
        "High",
        "",
        "",
        ""
      ],
      [
        "SME List",
        "Dodi Jump\nLillian King\nTitus Tart\nBen Walleye \nJeff Vault\n",
        "",
        "",
        ""
      ],
      [
        "Links",
        "www.theApp.com",
        "",
        "",
        ""
      ],
      [
        "Jira Link",
        "www.jira.com/SME4672",
        "",
        "",
        ""
      ],
      [
        "ID",
        "Scope",
        "Title",
        "Description",
        "Acceptance Criteria"
      ],
      [
        "1.1",
        "In Scope",
        "Add button to open the Claimant page in app",
        "This link is to be added to simplify workflow for the CMS by allowing them to navigate staring to the app",
        "The link should be labelled and intuitively labeled\nThe link should be in the Predictive scores section\nThe link should be labelled - View Claim in APP"
      ],
      [
        "1.2",
        "In Scope",
        "Clicking the link opens the App in a new Internet Browser Window",
        "Clicking the link will open the app in a separate browser based on the claim ID they are in.",
        "When the link is clicked\n\n- App opens in separate browser Window\n- Daisy displays the target screen \n- Where the Dynamic claim id is the passed claim id value"
      ],
      [
        "1.3",
        "In Scope",
        "Add acceptance criteria for link",
        "Button should only be enabled if the claim is in accepted status and approved date is >9 days",
        "If the claim is in Accepted Status, approved to date is =>0 calendar days, but there is no claim score yet available, or if the claim is accepted and the date is <9 days\n- Cm will receive a message advising them link does work, there is just no score at this time\nIf claim is accepted and => calendar days\n- Cms will click on link and be taken to the App link for that claim ID\nClaim status and date changes can be found by clicking the status button on the claims list page"
      ],
      [
        "1.4",
        "In Scope",
        "Link Language",
        "French claim should lead to French app",
        "The link for French App is different than English App. Both can be accessed from each other's home page (ie language toggle)."
      ]
    ]
  },
  "permissions": [
    {
      "id": "permission_sheet_b9a1547be305a49ecadc24f4a0a750b7",
      "role": "owner",
      "type": "user",
      "emailAddress": "john.doe@gmail.com"
    }
  ]
}
öe
$3. Testing/PRD/PRD Testing.xlsx.jsonapplication/json»e{
  "id": "sheet_5dc4996473daa0997024e8e442b02546",
  "driveId": "",
  "name": "PRD Testing.xlsx",
  "mimeType": "application/vnd.google-apps.spreadsheet",
  "createdTime": "2025-07-21T17:50:16Z",
  "modifiedTime": "2025-05-01T01:32:15Z",
  "parents": [],
  "owners": [
    "john.doe@gmail.com"
  ],
  "size": 0,
  "trashed": false,
  "starred": false,
  "properties": {
    "title": "PRD Testing",
    "locale": "en_US",
    "timeZone": "UTC"
  },
  "sheets": [
    {
      "properties": {
        "sheetId": 1,
        "title": "Scenarios",
        "index": 0,
        "sheetType": "GRID",
        "gridProperties": {
          "rowCount": 1000,
          "columnCount": 26
        }
      }
    },
    {
      "properties": {
        "sheetId": 2,
        "title": "UAT",
        "index": 1,
        "sheetType": "GRID",
        "gridProperties": {
          "rowCount": 1000,
          "columnCount": 26
        }
      }
    },
    {
      "properties": {
        "sheetId": 3,
        "title": "Date Calculator",
        "index": 2,
        "sheetType": "GRID",
        "gridProperties": {
          "rowCount": 1000,
          "columnCount": 26
        }
      }
    }
  ],
  "data": {
    "Scenarios!A1:C15": [
      [
        "Different claim scenario's to test whether or not the button is visible",
        "",
        ""
      ],
      [
        "Claim type",
        "Claim Status",
        "PID"
      ],
      [
        "STD",
        "Declined",
        "282935674.0"
      ],
      [
        "STD",
        "Terminated",
        "500721498.0"
      ],
      [
        "STD",
        "Pending",
        "626017724.0"
      ],
      [
        "STD",
        "Accepted",
        "238125167.0"
      ],
      [
        "BLIFE",
        "Accepted",
        "833017472.0"
      ],
      [
        "BLIFE",
        "Terminated",
        "968264911.0"
      ],
      [
        "STD & LTD",
        "STD Accepted and LTD pending",
        "260672113.0"
      ],
      [
        "LTD",
        "Pending",
        "596067929.0"
      ],
      [
        "LTD",
        "Terminated",
        "80011303.0"
      ],
      [
        "LTD & BLIFE",
        "LTD Terminated, BLIFE Accepted",
        "755588333.0"
      ],
      [
        "LTD",
        "Accepted < 9 days",
        "819450935.0"
      ],
      [
        "LTD",
        "Accepted > 9 days",
        "774214831.0"
      ],
      [
        "LTD",
        "Accepted, and then 9 days later check",
        "509740824.0"
      ]
    ],
    "UAT!A1:H20": [
      [
        "Test Pre conditions",
        "",
        "",
        "",
        "",
        "",
        "",
        "Assigned Tester"
      ],
      [
        "Once the testing dates are known, a PID with LTD needs to be changed from pending to accepted. You will create a new claim ID in 3.5. Enter the date into the date Calculator to know when to test for 3.7\nThere will be 2 days of testing\nSecurity class is set to Protected\nAccess to prd.TheAPP.com",
        "",
        "",
        "",
        "",
        "",
        "",
        "Dodi Jump"
      ],
      [
        "Ref #",
        "Test Set",
        "Test Condition",
        "Test Inputs/Preconditions",
        "Expected Results",
        "Status",
        "Date of the test",
        ""
      ],
      [
        "1.1",
        "Test to see if the button is available on STD claims",
        "Open a declined STD Clam",
        "Open TCD- Claims Management\nIn Claim ID, Enter \"282935674\"\nPress Search\nChoose STD Claim\nClick Assessment\nIf a message appears asking if you would like to create a new assessment, Choose No\nClick on Management & Intervention Tab",
        "When you go to the management and intervention tab, there is a disabled button in the predictive modeling scores",
        "",
        "",
        ""
      ],
      [
        "1.2",
        "",
        "Print the STD Claim in the TCD",
        "In the TCD, Click File\nChoose Save Assessment to online cabinet\nChoose Author type CM, and leave Doc Description\nPress OK\nLogin to APP UAT\nClick on All documents, and open your PAMP\nScroll to the Management and Intervention page. Ensure the button is not printed or visible",
        "When you press okay, the upload status bar will appear on your screen\nWhen it is finished uploading, it will disappear\nWhen you review the TCD, there is no App Button ",
        "",
        "",
        ""
      ],
      [
        "1.3",
        "",
        "Open a terminated STD Claim",
        "Open TCD- Claims Management\nIn Claim ID, Enter \"500721498\"\nPress Search\nChoose STD Claim\nClick Assessment\nIf a message appears asking if you would like to create a new assessment, Choose No\nClick on Management & Intervention Tab",
        "When you go to the management and intervention tab, there is a disabled button in the predictive modeling scores",
        "",
        "",
        ""
      ],
      [
        "1.4",
        "",
        "Open a Pending STD Claim",
        "Open TCD- Claims Management\nIn Claim ID, Enter \"626017724\"\nPress Search\nChoose STD Claim\nClick Assessment\nIf a message appears asking if you would like to create a new assessment, Choose No\nClick on Management & Intervention Tab",
        "When you go to the management and intervention tab, there is a disabled button in the predictive modeling scores",
        "",
        "",
        ""
      ],
      [
        "1.5",
        "",
        "Open an Accepted STD Claim",
        "Open TCD- Claims Management\nIn Claim ID, Enter \"238125167\"\nPress Search\nChoose STD Claim\nClick Assessment\nIf a message appears asking if you would like to create a new assessment, Choose No\nClick on Management & Intervention Tab",
        "When you go to the management and intervention tab, there is a enabled button in the predictive modeling scores. The link is blue and clickable",
        "",
        "",
        ""
      ],
      [
        "2.1",
        "Test to see if the button is visible on BLIFE claims",
        "Open an Accepted BLIFE claim",
        "Open TCD- Claims Management\nIn Claim ID, Enter \"833017472\"\nPress Search\nChoose LIFE Claim\nClick Assessment\nIf a message appears asking if you would like to create a new assessment, Choose No\nClick on Management & Intervention Tab",
        "When you go to the Management and Intervention tab, there is no button in the Predictive Modelling Scores",
        "",
        "",
        ""
      ],
      [
        "2.2",
        "",
        "Print the BLIFE Claim in the TCD",
        "In the TCD, Click File\nChoose Save Assessment to online cabinet\nChoose Author type CM, and leave Doc Description\nPress OK\nLogin to app UAT\nClick on All documents, and open your PAMP\nScroll to the Management and Intervention page. Ensure the button is not printed or visible",
        "When you press okay, the upload status bar will appear on your screen\nWhen it is finished uploading, it will disappear\nWhen you review the TCD, there is no App Button ",
        "",
        "",
        ""
      ],
      [
        "2.3",
        "",
        "Open a terminated BLIFE Claim",
        "Open TCD- Claims Management\nIn Claim ID, Enter \"968264911\"\nPress Search\nChoose LIFE Claim\nClick Assessment\nIf a message appears asking if you would like to create a new assessment, Choose No\nClick on Management & Intervention Tab",
        "When you go to the Management and Intervention tab, there is no button in the Predictive Modelling Scores",
        "",
        "",
        ""
      ],
      [
        "3.1",
        "Test to see if the button is available on LTD claims",
        "Open a claim where STD is accepted and LTD is Pending",
        "Open TCD- Claims Management\nIn Claim ID, Enter \"260672113\"\nPress Search\nChoose LTD Claim\nClick Assessment\nIf a message appears asking if you would like to create a new assessment, Choose No\nClick on Management & Intervention Tab",
        "When you go to the management and intervention tab, there is a enabled button in the predictive modeling scores. The link is blue and clickable",
        "",
        "",
        ""
      ],
      [
        "3.2",
        "",
        "Open a claim where the LTD is pending",
        "Open TCD- Claims Management\nIn Claim ID, Enter \"596067929\"\nPress Search\nChoose LTD Claim\nClick Assessment\nIf a message appears asking if you would like to create a new assessment, Choose No\nClick on Management & Intervention Tab",
        "When you go to the Management and Intervention tab, there is a button in the Predictive Modeling Scores, but the button is disabled. If you click the button, nothing happens.",
        "",
        "",
        ""
      ],
      [
        "3.3",
        "",
        "Open a claim where the LTD is terminated",
        "Open TCD- Claims Management\nIn Claim ID, Enter \"80011303\"\nPress Search\nChoose LTD Claim\nClick Assessment\nIf a message appears asking if you would like to create a new assessment, Choose No\nClick on Management & Intervention Tab",
        "When you go to the Management and Intervention tab, there is a button in the Predictive Modeling Scores, but the button is disabled. If you click the button, nothing happens.",
        "",
        "",
        ""
      ],
      [
        "3.4",
        "",
        "Open a claim where the LTD terminated, BLIFE accepted",
        "Open TCD- Claims Management\nIn Claim ID, Enter \"755588333\"\nPress Search\nChoose LTD Claim\nClick Assessment\nIf a message appears asking if you would like to create a new assessment, Choose No\nClick on Management & Intervention Tab",
        "When you go to the Management and Intervention tab, there is a button in the Predictive Modeling Scores, but the button is disabled. If you click the button, nothing happens.",
        "",
        "",
        ""
      ],
      [
        "3.6",
        "",
        "Open a claim where LTD status is accepted, and greater than 9 days",
        "Open TCD- Claims Management\nIn Claim ID, Enter \"755588333\"\nPress Search\nChoose LTD Claim\nClick Assessment\nIf a message appears asking if you would like to create a new assessment, Choose No\nClick on Management & Intervention Tab",
        "When you go to the management and intervention tab, there is a enabled button in the predictive modeling scores. The link is blue and clickable",
        "",
        "",
        ""
      ],
      [
        "3.8",
        "",
        "Print the LTD Claim in the TCD",
        "\"In the TCD, Click File\nChoose Save Assessment to online cabinet\nChoose Author type CM, and leave Doc Description\nPress OK\nLogin to app UAT\nClick on All documents, and open your PAMP\nScroll to the Management and Intervention page. Ensure the button is not printed or visible\"",
        "When you press okay, the upload status bar will appear on your screen\nWhen it is finished uploading, it will disappear\nWhen you review the TCD, there is no App Button ",
        "",
        "",
        ""
      ],
      [
        "4.1",
        "Test that when you have TCD in French, clicking on the French TCD app link launches the app in French",
        "Change your TCD to French",
        "Ensure that TCD is shut down before changing the language setting or the change will not take effect \n- From the Window desktop search bar, Search for Control Panel\n- Click on Control Panel\n- Double Click on Region\n- From the Format: English change to French (Canada) \n- Click on Apply\n- Click on OK\n- Start on the TCD application",
        "When you open TCD, you will see the loading messages and other labels switched to French",
        "",
        "",
        ""
      ],
      [
        "4.2",
        "",
        "Change your internet browser language to French",
        "In Google Chrome\nClick on the stacked ... on the right hand side of the page\nChoose settings\nChoose Languages\nIf you do not already have French(Canada)m press Add languages\nadd French (Canada)\nPress Add\nClick the  .. dots beside French (Canada)\nSelect Display Google Chrome in this language",
        "When you click on the button, the App is launched in French in your default web browser",
        "",
        "",
        ""
      ],
      [
        "4.3",
        "",
        "Open claim in TCD",
        "Open Claims Management\nIn Dossier No enter: 819450935\nPress Recherche\nSelect the ILD Claim\nProcess Evaluation\nGo to the Gestation / Intervention Tab\nClick on the button",
        "When you click on the button, Daisy is launched in French in your default web browser",
        "",
        "",
        ""
      ]
    ],
    "Date Calculator!A1:B2": [
      [
        "Today's Date",
        "2025-05-02T00:00:00"
      ],
      [
        "Date link becomes available",
        "2025-05-11T00:00:00"
      ]
    ]
  },
  "permissions": [
    {
      "id": "permission_sheet_5dc4996473daa0997024e8e442b02546",
      "role": "owner",
      "type": "user",
      "emailAddress": "john.doe@gmail.com"
    }
  ]
}
“i
$3. Testing/UAT/UAT Testing.xlsx.jsonapplication/jsonØh{
  "id": "sheet_cb1a6bdc17c4233ac58868fa1ec23cea",
  "driveId": "",
  "name": "UAT Testing.xlsx",
  "mimeType": "application/vnd.google-apps.spreadsheet",
  "createdTime": "2025-07-21T17:50:15Z",
  "modifiedTime": "2025-05-01T01:32:06Z",
  "parents": [],
  "owners": [
    "john.doe@gmail.com"
  ],
  "size": 0,
  "trashed": false,
  "starred": false,
  "properties": {
    "title": "UAT Testing",
    "locale": "en_US",
    "timeZone": "UTC"
  },
  "sheets": [
    {
      "properties": {
        "sheetId": 1,
        "title": "Scenarios",
        "index": 0,
        "sheetType": "GRID",
        "gridProperties": {
          "rowCount": 1000,
          "columnCount": 26
        }
      }
    },
    {
      "properties": {
        "sheetId": 2,
        "title": "UAT",
        "index": 1,
        "sheetType": "GRID",
        "gridProperties": {
          "rowCount": 1000,
          "columnCount": 26
        }
      }
    },
    {
      "properties": {
        "sheetId": 3,
        "title": "Date Calculator",
        "index": 2,
        "sheetType": "GRID",
        "gridProperties": {
          "rowCount": 1000,
          "columnCount": 26
        }
      }
    }
  ],
  "data": {
    "Scenarios!A1:C15": [
      [
        "Different claim scenario's to test whether or not the button is visible",
        "",
        ""
      ],
      [
        "Claim type",
        "Claim Status",
        "PID"
      ],
      [
        "STD",
        "Declined",
        "282935674.0"
      ],
      [
        "STD",
        "Terminated",
        "500721498.0"
      ],
      [
        "STD",
        "Pending",
        "626017724.0"
      ],
      [
        "STD",
        "Accepted",
        "238125167.0"
      ],
      [
        "BLIFE",
        "Accepted",
        "833017472.0"
      ],
      [
        "BLIFE",
        "Terminated",
        "968264911.0"
      ],
      [
        "STD & LTD",
        "STD Accepted and LTD pending",
        "260672113.0"
      ],
      [
        "LTD",
        "Pending",
        "596067929.0"
      ],
      [
        "LTD",
        "Terminated",
        "80011303.0"
      ],
      [
        "LTD & BLIFE",
        "LTD Terminated, BLIFE Accepted",
        "755588333.0"
      ],
      [
        "LTD",
        "Accepted < 9 days",
        "819450935.0"
      ],
      [
        "LTD",
        "Accepted > 9 days",
        "774214831.0"
      ],
      [
        "LTD",
        "Accepted, and then 9 days later check",
        "509740824.0"
      ]
    ],
    "UAT!A1:H20": [
      [
        "Test Pre conditions",
        "",
        "",
        "",
        "",
        "",
        "",
        "Assigned Tester"
      ],
      [
        "Once the testing dates are known, a PID with LTD needs to be changed from pending to accepted. You will create a new claim ID in 3.5. Enter the date into the date Calculator to know when to test for 3.7\nThere will be 2 days of testing\nSecurity class is set to Protected\nAccess to uat.TheAPP.com",
        "",
        "",
        "",
        "",
        "",
        "",
        "Gina Success"
      ],
      [
        "Ref #",
        "Test Set",
        "Test Condition",
        "Test Inputs/Preconditions",
        "Expected Results",
        "Status",
        "Date of the test",
        "2025-01-31T00:00:00"
      ],
      [
        "1.1",
        "Test to see if the button is available on STD claims",
        "Open a declined STD Clam",
        "Open TCD- Claims Management\nIn Claim ID, Enter \"282935674\"\nPress Search\nChoose STD Claim\nClick Assessment\nIf a message appears asking if you would like to create a new assessment, Choose No\nClick on Management & Intervention Tab",
        "When you go to the management and intervention tab, there is a disabled button in the predictive modeling scores",
        "Pass",
        "2025-01-31T00:00:00",
        ""
      ],
      [
        "1.2",
        "",
        "Print the STD Claim in the TCD",
        "In the TCD, Click File\nChoose Save Assessment to online cabinet\nChoose Author type CM, and leave Doc Description\nPress OK\nLogin to APP UAT\nClick on All documents, and open your PAMP\nScroll to the Management and Intervention page. Ensure the button is not printed or visible",
        "When you press okay, the upload status bar will appear on your screen\nWhen it is finished uploading, it will disappear\nWhen you review the TCD, there is no App Button ",
        "Pass",
        "2025-01-31T00:00:00",
        ""
      ],
      [
        "1.3",
        "",
        "Open a terminated STD Claim",
        "Open TCD- Claims Management\nIn Claim ID, Enter \"500721498\"\nPress Search\nChoose STD Claim\nClick Assessment\nIf a message appears asking if you would like to create a new assessment, Choose No\nClick on Management & Intervention Tab",
        "When you go to the management and intervention tab, there is a disabled button in the predictive modeling scores",
        "Pass",
        "2025-01-31T00:00:00",
        ""
      ],
      [
        "1.4",
        "",
        "Open a Pending STD Claim",
        "Open TCD- Claims Management\nIn Claim ID, Enter \"626017724\"\nPress Search\nChoose STD Claim\nClick Assessment\nIf a message appears asking if you would like to create a new assessment, Choose No\nClick on Management & Intervention Tab",
        "When you go to the management and intervention tab, there is a disabled button in the predictive modeling scores",
        "Pass",
        "2025-01-31T00:00:00",
        ""
      ],
      [
        "1.5",
        "",
        "Open an Accepted STD Claim",
        "Open TCD- Claims Management\nIn Claim ID, Enter \"238125167\"\nPress Search\nChoose STD Claim\nClick Assessment\nIf a message appears asking if you would like to create a new assessment, Choose No\nClick on Management & Intervention Tab",
        "When you go to the management and intervention tab, there is a enabled button in the predictive modeling scores. The link is blue and clickable",
        "Pass",
        "2025-01-31T00:00:00",
        ""
      ],
      [
        "2.1",
        "Test to see if the button is visible on BLIFE claims",
        "Open an Accepted BLIFE claim",
        "Open TCD- Claims Management\nIn Claim ID, Enter \"833017472\"\nPress Search\nChoose LIFE Claim\nClick Assessment\nIf a message appears asking if you would like to create a new assessment, Choose No\nClick on Management & Intervention Tab",
        "When you go to the Management and Intervention tab, there is no button in the Predictive Modelling Scores",
        "Pass",
        "2025-01-31T00:00:00",
        ""
      ],
      [
        "2.2",
        "",
        "Print the BLIFE Claim in the TCD",
        "In the TCD, Click File\nChoose Save Assessment to online cabinet\nChoose Author type CM, and leave Doc Description\nPress OK\nLogin to app UAT\nClick on All documents, and open your PAMP\nScroll to the Management and Intervention page. Ensure the button is not printed or visible",
        "When you press okay, the upload status bar will appear on your screen\nWhen it is finished uploading, it will disappear\nWhen you review the TCD, there is no App Button ",
        "Pass",
        "2025-01-31T00:00:00",
        ""
      ],
      [
        "2.3",
        "",
        "Open a terminated BLIFE Claim",
        "Open TCD- Claims Management\nIn Claim ID, Enter \"968264911\"\nPress Search\nChoose LIFE Claim\nClick Assessment\nIf a message appears asking if you would like to create a new assessment, Choose No\nClick on Management & Intervention Tab",
        "When you go to the Management and Intervention tab, there is no button in the Predictive Modelling Scores",
        "Pass",
        "2025-01-31T00:00:00",
        ""
      ],
      [
        "3.1",
        "Test to see if the button is available on LTD claims",
        "Open a claim where STD is accepted and LTD is Pending",
        "Open TCD- Claims Management\nIn Claim ID, Enter \"260672113\"\nPress Search\nChoose LTD Claim\nClick Assessment\nIf a message appears asking if you would like to create a new assessment, Choose No\nClick on Management & Intervention Tab",
        "When you go to the management and intervention tab, there is a enabled button in the predictive modeling scores. The link is blue and clickable",
        "Pass",
        "2025-01-31T00:00:00",
        ""
      ],
      [
        "3.2",
        "",
        "Open a claim where the LTD is pending",
        "Open TCD- Claims Management\nIn Claim ID, Enter \"596067929\"\nPress Search\nChoose LTD Claim\nClick Assessment\nIf a message appears asking if you would like to create a new assessment, Choose No\nClick on Management & Intervention Tab",
        "When you go to the Management and Intervention tab, there is a button in the Predictive Modeling Scores, but the button is disabled. If you click the button, nothing happens.",
        "Pass",
        "2025-01-31T00:00:00",
        ""
      ],
      [
        "3.3",
        "",
        "Open a claim where the LTD is terminated",
        "Open TCD- Claims Management\nIn Claim ID, Enter \"80011303\"\nPress Search\nChoose LTD Claim\nClick Assessment\nIf a message appears asking if you would like to create a new assessment, Choose No\nClick on Management & Intervention Tab",
        "When you go to the Management and Intervention tab, there is a button in the Predictive Modeling Scores, but the button is disabled. If you click the button, nothing happens.",
        "Pass",
        "2025-01-31T00:00:00",
        ""
      ],
      [
        "3.4",
        "",
        "Open a claim where the LTD terminated, BLIFE accepted",
        "Open TCD- Claims Management\nIn Claim ID, Enter \"755588333\"\nPress Search\nChoose LTD Claim\nClick Assessment\nIf a message appears asking if you would like to create a new assessment, Choose No\nClick on Management & Intervention Tab",
        "When you go to the Management and Intervention tab, there is a button in the Predictive Modeling Scores, but the button is disabled. If you click the button, nothing happens.",
        "Pass",
        "2025-01-31T00:00:00",
        ""
      ],
      [
        "3.6",
        "",
        "Open a claim where LTD status is accepted, and greater than 9 days",
        "Open TCD- Claims Management\nIn Claim ID, Enter \"755588333\"\nPress Search\nChoose LTD Claim\nClick Assessment\nIf a message appears asking if you would like to create a new assessment, Choose No\nClick on Management & Intervention Tab",
        "When you go to the management and intervention tab, there is a enabled button in the predictive modeling scores. The link is blue and clickable",
        "Pass",
        "2025-01-31T00:00:00",
        ""
      ],
      [
        "3.8",
        "",
        "Print the LTD Claim in the TCD",
        "\"In the TCD, Click File\nChoose Save Assessment to online cabinet\nChoose Author type CM, and leave Doc Description\nPress OK\nLogin to app UAT\nClick on All documents, and open your PAMP\nScroll to the Management and Intervention page. Ensure the button is not printed or visible\"",
        "When you press okay, the upload status bar will appear on your screen\nWhen it is finished uploading, it will disappear\nWhen you review the TCD, there is no App Button ",
        "Pass",
        "2025-01-31T00:00:00",
        ""
      ],
      [
        "4.1",
        "Test that when you have TCD in French, clicking on the French TCD app link launches the app in French",
        "Change your TCD to French",
        "Ensure that TCD is shut down before changing the language setting or the change will not take effect \n- From the Window desktop search bar, Search for Control Panel\n- Click on Control Panel\n- Double Click on Region\n- From the Format: English change to French (Canada) \n- Click on Apply\n- Click on OK\n- Start on the TCD application",
        "When you open TCD, you will see the loading messages and other labels switched to French",
        "Pass",
        "2025-01-31T00:00:00",
        ""
      ],
      [
        "4.2",
        "",
        "Change your internet browser language to French",
        "In Google Chrome\nClick on the stacked ... on the right hand side of the page\nChoose settings\nChoose Languages\nIf you do not already have French(Canada)m press Add languages\nadd French (Canada)\nPress Add\nClick the  .. dots beside French (Canada)\nSelect Display Google Chrome in this language",
        "When you click on the button, the App is launched in French in your default web browser",
        "Pass",
        "2025-01-31T00:00:00",
        ""
      ],
      [
        "4.3",
        "",
        "Open claim in TCD",
        "Open Claims Management\nIn Dossier No enter: 819450935\nPress Recherche\nSelect the ILD Claim\nProcess Evaluation\nGo to the Gestation / Intervention Tab\nClick on the button",
        "When you click on the button, Daisy is launched in French in your default web browser",
        "Pass",
        "2025-01-31T00:00:00",
        ""
      ]
    ],
    "Date Calculator!A1:B2": [
      [
        "Today's Date",
        "2025-05-02T00:00:00"
      ],
      [
        "Date link becomes available",
        "2025-05-11T00:00:00"
      ]
    ]
  },
  "permissions": [
    {
      "id": "permission_sheet_cb1a6bdc17c4233ac58868fa1ec23cea",
      "role": "owner",
      "type": "user",
      "emailAddress": "john.doe@gmail.com"
    }
  ]
}
„
;1. Documents/Change Management/Communication Plan.xlsx.jsonapplication/json²{
  "id": "sheet_44b14a9b5a86b2105c3deb8c3ecaa553",
  "driveId": "",
  "name": "Communication Plan.xlsx",
  "mimeType": "application/vnd.google-apps.spreadsheet",
  "createdTime": "2025-07-21T17:50:14Z",
  "modifiedTime": "2025-05-01T02:07:33Z",
  "parents": [],
  "owners": [
    "john.doe@gmail.com"
  ],
  "size": 0,
  "trashed": false,
  "starred": false,
  "properties": {
    "title": "Communication Plan",
    "locale": "en_US",
    "timeZone": "UTC"
  },
  "sheets": [
    {
      "properties": {
        "sheetId": 1,
        "title": "Sheet1",
        "index": 0,
        "sheetType": "GRID",
        "gridProperties": {
          "rowCount": 1000,
          "columnCount": 26
        }
      }
    }
  ],
  "data": {
    "Sheet1!B1:H7": [
      [
        "Communication Plan",
        "",
        "",
        "",
        "",
        "",
        ""
      ],
      [
        "Message",
        "When",
        "By Whom",
        "Delivery Method",
        "To Whom",
        "Content of Communication",
        "Frequency"
      ],
      [
        "Preview of the changes",
        "January 20th, 2025",
        "Lillian King",
        "Teams Meeting",
        "CM's in the pilot",
        "What to expect in the pilot\nDemonstrate the changes\nGather initial questions and feedback",
        "Once"
      ],
      [
        "Planned Go Live",
        "February 7th, 2025",
        "Dodi Jump",
        "Email",
        "Disability Offices\nManagers\nTech Support",
        "When will the pilot start\nWhen to expect the updates if the pilot goes well\nExplain what the changes are\nWho to contact if they encounter issues",
        "Once"
      ],
      [
        "Go or No Go email",
        "February 21th, 2025",
        "Dodi Jump",
        "Email",
        "Disability Offices\nManagers\nTech Support",
        "Let the field know if the change is going live\nIf yes, add reminder to restart computers overnight\nIf no, explain go live is not going forward ",
        "Once"
      ],
      [
        "Feedback Request",
        "March 21st, 2025",
        "Alex Windsor",
        "Teams Meeting\nEmail",
        "CM's in the pilot\nDisability Offices\nManagers\nTech Support",
        "Ask for feedback on the change\nLessons Learned",
        "Once"
      ],
      [
        "Project Updates",
        "December 15th, 2024",
        "Gina Success",
        "Teams Chat",
        "Managers\nTech Support",
        "Update on the project\nWhat was achieved in the last week\nWhat is still pending",
        "Weekly"
      ]
    ]
  },
  "permissions": [
    {
      "id": "permission_sheet_44b14a9b5a86b2105c3deb8c3ecaa553",
      "role": "owner",
      "type": "user",
      "emailAddress": "john.doe@gmail.com"
    }
  ]
}
”
61. Documents/Change Management/Training Plan.xlsx.jsonapplication/jsonÇ{
  "id": "sheet_2ab0815295303c596cd89ba3d5050be7",
  "driveId": "",
  "name": "Training Plan.xlsx",
  "mimeType": "application/vnd.google-apps.spreadsheet",
  "createdTime": "2025-07-21T17:50:14Z",
  "modifiedTime": "2025-05-01T02:03:29Z",
  "parents": [],
  "owners": [
    "john.doe@gmail.com"
  ],
  "size": 0,
  "trashed": false,
  "starred": false,
  "properties": {
    "title": "Training Plan",
    "locale": "en_US",
    "timeZone": "UTC"
  },
  "sheets": [
    {
      "properties": {
        "sheetId": 1,
        "title": "Sheet1",
        "index": 0,
        "sheetType": "GRID",
        "gridProperties": {
          "rowCount": 1000,
          "columnCount": 26
        }
      }
    }
  ],
  "data": {
    "Sheet1!B1:I5": [
      [
        "Training Plan",
        "",
        "",
        "",
        "",
        "",
        "",
        ""
      ],
      [
        "Training Topics",
        "Trainer",
        "Audience",
        "Date and Times",
        "Training Method",
        "Training Coordinator",
        "Costs",
        "Note"
      ],
      [
        "Sneak peak to Pilot Group\n- What do the cahnges look like\n- How will this impact voids\n- What will they have to do\n- What will they no longer have to do",
        "Alex Windsor",
        "Pilots CM's",
        "2025-01 17 10:30 AM",
        "Presentation through teams\nPower Point\nDocumentation",
        "Gina Success",
        "30 minutes of CM time x 26\n30 minutes of BA time ",
        "Feedback oppurtunity from CM's regarding what additional documentation might be needed, things not address, questions they still have, what else should be in the communication"
      ],
      [
        "Field Training",
        "Dodi Jump",
        "CM's in the pilot\nDisability Offices\nManagers\nTech Support",
        "February 21st, 2025",
        "Email",
        "Managers",
        "15 minutes of reading x 500",
        "Provide FAQ documentation created from pilot\nProvide training recording"
      ],
      [
        "Further clarification from FAQ",
        "Dodi Jump",
        "CM's in the pilot\nDisability Offices\nManagers\nTech Support",
        "2025-04-15T00:00:00",
        "Email",
        "Managers",
        "15 minutes of reading x 500",
        "Provider further FAQ's after the Go Live"
      ]
    ]
  },
  "permissions": [
    {
      "id": "permission_sheet_2ab0815295303c596cd89ba3d5050be7",
      "role": "owner",
      "type": "user",
      "emailAddress": "john.doe@gmail.com"
    }
  ]
}
³ð
(1. Documents/Mock Ups/Mock Ups.pptx.jsonapplication/jsonóï{
  "id": "pres_300bc8c1d6bd9fa76c4b749fccd6c8c2",
  "driveId": "",
  "name": "Mock Ups.pptx",
  "mimeType": "application/vnd.google-apps.presentation",
  "createdTime": "2025-07-21T17:50:14Z",
  "modifiedTime": "2025-05-01T01:41:23Z",
  "trashed": false,
  "starred": false,
  "parents": [],
  "owners": [
    "john.doe@gmail.com"
  ],
  "size": "42221",
  "permissions": [
    {
      "id": "permission_pres_300bc8c1d6bd9fa76c4b749fccd6c8c2",
      "role": "owner",
      "type": "user",
      "emailAddress": "john.doe@gmail.com"
    }
  ],
  "presentationId": "pres_300bc8c1d6bd9fa76c4b749fccd6c8c2",
  "title": "Mock Ups",
  "pageSize": {
    "width": {
      "magnitude": 9144000.0,
      "unit": "EMU"
    },
    "height": {
      "magnitude": 5143500.0,
      "unit": "EMU"
    }
  },
  "slides": [
    {
      "objectId": "metadata_slide",
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
      "slideProperties": {
        "masterObjectId": "master1",
        "layoutObjectId": "layout1"
      },
      "pageElements": [
        {
          "objectId": "metadata_element",
          "size": {
            "width": {
              "magnitude": 600,
              "unit": "PT"
            },
            "height": {
              "magnitude": 400,
              "unit": "PT"
            }
          },
          "transform": {
            "scaleX": 1.0,
            "scaleY": 1.0,
            "translateX": 50,
            "translateY": 50,
            "unit": "PT"
          },
          "shape": {
            "shapeType": "TEXT_BOX",
            "text": {
              "textElements": [
                {
                  "textRun": {
                    "content": "[Presentation title: PowerPoint Presentation]",
                    "style": {
                      "fontFamily": "Calibri",
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
      "revisionId": "rev_metadata"
    },
    {
      "objectId": "slide1_page1",
      "pageType": "SLIDE",
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
      "slideProperties": {
        "masterObjectId": "master1",
        "layoutObjectId": "layout1"
      },
      "pageElements": [
        {
          "objectId": "element1_slide1",
          "size": {
            "width": {
              "magnitude": 8520600.0,
              "unit": "PT"
            },
            "height": {
              "magnitude": 2052600.0,
              "unit": "PT"
            }
          },
          "transform": {
            "scaleX": 1.0,
            "scaleY": 1.0,
            "translateX": 311708.0,
            "translateY": 744575.0,
            "unit": "PT"
          },
          "shape": {
            "shapeType": "TEXT_BOX",
            "text": {
              "textElements": [
                {
                  "textRun": {
                    "content": "Mock Ups",
                    "style": {
                      "fontFamily": "Calibri",
                      "fontSize": {
                        "magnitude": 12,
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
      "objectId": "slide2_page2",
      "pageType": "SLIDE",
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
      "slideProperties": {
        "masterObjectId": "master1",
        "layoutObjectId": "layout1"
      },
      "pageElements": [
        {
          "objectId": "element1_slide2",
          "size": {
            "width": {
              "magnitude": 8520600.0,
              "unit": "PT"
            },
            "height": {
              "magnitude": 572700.0,
              "unit": "PT"
            }
          },
          "transform": {
            "scaleX": 1.0,
            "scaleY": 1.0,
            "translateX": 311700.0,
            "translateY": 445025.0,
            "unit": "PT"
          },
          "shape": {
            "shapeType": "TEXT_BOX",
            "text": {
              "textElements": [
                {
                  "textRun": {
                    "content": "Enabled",
                    "style": {
                      "fontFamily": "Calibri",
                      "fontSize": {
                        "magnitude": 12,
                        "unit": "PT"
                      }
                    }
                  }
                }
              ]
            }
          }
        },
        {
          "objectId": "element2_slide2",
          "size": {
            "width": {
              "magnitude": 8344800.0,
              "unit": "PT"
            },
            "height": {
              "magnitude": 2217900.0,
              "unit": "PT"
            }
          },
          "transform": {
            "scaleX": 1.0,
            "scaleY": 1.0,
            "translateX": 487500.0,
            "translateY": 1329125.0,
            "unit": "PT"
          },
          "shape": {
            "shapeType": "TEXT_BOX",
            "text": {
              "textElements": [
                {
                  "textRun": {
                    "content": "",
                    "style": {
                      "fontFamily": "Calibri",
                      "fontSize": {
                        "magnitude": 12,
                        "unit": "PT"
                      }
                    }
                  }
                }
              ]
            }
          }
        },
        {
          "objectId": "element3_slide2",
          "size": {
            "width": {
              "magnitude": 5371500.0,
              "unit": "PT"
            },
            "height": {
              "magnitude": 338100.0,
              "unit": "PT"
            }
          },
          "transform": {
            "scaleX": 1.0,
            "scaleY": 1.0,
            "translateX": 597725.0,
            "translateY": 1423500.0,
            "unit": "PT"
          },
          "shape": {
            "shapeType": "TEXT_BOX",
            "text": {
              "textElements": [
                {
                  "textRun": {
                    "content": "Predictive Modeling Scores",
                    "style": {
                      "fontFamily": "Calibri",
                      "fontSize": {
                        "magnitude": 12.0,
                        "unit": "PT"
                      }
                    }
                  }
                }
              ]
            }
          }
        },
        {
          "objectId": "element4_slide2",
          "size": {
            "width": {
              "magnitude": 2097000.0,
              "unit": "PT"
            },
            "height": {
              "magnitude": 338100.0,
              "unit": "PT"
            }
          },
          "transform": {
            "scaleX": 1.0,
            "scaleY": 1.0,
            "translateX": 597725.0,
            "translateY": 2167375.0,
            "unit": "PT"
          },
          "shape": {
            "shapeType": "TEXT_BOX",
            "text": {
              "textElements": [
                {
                  "textRun": {
                    "content": "STD Midpoint",
                    "style": {
                      "fontFamily": "Calibri",
                      "fontSize": {
                        "magnitude": 12.0,
                        "unit": "PT"
                      }
                    }
                  }
                }
              ]
            }
          }
        },
        {
          "objectId": "element5_slide2",
          "size": {
            "width": {
              "magnitude": 2097000.0,
              "unit": "PT"
            },
            "height": {
              "magnitude": 338100.0,
              "unit": "PT"
            }
          },
          "transform": {
            "scaleX": 1.0,
            "scaleY": 1.0,
            "translateX": 597725.0,
            "translateY": 2703525.0,
            "unit": "PT"
          },
          "shape": {
            "shapeType": "TEXT_BOX",
            "text": {
              "textElements": [
                {
                  "textRun": {
                    "content": "LTD @ 6 months",
                    "style": {
                      "fontFamily": "Calibri",
                      "fontSize": {
                        "magnitude": 12.0,
                        "unit": "PT"
                      }
                    }
                  }
                }
              ]
            }
          }
        },
        {
          "objectId": "element6_slide2",
          "size": {
            "width": {
              "magnitude": 2097000.0,
              "unit": "PT"
            },
            "height": {
              "magnitude": 338100.0,
              "unit": "PT"
            }
          },
          "transform": {
            "scaleX": 1.0,
            "scaleY": 1.0,
            "translateX": 3219650.0,
            "translateY": 2157450.0,
            "unit": "PT"
          },
          "shape": {
            "shapeType": "TEXT_BOX",
            "text": {
              "textElements": [
                {
                  "textRun": {
                    "content": "STD Maximum Date",
                    "style": {
                      "fontFamily": "Calibri",
                      "fontSize": {
                        "magnitude": 12.0,
                        "unit": "PT"
                      }
                    }
                  }
                }
              ]
            }
          }
        },
        {
          "objectId": "element7_slide2",
          "size": {
            "width": {
              "magnitude": 2097000.0,
              "unit": "PT"
            },
            "height": {
              "magnitude": 338100.0,
              "unit": "PT"
            }
          },
          "transform": {
            "scaleX": 1.0,
            "scaleY": 1.0,
            "translateX": 3219650.0,
            "translateY": 2703525.0,
            "unit": "PT"
          },
          "shape": {
            "shapeType": "TEXT_BOX",
            "text": {
              "textElements": [
                {
                  "textRun": {
                    "content": "LTD @ 24 Months",
                    "style": {
                      "fontFamily": "Calibri",
                      "fontSize": {
                        "magnitude": 12.0,
                        "unit": "PT"
                      }
                    }
                  }
                }
              ]
            }
          }
        },
        {
          "objectId": "element8_slide2",
          "size": {
            "width": {
              "magnitude": 2097000.0,
              "unit": "PT"
            },
            "height": {
              "magnitude": 338100.0,
              "unit": "PT"
            }
          },
          "transform": {
            "scaleX": 1.0,
            "scaleY": 1.0,
            "translateX": 5928075.0,
            "translateY": 2132350.0,
            "unit": "PT"
          },
          "shape": {
            "shapeType": "TEXT_BOX",
            "text": {
              "textElements": [
                {
                  "textRun": {
                    "content": "STD Variability Score",
                    "style": {
                      "fontFamily": "Calibri",
                      "fontSize": {
                        "magnitude": 12.0,
                        "unit": "PT"
                      }
                    }
                  }
                }
              ]
            }
          }
        },
        {
          "objectId": "element9_slide2",
          "size": {
            "width": {
              "magnitude": 1038300.0,
              "unit": "PT"
            },
            "height": {
              "magnitude": 298800.0,
              "unit": "PT"
            }
          },
          "transform": {
            "scaleX": 1.0,
            "scaleY": 1.0,
            "translateX": 1918975.0,
            "translateY": 2187025.0,
            "unit": "PT"
          },
          "shape": {
            "shapeType": "TEXT_BOX",
            "text": {
              "textElements": [
                {
                  "textRun": {
                    "content": "0.0",
                    "style": {
                      "fontFamily": "Calibri",
                      "fontSize": {
                        "magnitude": 12.0,
                        "unit": "PT"
                      }
                    }
                  }
                }
              ]
            }
          }
        },
        {
          "objectId": "element10_slide2",
          "size": {
            "width": {
              "magnitude": 1038300.0,
              "unit": "PT"
            },
            "height": {
              "magnitude": 298800.0,
              "unit": "PT"
            }
          },
          "transform": {
            "scaleX": 1.0,
            "scaleY": 1.0,
            "translateX": 1918975.0,
            "translateY": 2723175.0,
            "unit": "PT"
          },
          "shape": {
            "shapeType": "TEXT_BOX",
            "text": {
              "textElements": [
                {
                  "textRun": {
                    "content": "0.0",
                    "style": {
                      "fontFamily": "Calibri",
                      "fontSize": {
                        "magnitude": 12.0,
                        "unit": "PT"
                      }
                    }
                  }
                }
              ]
            }
          }
        },
        {
          "objectId": "element11_slide2",
          "size": {
            "width": {
              "magnitude": 1038300.0,
              "unit": "PT"
            },
            "height": {
              "magnitude": 298800.0,
              "unit": "PT"
            }
          },
          "transform": {
            "scaleX": 1.0,
            "scaleY": 1.0,
            "translateX": 4800400.0,
            "translateY": 2187025.0,
            "unit": "PT"
          },
          "shape": {
            "shapeType": "TEXT_BOX",
            "text": {
              "textElements": [
                {
                  "textRun": {
                    "content": "0.0",
                    "style": {
                      "fontFamily": "Calibri",
                      "fontSize": {
                        "magnitude": 12.0,
                        "unit": "PT"
                      }
                    }
                  }
                }
              ]
            }
          }
        },
        {
          "objectId": "element12_slide2",
          "size": {
            "width": {
              "magnitude": 1038300.0,
              "unit": "PT"
            },
            "height": {
              "magnitude": 298800.0,
              "unit": "PT"
            }
          },
          "transform": {
            "scaleX": 1.0,
            "scaleY": 1.0,
            "translateX": 4800400.0,
            "translateY": 2723175.0,
            "unit": "PT"
          },
          "shape": {
            "shapeType": "TEXT_BOX",
            "text": {
              "textElements": [
                {
                  "textRun": {
                    "content": "0.0",
                    "style": {
                      "fontFamily": "Calibri",
                      "fontSize": {
                        "magnitude": 12.0,
                        "unit": "PT"
                      }
                    }
                  }
                }
              ]
            }
          }
        },
        {
          "objectId": "element13_slide2",
          "size": {
            "width": {
              "magnitude": 1038300.0,
              "unit": "PT"
            },
            "height": {
              "magnitude": 298800.0,
              "unit": "PT"
            }
          },
          "transform": {
            "scaleX": 1.0,
            "scaleY": 1.0,
            "translateX": 7618925.0,
            "translateY": 2177100.0,
            "unit": "PT"
          },
          "shape": {
            "shapeType": "TEXT_BOX",
            "text": {
              "textElements": [
                {
                  "textRun": {
                    "content": "0.0",
                    "style": {
                      "fontFamily": "Calibri",
                      "fontSize": {
                        "magnitude": 12.0,
                        "unit": "PT"
                      }
                    }
                  }
                }
              ]
            }
          }
        },
        {
          "objectId": "element14_slide2",
          "size": {
            "width": {
              "magnitude": 2483400.0,
              "unit": "PT"
            },
            "height": {
              "magnitude": 401100.0,
              "unit": "PT"
            }
          },
          "transform": {
            "scaleX": 1.0,
            "scaleY": 1.0,
            "translateX": 6173775.0,
            "translateY": 2713325.0,
            "unit": "PT"
          },
          "shape": {
            "shapeType": "TEXT_BOX",
            "text": {
              "textElements": [
                {
                  "textRun": {
                    "content": "View Claim in App",
                    "style": {
                      "fontFamily": "Calibri",
                      "fontSize": {
                        "magnitude": 11.0,
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
      "revisionId": "rev_slide2"
    },
    {
      "objectId": "slide3_page3",
      "pageType": "SLIDE",
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
      "slideProperties": {
        "masterObjectId": "master1",
        "layoutObjectId": "layout1"
      },
      "pageElements": [
        {
          "objectId": "element1_slide3",
          "size": {
            "width": {
              "magnitude": 8520600.0,
              "unit": "PT"
            },
            "height": {
              "magnitude": 572700.0,
              "unit": "PT"
            }
          },
          "transform": {
            "scaleX": 1.0,
            "scaleY": 1.0,
            "translateX": 311700.0,
            "translateY": 445025.0,
            "unit": "PT"
          },
          "shape": {
            "shapeType": "TEXT_BOX",
            "text": {
              "textElements": [
                {
                  "textRun": {
                    "content": "Disabled",
                    "style": {
                      "fontFamily": "Calibri",
                      "fontSize": {
                        "magnitude": 12,
                        "unit": "PT"
                      }
                    }
                  }
                }
              ]
            }
          }
        },
        {
          "objectId": "element2_slide3",
          "size": {
            "width": {
              "magnitude": 8344800.0,
              "unit": "PT"
            },
            "height": {
              "magnitude": 2217900.0,
              "unit": "PT"
            }
          },
          "transform": {
            "scaleX": 1.0,
            "scaleY": 1.0,
            "translateX": 487500.0,
            "translateY": 1329125.0,
            "unit": "PT"
          },
          "shape": {
            "shapeType": "TEXT_BOX",
            "text": {
              "textElements": [
                {
                  "textRun": {
                    "content": "",
                    "style": {
                      "fontFamily": "Calibri",
                      "fontSize": {
                        "magnitude": 12,
                        "unit": "PT"
                      }
                    }
                  }
                }
              ]
            }
          }
        },
        {
          "objectId": "element3_slide3",
          "size": {
            "width": {
              "magnitude": 5371500.0,
              "unit": "PT"
            },
            "height": {
              "magnitude": 338100.0,
              "unit": "PT"
            }
          },
          "transform": {
            "scaleX": 1.0,
            "scaleY": 1.0,
            "translateX": 597725.0,
            "translateY": 1423500.0,
            "unit": "PT"
          },
          "shape": {
            "shapeType": "TEXT_BOX",
            "text": {
              "textElements": [
                {
                  "textRun": {
                    "content": "Predictive Modeling Scores",
                    "style": {
                      "fontFamily": "Calibri",
                      "fontSize": {
                        "magnitude": 12.0,
                        "unit": "PT"
                      }
                    }
                  }
                }
              ]
            }
          }
        },
        {
          "objectId": "element4_slide3",
          "size": {
            "width": {
              "magnitude": 2097000.0,
              "unit": "PT"
            },
            "height": {
              "magnitude": 338100.0,
              "unit": "PT"
            }
          },
          "transform": {
            "scaleX": 1.0,
            "scaleY": 1.0,
            "translateX": 597725.0,
            "translateY": 2167375.0,
            "unit": "PT"
          },
          "shape": {
            "shapeType": "TEXT_BOX",
            "text": {
              "textElements": [
                {
                  "textRun": {
                    "content": "STD Midpoint",
                    "style": {
                      "fontFamily": "Calibri",
                      "fontSize": {
                        "magnitude": 12.0,
                        "unit": "PT"
                      }
                    }
                  }
                }
              ]
            }
          }
        },
        {
          "objectId": "element5_slide3",
          "size": {
            "width": {
              "magnitude": 2097000.0,
              "unit": "PT"
            },
            "height": {
              "magnitude": 338100.0,
              "unit": "PT"
            }
          },
          "transform": {
            "scaleX": 1.0,
            "scaleY": 1.0,
            "translateX": 597725.0,
            "translateY": 2703525.0,
            "unit": "PT"
          },
          "shape": {
            "shapeType": "TEXT_BOX",
            "text": {
              "textElements": [
                {
                  "textRun": {
                    "content": "LTD @ 6 months",
                    "style": {
                      "fontFamily": "Calibri",
                      "fontSize": {
                        "magnitude": 12.0,
                        "unit": "PT"
                      }
                    }
                  }
                }
              ]
            }
          }
        },
        {
          "objectId": "element6_slide3",
          "size": {
            "width": {
              "magnitude": 2097000.0,
              "unit": "PT"
            },
            "height": {
              "magnitude": 338100.0,
              "unit": "PT"
            }
          },
          "transform": {
            "scaleX": 1.0,
            "scaleY": 1.0,
            "translateX": 3219650.0,
            "translateY": 2157450.0,
            "unit": "PT"
          },
          "shape": {
            "shapeType": "TEXT_BOX",
            "text": {
              "textElements": [
                {
                  "textRun": {
                    "content": "STD Maximum Date",
                    "style": {
                      "fontFamily": "Calibri",
                      "fontSize": {
                        "magnitude": 12.0,
                        "unit": "PT"
                      }
                    }
                  }
                }
              ]
            }
          }
        },
        {
          "objectId": "element7_slide3",
          "size": {
            "width": {
              "magnitude": 2097000.0,
              "unit": "PT"
            },
            "height": {
              "magnitude": 338100.0,
              "unit": "PT"
            }
          },
          "transform": {
            "scaleX": 1.0,
            "scaleY": 1.0,
            "translateX": 3219650.0,
            "translateY": 2703525.0,
            "unit": "PT"
          },
          "shape": {
            "shapeType": "TEXT_BOX",
            "text": {
              "textElements": [
                {
                  "textRun": {
                    "content": "LTD @ 24 Months",
                    "style": {
                      "fontFamily": "Calibri",
                      "fontSize": {
                        "magnitude": 12.0,
                        "unit": "PT"
                      }
                    }
                  }
                }
              ]
            }
          }
        },
        {
          "objectId": "element8_slide3",
          "size": {
            "width": {
              "magnitude": 2097000.0,
              "unit": "PT"
            },
            "height": {
              "magnitude": 338100.0,
              "unit": "PT"
            }
          },
          "transform": {
            "scaleX": 1.0,
            "scaleY": 1.0,
            "translateX": 5928075.0,
            "translateY": 2132350.0,
            "unit": "PT"
          },
          "shape": {
            "shapeType": "TEXT_BOX",
            "text": {
              "textElements": [
                {
                  "textRun": {
                    "content": "STD Variability Score",
                    "style": {
                      "fontFamily": "Calibri",
                      "fontSize": {
                        "magnitude": 12.0,
                        "unit": "PT"
                      }
                    }
                  }
                }
              ]
            }
          }
        },
        {
          "objectId": "element9_slide3",
          "size": {
            "width": {
              "magnitude": 1038300.0,
              "unit": "PT"
            },
            "height": {
              "magnitude": 298800.0,
              "unit": "PT"
            }
          },
          "transform": {
            "scaleX": 1.0,
            "scaleY": 1.0,
            "translateX": 1918975.0,
            "translateY": 2187025.0,
            "unit": "PT"
          },
          "shape": {
            "shapeType": "TEXT_BOX",
            "text": {
              "textElements": [
                {
                  "textRun": {
                    "content": "0.0",
                    "style": {
                      "fontFamily": "Calibri",
                      "fontSize": {
                        "magnitude": 12.0,
                        "unit": "PT"
                      }
                    }
                  }
                }
              ]
            }
          }
        },
        {
          "objectId": "element10_slide3",
          "size": {
            "width": {
              "magnitude": 1038300.0,
              "unit": "PT"
            },
            "height": {
              "magnitude": 298800.0,
              "unit": "PT"
            }
          },
          "transform": {
            "scaleX": 1.0,
            "scaleY": 1.0,
            "translateX": 1918975.0,
            "translateY": 2723175.0,
            "unit": "PT"
          },
          "shape": {
            "shapeType": "TEXT_BOX",
            "text": {
              "textElements": [
                {
                  "textRun": {
                    "content": "0.0",
                    "style": {
                      "fontFamily": "Calibri",
                      "fontSize": {
                        "magnitude": 12.0,
                        "unit": "PT"
                      }
                    }
                  }
                }
              ]
            }
          }
        },
        {
          "objectId": "element11_slide3",
          "size": {
            "width": {
              "magnitude": 1038300.0,
              "unit": "PT"
            },
            "height": {
              "magnitude": 298800.0,
              "unit": "PT"
            }
          },
          "transform": {
            "scaleX": 1.0,
            "scaleY": 1.0,
            "translateX": 4800400.0,
            "translateY": 2187025.0,
            "unit": "PT"
          },
          "shape": {
            "shapeType": "TEXT_BOX",
            "text": {
              "textElements": [
                {
                  "textRun": {
                    "content": "0.0",
                    "style": {
                      "fontFamily": "Calibri",
                      "fontSize": {
                        "magnitude": 12.0,
                        "unit": "PT"
                      }
                    }
                  }
                }
              ]
            }
          }
        },
        {
          "objectId": "element12_slide3",
          "size": {
            "width": {
              "magnitude": 1038300.0,
              "unit": "PT"
            },
            "height": {
              "magnitude": 298800.0,
              "unit": "PT"
            }
          },
          "transform": {
            "scaleX": 1.0,
            "scaleY": 1.0,
            "translateX": 4800400.0,
            "translateY": 2723175.0,
            "unit": "PT"
          },
          "shape": {
            "shapeType": "TEXT_BOX",
            "text": {
              "textElements": [
                {
                  "textRun": {
                    "content": "0.0",
                    "style": {
                      "fontFamily": "Calibri",
                      "fontSize": {
                        "magnitude": 12.0,
                        "unit": "PT"
                      }
                    }
                  }
                }
              ]
            }
          }
        },
        {
          "objectId": "element13_slide3",
          "size": {
            "width": {
              "magnitude": 1038300.0,
              "unit": "PT"
            },
            "height": {
              "magnitude": 298800.0,
              "unit": "PT"
            }
          },
          "transform": {
            "scaleX": 1.0,
            "scaleY": 1.0,
            "translateX": 7618925.0,
            "translateY": 2177100.0,
            "unit": "PT"
          },
          "shape": {
            "shapeType": "TEXT_BOX",
            "text": {
              "textElements": [
                {
                  "textRun": {
                    "content": "0.0",
                    "style": {
                      "fontFamily": "Calibri",
                      "fontSize": {
                        "magnitude": 12.0,
                        "unit": "PT"
                      }
                    }
                  }
                }
              ]
            }
          }
        },
        {
          "objectId": "element14_slide3",
          "size": {
            "width": {
              "magnitude": 2483400.0,
              "unit": "PT"
            },
            "height": {
              "magnitude": 401100.0,
              "unit": "PT"
            }
          },
          "transform": {
            "scaleX": 1.0,
            "scaleY": 1.0,
            "translateX": 6173775.0,
            "translateY": 2713325.0,
            "unit": "PT"
          },
          "shape": {
            "shapeType": "TEXT_BOX",
            "text": {
              "textElements": [
                {
                  "textRun": {
                    "content": "View Claim in App",
                    "style": {
                      "fontFamily": "Calibri",
                      "fontSize": {
                        "magnitude": 11.0,
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
      "revisionId": "rev_slide3"
    },
    {
      "objectId": "slide4_page4",
      "pageType": "SLIDE",
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
      "slideProperties": {
        "masterObjectId": "master1",
        "layoutObjectId": "layout1"
      },
      "pageElements": [
        {
          "objectId": "element1_slide4",
          "size": {
            "width": {
              "magnitude": 8520600.0,
              "unit": "PT"
            },
            "height": {
              "magnitude": 572700.0,
              "unit": "PT"
            }
          },
          "transform": {
            "scaleX": 1.0,
            "scaleY": 1.0,
            "translateX": 311700.0,
            "translateY": 445025.0,
            "unit": "PT"
          },
          "shape": {
            "shapeType": "TEXT_BOX",
            "text": {
              "textElements": [
                {
                  "textRun": {
                    "content": "Not Visible",
                    "style": {
                      "fontFamily": "Calibri",
                      "fontSize": {
                        "magnitude": 12,
                        "unit": "PT"
                      }
                    }
                  }
                }
              ]
            }
          }
        },
        {
          "objectId": "element2_slide4",
          "size": {
            "width": {
              "magnitude": 8344800.0,
              "unit": "PT"
            },
            "height": {
              "magnitude": 2217900.0,
              "unit": "PT"
            }
          },
          "transform": {
            "scaleX": 1.0,
            "scaleY": 1.0,
            "translateX": 487500.0,
            "translateY": 1329125.0,
            "unit": "PT"
          },
          "shape": {
            "shapeType": "TEXT_BOX",
            "text": {
              "textElements": [
                {
                  "textRun": {
                    "content": "",
                    "style": {
                      "fontFamily": "Calibri",
                      "fontSize": {
                        "magnitude": 12,
                        "unit": "PT"
                      }
                    }
                  }
                }
              ]
            }
          }
        },
        {
          "objectId": "element3_slide4",
          "size": {
            "width": {
              "magnitude": 5371500.0,
              "unit": "PT"
            },
            "height": {
              "magnitude": 338100.0,
              "unit": "PT"
            }
          },
          "transform": {
            "scaleX": 1.0,
            "scaleY": 1.0,
            "translateX": 597725.0,
            "translateY": 1423500.0,
            "unit": "PT"
          },
          "shape": {
            "shapeType": "TEXT_BOX",
            "text": {
              "textElements": [
                {
                  "textRun": {
                    "content": "Predictive Modeling Scores",
                    "style": {
                      "fontFamily": "Calibri",
                      "fontSize": {
                        "magnitude": 12.0,
                        "unit": "PT"
                      }
                    }
                  }
                }
              ]
            }
          }
        },
        {
          "objectId": "element4_slide4",
          "size": {
            "width": {
              "magnitude": 2097000.0,
              "unit": "PT"
            },
            "height": {
              "magnitude": 338100.0,
              "unit": "PT"
            }
          },
          "transform": {
            "scaleX": 1.0,
            "scaleY": 1.0,
            "translateX": 597725.0,
            "translateY": 2167375.0,
            "unit": "PT"
          },
          "shape": {
            "shapeType": "TEXT_BOX",
            "text": {
              "textElements": [
                {
                  "textRun": {
                    "content": "STD Midpoint",
                    "style": {
                      "fontFamily": "Calibri",
                      "fontSize": {
                        "magnitude": 12.0,
                        "unit": "PT"
                      }
                    }
                  }
                }
              ]
            }
          }
        },
        {
          "objectId": "element5_slide4",
          "size": {
            "width": {
              "magnitude": 2097000.0,
              "unit": "PT"
            },
            "height": {
              "magnitude": 338100.0,
              "unit": "PT"
            }
          },
          "transform": {
            "scaleX": 1.0,
            "scaleY": 1.0,
            "translateX": 597725.0,
            "translateY": 2703525.0,
            "unit": "PT"
          },
          "shape": {
            "shapeType": "TEXT_BOX",
            "text": {
              "textElements": [
                {
                  "textRun": {
                    "content": "LTD @ 6 months",
                    "style": {
                      "fontFamily": "Calibri",
                      "fontSize": {
                        "magnitude": 12.0,
                        "unit": "PT"
                      }
                    }
                  }
                }
              ]
            }
          }
        },
        {
          "objectId": "element6_slide4",
          "size": {
            "width": {
              "magnitude": 2097000.0,
              "unit": "PT"
            },
            "height": {
              "magnitude": 338100.0,
              "unit": "PT"
            }
          },
          "transform": {
            "scaleX": 1.0,
            "scaleY": 1.0,
            "translateX": 3219650.0,
            "translateY": 2157450.0,
            "unit": "PT"
          },
          "shape": {
            "shapeType": "TEXT_BOX",
            "text": {
              "textElements": [
                {
                  "textRun": {
                    "content": "STD Maximum Date",
                    "style": {
                      "fontFamily": "Calibri",
                      "fontSize": {
                        "magnitude": 12.0,
                        "unit": "PT"
                      }
                    }
                  }
                }
              ]
            }
          }
        },
        {
          "objectId": "element7_slide4",
          "size": {
            "width": {
              "magnitude": 2097000.0,
              "unit": "PT"
            },
            "height": {
              "magnitude": 338100.0,
              "unit": "PT"
            }
          },
          "transform": {
            "scaleX": 1.0,
            "scaleY": 1.0,
            "translateX": 3219650.0,
            "translateY": 2703525.0,
            "unit": "PT"
          },
          "shape": {
            "shapeType": "TEXT_BOX",
            "text": {
              "textElements": [
                {
                  "textRun": {
                    "content": "LTD @ 24 Months",
                    "style": {
                      "fontFamily": "Calibri",
                      "fontSize": {
                        "magnitude": 12.0,
                        "unit": "PT"
                      }
                    }
                  }
                }
              ]
            }
          }
        },
        {
          "objectId": "element8_slide4",
          "size": {
            "width": {
              "magnitude": 2097000.0,
              "unit": "PT"
            },
            "height": {
              "magnitude": 338100.0,
              "unit": "PT"
            }
          },
          "transform": {
            "scaleX": 1.0,
            "scaleY": 1.0,
            "translateX": 5928075.0,
            "translateY": 2132350.0,
            "unit": "PT"
          },
          "shape": {
            "shapeType": "TEXT_BOX",
            "text": {
              "textElements": [
                {
                  "textRun": {
                    "content": "STD Variability Score",
                    "style": {
                      "fontFamily": "Calibri",
                      "fontSize": {
                        "magnitude": 12.0,
                        "unit": "PT"
                      }
                    }
                  }
                }
              ]
            }
          }
        },
        {
          "objectId": "element9_slide4",
          "size": {
            "width": {
              "magnitude": 1038300.0,
              "unit": "PT"
            },
            "height": {
              "magnitude": 298800.0,
              "unit": "PT"
            }
          },
          "transform": {
            "scaleX": 1.0,
            "scaleY": 1.0,
            "translateX": 1918975.0,
            "translateY": 2187025.0,
            "unit": "PT"
          },
          "shape": {
            "shapeType": "TEXT_BOX",
            "text": {
              "textElements": [
                {
                  "textRun": {
                    "content": "0.0",
                    "style": {
                      "fontFamily": "Calibri",
                      "fontSize": {
                        "magnitude": 12.0,
                        "unit": "PT"
                      }
                    }
                  }
                }
              ]
            }
          }
        },
        {
          "objectId": "element10_slide4",
          "size": {
            "width": {
              "magnitude": 1038300.0,
              "unit": "PT"
            },
            "height": {
              "magnitude": 298800.0,
              "unit": "PT"
            }
          },
          "transform": {
            "scaleX": 1.0,
            "scaleY": 1.0,
            "translateX": 1918975.0,
            "translateY": 2723175.0,
            "unit": "PT"
          },
          "shape": {
            "shapeType": "TEXT_BOX",
            "text": {
              "textElements": [
                {
                  "textRun": {
                    "content": "0.0",
                    "style": {
                      "fontFamily": "Calibri",
                      "fontSize": {
                        "magnitude": 12.0,
                        "unit": "PT"
                      }
                    }
                  }
                }
              ]
            }
          }
        },
        {
          "objectId": "element11_slide4",
          "size": {
            "width": {
              "magnitude": 1038300.0,
              "unit": "PT"
            },
            "height": {
              "magnitude": 298800.0,
              "unit": "PT"
            }
          },
          "transform": {
            "scaleX": 1.0,
            "scaleY": 1.0,
            "translateX": 4800400.0,
            "translateY": 2187025.0,
            "unit": "PT"
          },
          "shape": {
            "shapeType": "TEXT_BOX",
            "text": {
              "textElements": [
                {
                  "textRun": {
                    "content": "0.0",
                    "style": {
                      "fontFamily": "Calibri",
                      "fontSize": {
                        "magnitude": 12.0,
                        "unit": "PT"
                      }
                    }
                  }
                }
              ]
            }
          }
        },
        {
          "objectId": "element12_slide4",
          "size": {
            "width": {
              "magnitude": 1038300.0,
              "unit": "PT"
            },
            "height": {
              "magnitude": 298800.0,
              "unit": "PT"
            }
          },
          "transform": {
            "scaleX": 1.0,
            "scaleY": 1.0,
            "translateX": 4800400.0,
            "translateY": 2723175.0,
            "unit": "PT"
          },
          "shape": {
            "shapeType": "TEXT_BOX",
            "text": {
              "textElements": [
                {
                  "textRun": {
                    "content": "0.0",
                    "style": {
                      "fontFamily": "Calibri",
                      "fontSize": {
                        "magnitude": 12.0,
                        "unit": "PT"
                      }
                    }
                  }
                }
              ]
            }
          }
        },
        {
          "objectId": "element13_slide4",
          "size": {
            "width": {
              "magnitude": 1038300.0,
              "unit": "PT"
            },
            "height": {
              "magnitude": 298800.0,
              "unit": "PT"
            }
          },
          "transform": {
            "scaleX": 1.0,
            "scaleY": 1.0,
            "translateX": 7618925.0,
            "translateY": 2177100.0,
            "unit": "PT"
          },
          "shape": {
            "shapeType": "TEXT_BOX",
            "text": {
              "textElements": [
                {
                  "textRun": {
                    "content": "0.0",
                    "style": {
                      "fontFamily": "Calibri",
                      "fontSize": {
                        "magnitude": 12.0,
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
      "revisionId": "rev_slide4"
    }
  ],
  "masters": [],
  "layouts": [],
  "notesMaster": null,
  "locale": "en-US",
  "revisionId": "rev_pres_300bc8c1d6bd9fa76c4b749fccd6c8c2"
}
®&
01. Documents/Meetings/Project Kick off.docx.jsonapplication/jsonç%{
  "id": "file_8de15e9919cea8d4b666d2bde8be0fa5",
  "driveId": "",
  "name": "Project Kick off.docx",
  "mimeType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "createdTime": "2025-07-21T17:50:16Z",
  "modifiedTime": "2025-05-01T00:19:02Z",
  "trashed": false,
  "starred": false,
  "parents": [],
  "owners": [
    "john.doe@gmail.com"
  ],
  "size": "8548",
  "permissions": [
    {
      "id": "permission_file_8de15e9919cea8d4b666d2bde8be0fa5",
      "role": "owner",
      "type": "user",
      "emailAddress": "john.doe@gmail.com"
    }
  ],
  "suggestionsViewMode": "DEFAULT",
  "includeTabsContent": false,
  "tabs": [],
  "content": [
    {
      "elementId": "p1",
      "text": "New Link"
    },
    {
      "elementId": "p2",
      "text": "Attending: Gina Success, Alex Windsor, Dodi Jump, Lillian King, Titus Tart, Ben Walleye Jeff Vault, Karen Sturgeon"
    },
    {
      "elementId": "p4",
      "text": "Ask: Add a link to the App that will bring the user directly to the claimants summary page"
    },
    {
      "elementId": "p5",
      "text": "Priority: High"
    },
    {
      "elementId": "p6",
      "text": "Benefits:"
    },
    {
      "elementId": "p7",
      "text": "Time Savings"
    },
    {
      "elementId": "p8",
      "text": "Greater Utilization"
    },
    {
      "elementId": "p9",
      "text": "Requirements"
    },
    {
      "elementId": "p10",
      "text": "Will set later meeting"
    },
    {
      "elementId": "p11",
      "text": "Questions"
    },
    {
      "elementId": "p12",
      "text": "How often are people using the app?"
    },
    {
      "elementId": "p13",
      "text": "App is effective when it is used as early in the claim as possible"
    },
    {
      "elementId": "p14",
      "text": "Claim has to be complete and in the system for at least 9 days before the app can give it a score"
    },
    {
      "elementId": "p15",
      "text": "Can we measure the benefits?"
    },
    {
      "elementId": "p16",
      "text": "Can we track how often people are currently using the app?"
    },
    {
      "elementId": "p17",
      "text": "Can we track if there is an increase?"
    },
    {
      "elementId": "p19",
      "text": "Notes:"
    },
    {
      "elementId": "p20",
      "text": "Link wonâ€™t work until the claim has been accepted"
    },
    {
      "elementId": "p21",
      "text": "Link will need to be disabled in Pend Status"
    },
    {
      "elementId": "p22",
      "text": "Will the link be enabled 14 days after acceptance?"
    },
    {
      "elementId": "p23",
      "text": "All accepted claims from week prior and run then through app"
    },
    {
      "elementId": "p24",
      "text": "Come up with a useful error message if they try to access the claim before there is any information available"
    },
    {
      "elementId": "p25",
      "text": "What changes need to be made in the app?"
    },
    {
      "elementId": "p26",
      "text": "Changes already made in prior update"
    },
    {
      "elementId": "p27",
      "text": "The consensus is CMâ€™s are not using the app because of all the extra steps it is taking to get the information"
    },
    {
      "elementId": "p28",
      "text": "Training Department will need at least 1 month notice before go live to update training  material"
    },
    {
      "elementId": "p29",
      "text": "The app is accessed when?"
    },
    {
      "elementId": "p30",
      "text": "Depends on complexity of the claim and the med info provided on file"
    },
    {
      "elementId": "p31",
      "text": "If the tx is not RTW focused, or there gaps in accessing tx, if med info is passive/not appropriate and limited, if EE is not receiving or participating in reasonable and customary tx, and/or if all avenues has been explored and claimant remains limited, for scenarios such as above to review app to identity, what other interventions could be provided?"
    },
    {
      "elementId": "p32",
      "text": "CM feedback: Donâ€™t have a timeline, most of the time don't use app during initial assessment unless there is a gap with med info etc. Review app once developed own mgmt plan to confirm if anything else is identified or suggested."
    },
    {
      "elementId": "p33",
      "text": "Takeaways:"
    },
    {
      "elementId": "p34",
      "text": "Gina and Alex to set up separate requirement meeting"
    },
    {
      "elementId": "p35",
      "text": "Dodi and Alex to identify documentation to update"
    }
  ],
  "revisions": [
    {
      "id": "rev-1",
      "mimeType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      "modifiedTime": "2025-05-01T00:19:02Z",
      "keepForever": false,
      "originalFilename": "Project Kick off.docx",
      "size": "8548"
    }
  ]
}
ó
31. Documents/Meetings/Requirement meeting.docx.jsonapplication/json©{
  "id": "file_209887a00912e797808e6bf67c0982ed",
  "driveId": "",
  "name": "Requirement meeting.docx",
  "mimeType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "createdTime": "2025-07-21T17:50:14Z",
  "modifiedTime": "2025-05-01T01:54:11Z",
  "trashed": false,
  "starred": false,
  "parents": [],
  "owners": [
    "john.doe@gmail.com"
  ],
  "size": "7657",
  "permissions": [
    {
      "id": "permission_file_209887a00912e797808e6bf67c0982ed",
      "role": "owner",
      "type": "user",
      "emailAddress": "john.doe@gmail.com"
    }
  ],
  "suggestionsViewMode": "DEFAULT",
  "includeTabsContent": false,
  "tabs": [],
  "content": [
    {
      "elementId": "p1",
      "text": "New Link- Requirement Gathering"
    },
    {
      "elementId": "p2",
      "text": "Attending: Gina Success, Alex Windsor, Dodi Jump, Lillian King, Titus Tart, Ben Walleye Jeff Vault,"
    },
    {
      "elementId": "p3",
      "text": "Requirements"
    },
    {
      "elementId": "p4",
      "text": "Add button to open the Claimant page in app"
    },
    {
      "elementId": "p5",
      "text": "This link is to be added to simplify workflow for the CMS by allowing them to navigate staring to the app"
    },
    {
      "elementId": "p6",
      "text": "The link should be visible and intuitively labelled"
    },
    {
      "elementId": "p7",
      "text": "Verbiage: View claim in App"
    },
    {
      "elementId": "p8",
      "text": "Located: Predictive Scores Sections"
    },
    {
      "elementId": "p9",
      "text": "Clicking the link opens the App in a new Internet Browser Window"
    },
    {
      "elementId": "p10",
      "text": "Clicking the link will open the app in a separate browser based on the claim ID they are in."
    },
    {
      "elementId": "p11",
      "text": "When the link is clicked, the app will open in a new window"
    },
    {
      "elementId": "p12",
      "text": "The app displays the target screen - Claim Details"
    },
    {
      "elementId": "p13",
      "text": "Add acceptance criteria for link"
    },
    {
      "elementId": "p14",
      "text": "Button should only be enabled if the claim is in accepted status and approved date is >9 days"
    },
    {
      "elementId": "p15",
      "text": "If <9 days button should be disabled"
    },
    {
      "elementId": "p16",
      "text": "Any other status link should be disabled"
    },
    {
      "elementId": "p17",
      "text": "Link Language"
    },
    {
      "elementId": "p18",
      "text": "French claim should lead to French app"
    },
    {
      "elementId": "p19",
      "text": "The link for French is different from English. Both can be accessed from the others home page (ie language toggle)"
    },
    {
      "elementId": "p20",
      "text": "Takeaways"
    },
    {
      "elementId": "p22",
      "text": "Dodi and Alex to identify documentation to update"
    }
  ],
  "revisions": [
    {
      "id": "rev-1",
      "mimeType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      "modifiedTime": "2025-05-01T01:54:11Z",
      "keepForever": false,
      "originalFilename": "Requirement meeting.docx",
      "size": "7657"
    }
  ]
}