function getShortUuid(uuid) {
    return uuid.replace(/-/g, "").slice(0, 6);
}

function loadDynamicOptions(resourceType, values) {
    const siteSelected = $('select[name="site"]').val();
    const site = values.sites.find(site => site.name === siteSelected);
    let options = {};

    switch (resourceType) {
        case 'sites':
            options[site.id] = `urn:srcnet:site:${site.name}:${getShortUuid(site.id)}`
            break;
        case 'compute': {
            site?.compute?.forEach(compute => {
                options[compute.id] =
                    `urn:srcnet:compute:${compute.name || compute.description}:${getShortUuid(compute.id)}`
            });
            break;
        }
        case 'storages': {
            site?.storages?.forEach(storage => {
                options[storage.id] =
                    `urn:srcnet:storage:${storage.srm}:${storage.host}:${storage.base_path}:${getShortUuid(storage.id)}`
            });
            break;
        }
        case 'storage_areas': {
            site?.storages?.forEach(storage => {
                storage.areas?.forEach(area => {
                    options[area.id] =
                        `urn:srcnet:storage-area:${area.name}:${area.type}:${area.relative_path}:${getShortUuid(area.id)}`
                });
            });
            break;
        }
        case 'compute_local_services': {
            site?.compute?.forEach(compute => {
                compute.associated_local_services?.forEach(service => {
                    options[service.id] =
                        `urn:srcnet:local-service:${service.name}:${service.type}:${service.host}:${getShortUuid(service.id)}`
                });
            });
            break;
        }
        case 'compute_global_services': {
            site?.compute?.forEach(compute => {
                compute.associated_global_services?.forEach(service => {
                    options[service.id] =
                        `urn:srcnet:global-service:${service.name}:${service.type}:${service.host}:${getShortUuid(service.id)}`;
                });
            });
            break;
        }
    }
    return options;
}

function reinitialiseWithNewOptions(resourceType, node_values, downtime_form, downtimeFormUi, token, editNodeEndpointUrl) {
    const options = loadDynamicOptions(resourceType, node_values);
    const updatedSchema = {...downtime_schema};

    const currentFormValues = downtime_form.jsonFormValue();
    updatedSchema.properties.uniqueResourceName.enum = Object.keys(options);

    const updatedFormUi = downtimeFormUi.map(item => {
        if (item.key === "uniqueResourceName") {
            return {...item, titleMap: options};
        }
        return item;
    });

    downtime_form.html('');
    downtime_form.jsonForm({
        schema: updatedSchema,
        form: updatedFormUi,
        value: currentFormValues,
        validate: true,
        onSubmit: function (formErrors, values) {
            if (formErrors) {
                let fieldPath = formErrors[0].uri.split('#/')[1];
                let message = `The field <b>${fieldPath}</b> failed validation: ${formErrors[0].message}.`;
                showAndDismissAlert('danger', message);
                return; // Stop execution on validation error
            }

            updateNodeJson(node_values, values);
            let jsonParsingErrors = parseOtherAttributes(node_values);

            if (jsonParsingErrors.length > 0) {
                let message = `The field <b>${jsonParsingErrors[0].uri}</b> failed validation: ${jsonParsingErrors[0].message}.`;
                showAndDismissAlert('danger', message);
                // Stop execution if parsing fails
                return;
            }
            // --- REUSED LOGIC: AJAX Submission ---
            else {
                $.ajax({
                    url: editNodeEndpointUrl, // Use the specific endpoint URL passed to the function
                    data: JSON.stringify(node_values),
                    type: 'POST', // Assuming your API uses POST for edits/updates. Change to 'PUT' if necessary.
                    headers: {
                        // Use the access token passed to the function
                        "Authorization": token
                    },
                    success: function (data) {
                        showAndDismissAlert('success', 'Node successfully edited after downtime schedule.')
                    },
                    error: function (xhr, textStatus, errorThrown) {
                        // Display server error
                        showAndDismissAlert('danger', xhr.responseText)
                    }
                });
            }
        }
    });
}

function parseOtherAttributes(obj, parentPath = '') {
    let errors = [];

    function recursiveParse(obj, currentPath) {
        for (let key in obj) {
            if (obj.hasOwnProperty(key)) {
                let newPath = currentPath ? `${currentPath}/${key}` : key;

                if (key === "other_attributes" && typeof obj[key] === "string") {
                    try {
                        if (obj[key] === "") {
                            obj[key] = "{}";
                        }
                        obj[key] = JSON.parse(obj[key]);  // Parse and replace
                    } catch (error) {
                        errors.push({
                            uri: newPath, // More readable path
                            message: error.message
                        });
                    }
                } else if (typeof obj[key] === "object" && obj[key] !== null) {
                    recursiveParse(obj[key], newPath);  // Recursively track path
                }
            }
        }
    }

    recursiveParse(obj, parentPath);
    return errors.length > 0 ? errors : false;
}

