function loadDynamicOptions(resourceType, values) {
    const siteSelected = $('select[name="site"]').val();
    const site = values.sites.find(site => site.name === siteSelected);
    let options = {};

    switch (resourceType) {
        case 'sites':
            options[site.id] = site.name;
            break;
        case 'compute': {
            site?.compute?.forEach(compute => {
                options[compute.id] = compute.name || compute.description;
            });
            break;
        }
        case 'storages': {
            site?.storages?.forEach(storage => {
                options[storage.id] = storage.host;
            });
            break;
        }
        case 'storage_areas': {
            site?.storages?.forEach(storage => {
                storage.areas?.forEach(area => {
                    options[area.id] = `${storage.host} - ${area.name}`;
                });
            });
            break;
        }
        case 'compute_local_services': {
            site?.compute?.forEach(compute => {
                compute.associated_local_services?.forEach(service => {
                    options[service.id] = `${compute.name || compute.description} - ${service.type} - ${service.host}`;
                });
            });
            break;
        }
        case 'compute_global_services': {
            site?.compute?.forEach(compute => {
                compute.associated_global_services?.forEach(service => {
                    options[service.id] = `${compute.name || compute.description} - ${service.type} - ${service.host}`;
                });
            });
            break;
        }
    }
    return options;
}

function reinitialiseWithNewOptions(resourceType, node_values, downtime_form, downtimeFormUi) {
    const options = loadDynamicOptions(resourceType, node_values);
    const updatedSchema = {...downtime_schema};

    const currentFormValues = downtime_form.jsonFormValue();
    updatedSchema.properties.specificResource.enum = Object.keys(options);

    const updatedFormUi = downtimeFormUi.map(item => {
        if (item.key === "specificResource") {
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
            console.log("calling update with values");
            updateNodeJson(node_values, values);
        }
    });
}


function updateNodeJson(node_values, form_values) {
    const {site, resourceType, specificResource, type, date_range, reason} = form_values;
    console.log(site, resourceType, specificResource, type, date_range, reason);

    switch (resourceType) {
        case 'sites':
            node_values.sites.forEach(s => {
                if (s.id === specificResource) {
                    s.downtime = s.downtime || [];
                    s.downtime.push({
                        type: type,
                        reason: reason,
                        date_range: date_range
                    });
                }
            });
            break;
        case 'compute' :
            node_values.sites.forEach(site => {
                site.compute.forEach(s => {
                    if (s.id === specificResource) {
                        s.downtime = s.downtime || [];
                        s.downtime.push({
                            type: type,
                            reason: reason,
                            date_range: date_range
                        });
                    }
                })
            })
            break;
        case 'storages'  :
            node_values.sites.forEach(site => {
                site.storages.forEach(s => {
                    if (s.id === specificResource) {
                        s.downtime = s.downtime || [];
                        s.downtime.push({
                            type: type,
                            reason: reason,
                            date_range: date_range
                        });
                    }
                })
            })
            break;
        case 'storage_areas'  :
            node_values.sites.forEach(site => {
                site.storages.forEach(s => {
                    s.areas.forEach(a => {
                        if (a.id === specificResource) {
                            a.downtime = a.downtime || [];
                            a.downtime.push({
                                type: type,
                                reason: reason,
                                date_range: date_range
                            });
                        }
                    })
                })
            })
            break;
        case 'compute_local_services'  :
            node_values.sites.forEach(site => {
                site.compute.forEach(s => {
                    s.associated_local_services.forEach(a => {
                        if (a.id === specificResource) {
                            a.downtime = a.downtime || [];
                            a.downtime.push({
                                type: type,
                                reason: reason,
                                date_range: date_range
                            });
                        }
                    })
                })
            })
            break;
        case 'compute_global_services'   :
            node_values.sites.forEach(site => {
                site.compute.forEach(s => {
                    s.associated_global_services.forEach(a => {
                        if (a.id === specificResource) {
                            a.downtime = a.downtime || [];
                            a.downtime.push({
                                type: type,
                                reason: reason,
                                date_range: date_range
                            });
                        }
                    })
                })
            })
            break;
    }
    console.log(node_values);
}

