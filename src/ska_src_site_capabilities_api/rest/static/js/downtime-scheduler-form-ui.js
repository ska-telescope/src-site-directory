[
    {
        "type": "fieldset",
        "title": "Downtime Management Form"
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
            "storage_areas": "Storage Areas",
            "compute_local_services": "Compute Local Services",
            "compute_global_services": "Compute Global Services"
        }
    },
    {
        "key": "uniqueResourceName",
        "titleMap": {}
    },
    {
        "key": "type",
        "title": "Type of Downtime" 
    },
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