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
            "site",
            "resourceType",
            "specificResource"
        ]
    },
    {
        "type": "fieldset",
        "title": "Define Downtime Period",
        "items": [
            {
                "type": "section",
                "htmlClass": "date-time-group",
                "items": ["startTime", "endTime"]
            },
            {
                "key": "timeType",
                "type": "radios"
            },
            {
                "key": "reason",
                "type": "textarea"
            }
        ]
    },
    {
        "type": "submit",
        "title": "Schedule Downtime"
    }
]