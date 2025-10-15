[
    {
        "type": "fieldset",
        "title": "Downtime Management Form"
    },

    {
        "key": "node",
        "readOnly": true
    },
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
    {"key": "specificResource", "titleMap": {}},
    {
        "type": "text",
        "title": "Reason for Downtime",
        "key": "reason",
        "placeholder": "Enter reason for downtime"
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