function addDowntime(resources, id, downtime) {
    const resource = resources.find(_ => _.id === id);
    if (resource) {
        resource.downtime ??= [];
        resource.downtime.push(downtime);
    }
}

function updateNodeJson(node_values, form_values) {
    const {site, resourceType, uniqueResourceName, type, date_range, reason} = form_values;

    const affectedSite = node_values.sites.find(s => s.name === site);
    const downtime = {
        type: type,
        reason: reason,
        date_range: date_range
    };

    switch (resourceType) {
        case 'sites':
            affectedSite.downtime ??= [];
            affectedSite?.downtime.push(downtime);
            break;
        case 'compute' :
            addDowntime(affectedSite?.compute, uniqueResourceName, downtime)
            break;
        case 'storages'  :
            addDowntime(affectedSite?.storages, uniqueResourceName, downtime)
            break;
        case 'storage_areas'  :
            affectedSite?.storages.forEach(storage => {
                addDowntime(storage.areas, uniqueResourceName, downtime)
            })
            break;
        case 'compute_local_services'  :
            affectedSite?.compute.forEach(compute => {
                addDowntime(compute.associated_local_services, uniqueResourceName, downtime)
            })
            break;
        case 'compute_global_services'   :
            affectedSite?.compute.forEach(compute => {
                addDowntime(compute.associated_global_services, uniqueResourceName, downtime)
            })
            break;
    }

}

function getStartEndDates(downtime) {
    const [start, end] = downtime.date_range.split(' to ')
        .map(dateStr => new Date(dateStr.trim()).toLocaleString());

    return {start, end};
}

function getDowntimes(node_values) {
    const sites = node_values.sites.flatMap(site => {
        return (site.downtime || []).map(downtime => {
            const {start, end} = getStartEndDates(downtime);
            return {
                resourceType: 'sites',
                resourceName: `${site.name}`,
                resourceId: site.id,
                start, end, ...downtime
            }
        });
    })

    const compute = node_values.sites.flatMap(site => {
        return (site.compute || []).flatMap(compute => {
            return (compute.downtime || []).map(downtime => {
                const {start, end} = getStartEndDates(downtime);
                return {
                    resourceType: 'compute',
                    resourceName: `${compute.name || compute.description}`,
                    resourceId: compute.id,
                    start, end, ...downtime
                }
            });
        });
    });

    const storages = node_values.sites.flatMap(site => {
        return (site.storages || []).flatMap(storage => {
            return (storage.downtime || []).map(downtime => {
                const {start, end} = getStartEndDates(downtime);
                return {
                    resourceType: 'storages',
                    resourceName: `${storage.host}`,
                    resourceId: storage.id,
                    start, end, ...downtime
                }
            });
        });
    });

    const storage_areas = node_values.sites.flatMap(site => {
        return (site.storages || []).flatMap(storage => {
            return (storage.areas || []).flatMap(area => {
                return (area.downtime || []).map(downtime => {
                    const {start, end} = getStartEndDates(downtime);
                    return {
                        resourceType: 'storage_areas',
                        resourceName: `${area.name} ${area.type}`,
                        resourceId: area.id,
                        start, end, ...downtime
                    }
                });
            });
        });
    })


    const compute_local_services = node_values.sites.flatMap(site => {
        return (site.compute || []).flatMap(compute => {
            return (compute.associated_local_services || []).flatMap(service => {
                return (service.downtime || []).map(downtime => {
                    const {start, end} = getStartEndDates(downtime);
                    return {
                        resourceType: 'compute_local_services',
                        resourceName: `${service.name} ${service.host}`,
                        resourceId: service.id,
                        start, end, ...downtime
                    }
                });
            });
        });
    });

    const compute_global_services = node_values.sites.flatMap(site => {
        return (site.compute || []).flatMap(compute => {
            return (compute.associated_global_services || []).flatMap(service => {
                return (service.downtime || []).map(downtime => {
                    const {start, end} = getStartEndDates(downtime);
                    return {
                        resourceType: 'compute_global_services',
                        resourceName: `${service.name} ${service.host}`,
                        resourceId: service.id,
                        start, end, ...downtime
                    }
                });
            });
        });
    });
    return [...sites, ...compute, ...storages, ...storage_areas, ...compute_local_services, ...compute_global_services];
}