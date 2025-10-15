[
    {
        "type": "fieldset",
        "title": "Downtime Management Form"
    },
    {
        "type": "fieldset",
        "title": "Identify the Downtime Target",
        "items": [
            "node",
            {
                "key": "site",
                "title": "Affected Site",
                "type": "select",
                "titleMap": []
            },
            {
                "key": "resourceType",
                "titleMap": {
                    "sites": "Site",
                    "compute": "Compute Resource",
                    "storages": "Storage Resource",
                    "storage-areas": "Stoage Areas",
                    "other": "Other Resource"
                }
            },
            "specificResource"
        ]
    },
    {
        "title": "Select Downtime Start and End",
        "key": "date_range",
        "type": "text",
        "placeholder": "Select date range",
        "htmlClass": "datepicker"
    },
    {
        "type": "submit",
        "title": "Schedule Downtime"
    }
]