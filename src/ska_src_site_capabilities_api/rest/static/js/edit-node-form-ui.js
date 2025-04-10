[
    {
      "key": "name",
      "placeholder": "Unique node name",
      "readOnly": true
    },
    {
      "key": "description",
      "placeholder": "Node description"
    },
    {
      "key": "comments",
      "placeholder": "Comments for this version",
      "type": "wysihtml5"
    },
    {
      "title": "Sites",
      "type": "tabarray",
      "items": {
        "type": "section",
        "legend": "{{value}} ({{idx-1}})",
        "items": [
            {
              "key": "sites[].id",
              "readOnly": true
            },
            {
              "key": "sites[].name",
              "placeholder": "Unique site name",
              "valueInLegend": true
            },
            {
              "key": "sites[].description",
              "placeholder": "Site description"
            },
            {
              "key": "sites[].country",
              "type": "select",
              "title": "Country",
              "titleMap": {
                "AF": "Afghanistan",
                "AX": "Aland Islands",
                "AL": "Albania",
                "DZ": "Algeria",
                "AS": "American Samoa",
                "AD": "Andorra",
                "AO": "Angola",
                "AI": "Anguilla",
                "AQ": "Antarctica",
                "AG": "Antigua And Barbuda",
                "AR": "Argentina",
                "AM": "Armenia",
                "AW": "Aruba",
                "AU": "Australia",
                "AT": "Austria",
                "AZ": "Azerbaijan",
                "BS": "Bahamas",
                "BH": "Bahrain",
                "BD": "Bangladesh",
                "BB": "Barbados",
                "BY": "Belarus",
                "BE": "Belgium",
                "BZ": "Belize",
                "BJ": "Benin",
                "BM": "Bermuda",
                "BT": "Bhutan",
                "BO": "Bolivia",
                "BA": "Bosnia And Herzegovina",
                "BW": "Botswana",
                "BV": "Bouvet Island",
                "BR": "Brazil",
                "IO": "British Indian Ocean Territory",
                "BN": "Brunei Darussalam",
                "BG": "Bulgaria",
                "BF": "Burkina Faso",
                "BI": "Burundi",
                "KH": "Cambodia",
                "CM": "Cameroon",
                "CA": "Canada",
                "CV": "Cape Verde",
                "KY": "Cayman Islands",
                "CF": "Central African Republic",
                "TD": "Chad",
                "CL": "Chile",
                "CN": "China",
                "CX": "Christmas Island",
                "CC": "Cocos (Keeling) Islands",
                "CO": "Colombia",
                "KM": "Comoros",
                "CG": "Congo",
                "CD": "Congo, Democratic Republic",
                "CK": "Cook Islands",
                "CR": "Costa Rica",
                "CI": "Cote D\"Ivoire",
                "HR": "Croatia",
                "CU": "Cuba",
                "CY": "Cyprus",
                "CZ": "Czech Republic",
                "DK": "Denmark",
                "DJ": "Djibouti",
                "DM": "Dominica",
                "DO": "Dominican Republic",
                "EC": "Ecuador",
                "EG": "Egypt",
                "SV": "El Salvador",
                "GQ": "Equatorial Guinea",
                "ER": "Eritrea",
                "EE": "Estonia",
                "ET": "Ethiopia",
                "FK": "Falkland Islands (Malvinas)",
                "FO": "Faroe Islands",
                "FJ": "Fiji",
                "FI": "Finland",
                "FR": "France",
                "GF": "French Guiana",
                "PF": "French Polynesia",
                "TF": "French Southern Territories",
                "GA": "Gabon",
                "GM": "Gambia",
                "GE": "Georgia",
                "DE": "Germany",
                "GH": "Ghana",
                "GI": "Gibraltar",
                "GR": "Greece",
                "GL": "Greenland",
                "GD": "Grenada",
                "GP": "Guadeloupe",
                "GU": "Guam",
                "GT": "Guatemala",
                "GG": "Guernsey",
                "GN": "Guinea",
                "GW": "Guinea-Bissau",
                "GY": "Guyana",
                "HT": "Haiti",
                "HM": "Heard Island & Mcdonald Islands",
                "VA": "Holy See (Vatican City State)",
                "HN": "Honduras",
                "HK": "Hong Kong",
                "HU": "Hungary",
                "IS": "Iceland",
                "IN": "India",
                "ID": "Indonesia",
                "IR": "Iran, Islamic Republic Of",
                "IQ": "Iraq",
                "IE": "Ireland",
                "IM": "Isle Of Man",
                "IL": "Israel",
                "IT": "Italy",
                "JM": "Jamaica",
                "JP": "Japan",
                "JE": "Jersey",
                "JO": "Jordan",
                "KZ": "Kazakhstan",
                "KE": "Kenya",
                "KI": "Kiribati",
                "KR": "Korea",
                "KP": "North Korea",
                "KW": "Kuwait",
                "KG": "Kyrgyzstan",
                "LA": "Lao People\"s Democratic Republic",
                "LV": "Latvia",
                "LB": "Lebanon",
                "LS": "Lesotho",
                "LR": "Liberia",
                "LY": "Libyan Arab Jamahiriya",
                "LI": "Liechtenstein",
                "LT": "Lithuania",
                "LU": "Luxembourg",
                "MO": "Macao",
                "MK": "Macedonia",
                "MG": "Madagascar",
                "MW": "Malawi",
                "MY": "Malaysia",
                "MV": "Maldives",
                "ML": "Mali",
                "MT": "Malta",
                "MH": "Marshall Islands",
                "MQ": "Martinique",
                "MR": "Mauritania",
                "MU": "Mauritius",
                "YT": "Mayotte",
                "MX": "Mexico",
                "FM": "Micronesia, Federated States Of",
                "MD": "Moldova",
                "MC": "Monaco",
                "MN": "Mongolia",
                "ME": "Montenegro",
                "MS": "Montserrat",
                "MA": "Morocco",
                "MZ": "Mozambique",
                "MM": "Myanmar",
                "NA": "Namibia",
                "NR": "Nauru",
                "NP": "Nepal",
                "NL": "Netherlands",
                "AN": "Netherlands Antilles",
                "NC": "New Caledonia",
                "NZ": "New Zealand",
                "NI": "Nicaragua",
                "NE": "Niger",
                "NG": "Nigeria",
                "NU": "Niue",
                "NF": "Norfolk Island",
                "MP": "Northern Mariana Islands",
                "NO": "Norway",
                "OM": "Oman",
                "PK": "Pakistan",
                "PW": "Palau",
                "PS": "Palestinian Territory, Occupied",
                "PA": "Panama",
                "PG": "Papua New Guinea",
                "PY": "Paraguay",
                "PE": "Peru",
                "PH": "Philippines",
                "PN": "Pitcairn",
                "PL": "Poland",
                "PT": "Portugal",
                "PR": "Puerto Rico",
                "QA": "Qatar",
                "RE": "Reunion",
                "RO": "Romania",
                "RU": "Russian Federation",
                "RW": "Rwanda",
                "BL": "Saint Barthelemy",
                "SH": "Saint Helena",
                "KN": "Saint Kitts And Nevis",
                "LC": "Saint Lucia",
                "MF": "Saint Martin",
                "PM": "Saint Pierre And Miquelon",
                "VC": "Saint Vincent And Grenadines",
                "WS": "Samoa",
                "SM": "San Marino",
                "ST": "Sao Tome And Principe",
                "SA": "Saudi Arabia",
                "SN": "Senegal",
                "RS": "Serbia",
                "SC": "Seychelles",
                "SL": "Sierra Leone",
                "SG": "Singapore",
                "SK": "Slovakia",
                "SI": "Slovenia",
                "SB": "Solomon Islands",
                "SO": "Somalia",
                "ZA": "South Africa",
                "GS": "South Georgia And Sandwich Isl.",
                "ES": "Spain",
                "LK": "Sri Lanka",
                "SD": "Sudan",
                "SR": "Suriname",
                "SJ": "Svalbard And Jan Mayen",
                "SZ": "Swaziland",
                "SE": "Sweden",
                "CH": "Switzerland",
                "SY": "Syrian Arab Republic",
                "TW": "Taiwan",
                "TJ": "Tajikistan",
                "TZ": "Tanzania",
                "TH": "Thailand",
                "TL": "Timor-Leste",
                "TG": "Togo",
                "TK": "Tokelau",
                "TO": "Tonga",
                "TT": "Trinidad And Tobago",
                "TN": "Tunisia",
                "TR": "Turkey",
                "TM": "Turkmenistan",
                "TC": "Turks And Caicos Islands",
                "TV": "Tuvalu",
                "UG": "Uganda",
                "UA": "Ukraine",
                "AE": "United Arab Emirates",
                "GB": "United Kingdom",
                "US": "United States",
                "UM": "United States Outlying Islands",
                "UY": "Uruguay",
                "UZ": "Uzbekistan",
                "VU": "Vanuatu",
                "VE": "Venezuela",
                "VN": "Vietnam",
                "VG": "Virgin Islands, British",
                "VI": "Virgin Islands, U.S.",
                "WF": "Wallis And Futuna",
                "EH": "Western Sahara",
                "YE": "Yemen",
                "ZM": "Zambia",
                "ZW": "Zimbabwe"
              }
            },
            {
              "key": "sites[].latitude",
              "placeholder": "Latitude of site"
            },
            {
              "key": "sites[].longitude",
              "placeholder": "Longitude of site"
            },
            {
              "key": "sites[].primary_contact_email",
              "placeholder": "Primary contact email"
            },
            {
              "key": "sites[].secondary_contact_email",
              "placeholder": "Secondary contact email"
            },
            {
              "title": "Downtime (site)",
              "type": "tabarray",
              "items": {
                "type": "section",
                "items": [
                  {
                    "key": "sites[].downtime[].date_range",
                    "type": "text",
                    "placeholder": "Select date range",
                    "htmlClass": "datepicker"
                  },
                  {
                    "key": "sites[].downtime[].type",
                    "placeholder": "Type of downtime"
                  },
                  {
                    "key": "sites[].downtime[].reason",
                    "type": "textarea",
                    "placeholder": "Reason for downtime"
                  }
                ]
              }
            },
            {
              "type": "fieldset",
              "title": "Storage",
              "expandable": true,
              "items": [
                {
                  "type": "tabarray",
                  "items": [
                    {
                      "type": "section",
                      "legend": "{{value}} ({{idx-1}})",
                      "items": [
                        {
                          "key": "sites[].storages[].id",
                          "readOnly": true
                        },
                        {
                          "key": "sites[].storages[].host",
                          "placeholder": "The hostname for this storage excluding prefix and path"
                        },
                        {
                          "key": "sites[].storages[].base_path",
                          "placeholder": "The base path for access to this storage element"
                        },
                        {
                          "key": "sites[].storages[].srm"
                        },
                        {
                          "key": "sites[].storages[].device_type"
                        },
                        {
                          "key": "sites[].storages[].size_in_terabytes",
                          "placeholder": "Storage capacity of this storage element in TB"
                        },
                        {
                          "key": "sites[].storages[].name",
                          "placeholder": "A name used to identify this storage element",
                          "valueInLegend": true
                        },
                        {
                          "type": "tabarray",
                          "title": "Supported protocols",
                          "expandable": false,
                          "items": [
                            {
                              "type": "section",
                              "legend": "{{value}} ({{idx-1}})",
                              "items": [
                                {
                                  "key": "sites[].storages[].supported_protocols[].prefix",
                                  "placeholder": "The prefix for this protocol",
                                  "valueInLegend": true
                                },
                                {
                                  "key": "sites[].storages[].supported_protocols[].port",
                                  "placeholder": "The port for this protocol"
                                }
                              ]
                            }
                          ]
                        },
                        {
                          "title": "Downtime (storage)",
                          "type": "tabarray",
                          "items": {
                            "type": "section",
                            "items": [
                              {
                                "key": "sites[].storages[].downtime[].date_range",
                                "type": "text",
                                "placeholder": "Select date range",
                                "htmlClass": "datepicker"
                              },
                              {
                                "key": "sites[].storages[].downtime[].type",
                                "placeholder": "Type of downtime"
                              },
                              {
                                "key": "sites[].storages[].downtime[].reason",
                                "type": "textarea",
                                "placeholder": "Reason for downtime"
                              }
                            ]
                          }
                        },
                        {
                          "type": "tabarray",
                          "title": "Areas",
                          "expandable": false,
                          "items": [
                            {
                              "type": "section",
                              "legend": "{{value}} ({{idx-1}})",
                              "items": [
                                {
                                  "key": "sites[].storages[].areas[].id",
                                  "readOnly": true
                                },
                                {
                                  "key": "sites[].storages[].areas[].type"
                                },
                                {
                                  "key": "sites[].storages[].areas[].relative_path",
                                  "placeholder": "The path for this area relative to the storage base path"
                                },
                                {
                                  "key": "sites[].storages[].areas[].name",
                                  "placeholder": "A name used to identify this storage area",
                                  "valueInLegend": true
                                },
                                {
                                  "key": "sites[].storages[].areas[].tier",
                                  "placeholder": "The storage area tier",
                                  "type": "radios"
                                },
                                {
                                  "title": "Downtime (storage area)",
                                  "type": "tabarray",
                                  "items": {
                                    "type": "section",
                                    "items": [
                                      {
                                        "key": "sites[].storages[].areas[].downtime[].date_range",
                                        "type": "text",
                                        "placeholder": "Select date range",
                                        "htmlClass": "datepicker"
                                      },
                                      {
                                        "key": "sites[].storages[].areas[].downtime[].type",
                                        "placeholder": "Type of downtime"
                                      },
                                      {
                                        "key": "sites[].storages[].areas[].downtime[].reason",
                                        "type": "textarea",
                                        "placeholder": "Reason for downtime"
                                      }
                                    ]
                                  }
                                },
                                {
                                  "key": "sites[].storages[].areas[].other_attributes",
                                  "type": "ace",
                                  "aceMode": "json",
                                  "aceTheme": "twilight"
                                },
                                {
                                  "key": "sites[].storages[].areas[].is_force_disabled",
                                  "notitle": true,
                                  "inlinetitle": "Force disable storage area?",
                                  "htmlClass": "highlight-disable"
                                }
                              ]
                            }
                          ]
                        },
                        {
                          "key": "sites[].storages[].is_force_disabled",
                          "notitle": true,
                          "inlinetitle": "Force disable storage?",
                          "htmlClass": "highlight-disable"
                        }
                      ]
                    }
                  ]
                }
              ]
            },
            {
              "type": "fieldset",
              "title": "Compute",
              "expandable": true,
              "items": [
                {
                  "type": "tabarray",
                  "items": [
                    {
                      "type": "section",
                      "legend": "{{value}} ({{idx-1}})",
                      "items": [
                        {
                          "key": "sites[].compute[].id",
                          "readOnly": true
                        },
                        {
                          "key": "sites[].compute[].hardware_capabilities",
                          "type": "checkboxes",
                          "placeholder": "Hardware capabilities for this compute element"
                        },
                        {
                          "key": "sites[].compute[].hardware_type",
                          "type": "radios",
                          "placeholder": "Hardware types for this compute element"
                        },
                        {
                          "key": "sites[].compute[].description",
                          "placeholder": "Description of this compute element"
                        },
                        {
                          "key": "sites[].compute[].name",
                          "placeholder": "A name used to identify this compute element",
                          "valueInLegend": true
                        },
                        {
                          "key": "sites[].compute[].middleware_version",
                          "placeholder": "Middleware version for this compute element"
                        },
                        {
                          "title": "Downtime (compute)",
                          "type": "tabarray",
                          "items": {
                            "type": "section",
                            "items": [
                              {
                                "key": "sites[].compute[].downtime[].date_range",
                                "type": "text",
                                "placeholder": "Select date range",
                                "htmlClass": "datepicker"
                              },
                              {
                                "key": "sites[].compute[].downtime[].type",
                                "placeholder": "Type of downtime"
                              },
                              {
                                "key": "sites[].compute[].downtime[].reason",
                                "type": "textarea",
                                "placeholder": "Reason for downtime"
                              }
                            ]
                          }
                        },
                        {
                          "type": "tabarray",
                          "title": "Associated local services",
                          "expandable": false,
                          "items": [
                            {
                              "type": "section",
                              "legend": "{{value}} ({{idx-1}})",
                              "items": [
                                {
                                  "key": "sites[].compute[].associated_local_services[].id",
                                  "readOnly": true
                                },
                                {
                                  "key": "sites[].compute[].associated_local_services[].type",
                                  "valueInLegend": true
                                },
                                {
                                  "key": "sites[].compute[].associated_local_services[].version",
                                  "placeholder": "The version of this service"
                                },
                                {
                                  "key": "sites[].compute[].associated_local_services[].prefix",
                                  "placeholder": "The prefix for this service (if applicable)"
                                },
                                {
                                  "key": "sites[].compute[].associated_local_services[].host",
                                  "placeholder": "The hostname for this service excluding prefix and path (if applicable)"
                                },
                                {
                                  "key": "sites[].compute[].associated_local_services[].port",
                                  "placeholder": "The port for this service (if applicable)"
                                },
                                {
                                  "key": "sites[].compute[].associated_local_services[].path",
                                  "placeholder": "The path for this service (if applicable)"
                                },
                                {
                                  "key": "sites[].compute[].associated_local_services[].associated_storage_area_id",
                                  "placeholder": "Associated storage area ID (if applicable)"
                                },
                                {
                                  "key": "sites[].compute[].associated_local_services[].name",
                                  "placeholder": "A name used to identify this service"
                                },
                                {
                                  "key": "sites[].compute[].associated_local_services[].is_mandatory",
                                  "notitle": true,
                                  "inlinetitle": "Mandatory?"
                                },
                                {
                                  "title": "Downtime (service)",
                                  "type": "tabarray",
                                  "items": {
                                    "type": "section",
                                    "items": [
                                      {
                                        "key": "sites[].compute[].associated_local_services[].downtime[].date_range",
                                        "type": "text",
                                        "placeholder": "Select date range",
                                        "htmlClass": "datepicker"
                                      },
                                      {
                                        "key": "sites[].compute[].associated_local_services[].downtime[].type",
                                        "placeholder": "Type of downtime"
                                      },
                                      {
                                        "key": "sites[].compute[].associated_local_services[].downtime[].reason",
                                        "type": "textarea",
                                        "placeholder": "Reason for downtime"
                                      }
                                    ]
                                  }
                                },
                                {
                                  "key": "sites[].compute[].associated_local_services[].other_attributes",
                                  "type": "ace",
                                  "aceMode": "json",
                                  "aceTheme": "twilight"
                                },
                                {
                                  "key": "sites[].compute[].associated_local_services[].is_force_disabled",
                                  "notitle": true,
                                  "inlinetitle": "Force disable service?",
                                  "htmlClass": "highlight-disable"
                                }
                              ]
                            }
                          ]
                        },
                        {
                          "type": "tabarray",
                          "title": "Associated global services",
                          "expandable": false,
                          "items": [
                            {
                              "type": "section",
                              "legend": "{{value}} ({{idx-1}})",
                              "items": [
                                {
                                  "key": "sites[].compute[].associated_global_services[].id",
                                  "readOnly": true
                                },
                                {
                                  "key": "sites[].compute[].associated_global_services[].type",
                                  "valueInLegend": true
                                },
                                {
                                  "key": "sites[].compute[].associated_global_services[].version",
                                  "placeholder": "The version of this service"
                                },
                                {
                                  "key": "sites[].compute[].associated_global_services[].prefix",
                                  "placeholder": "The prefix for this service"
                                },
                                {
                                  "key": "sites[].compute[].associated_global_services[].host",
                                  "placeholder": "The hostname for this service excluding prefix and path (if applicable)"
                                },
                                {
                                  "key": "sites[].compute[].associated_global_services[].port",
                                  "placeholder": "The port for this service (if applicable)"
                                },
                                {
                                  "key": "sites[].compute[].associated_global_services[].path",
                                  "placeholder": "The path for this service (if applicable)"
                                },
                                {
                                  "key": "sites[].compute[].associated_global_services[].associated_storage_area_id",
                                  "placeholder": "Associated storage area ID (if applicable)"
                                },
                                {
                                  "key": "sites[].compute[].associated_global_services[].name",
                                  "placeholder": "A name used to identify this service"
                                },
                                {
                                  "title": "Downtime (service)",
                                  "type": "tabarray",
                                  "items": {
                                    "type": "section",
                                    "legend": "{{value}} ({{idx-1}})",
                                    "items": [
                                      {
                                        "key": "sites[].compute[].associated_global_services[].downtime[].date_range",
                                        "type": "text",
                                        "placeholder": "Select date range",
                                        "htmlClass": "datepicker"
                                      },
                                      {
                                        "key": "sites[].compute[].associated_global_services[].downtime[].type",
                                        "placeholder": "Type of downtime"
                                      },
                                      {
                                        "key": "sites[].compute[].associated_global_services[].downtime[].reason",
                                        "type": "textarea",
                                        "placeholder": "Reason for downtime"
                                      }
                                    ]
                                  }
                                },
                                {
                                  "key": "sites[].compute[].associated_global_services[].other_attributes",
                                  "placeholder": "Other attributes for this service in format {\"other_attribute_key\":\"other_attribute_value\"} (if applicable)",
                                  "type": "ace",
                                  "aceMode": "json",
                                  "aceTheme": "twilight"
                                },
                                {
                                  "key": "sites[].compute[].associated_global_services[].is_force_disabled",
                                  "notitle": true,
                                  "inlinetitle": "Force disable service?",
                                  "htmlClass": "highlight-disable"
                                }
                              ]
                            }
                          ]
                        },
                        {
                          "key": "sites[].compute[].is_force_disabled",
                          "notitle": true,
                          "inlinetitle": "Force disable compute?",
                          "htmlClass": "highlight-disable"
                        }
                      ]
                    }
                  ]
                }
              ]
            },
            {
                  "key": "sites[].other_attributes",
                  "title": "Other attributes (as json)",
                  "type": "ace",
                  "aceMode": "json",
                  "aceTheme": "twilight"
            },
            {
              "key": "sites[].is_force_disabled",
              "notitle": true,
              "inlinetitle": "Force disable site?",
              "htmlClass": "highlight-disable"
            }
        ]
      }
    },
    {
      "type": "submit",
      "title": "Save"
    }
]