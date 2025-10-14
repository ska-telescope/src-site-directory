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
                "titleMap": [
                ]
            },
            "resourceType",
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