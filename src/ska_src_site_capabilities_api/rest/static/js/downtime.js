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

function addDowntime(resources, id, downtime) {
    const resource = resources.find(_ => _.id === id);
    if (resource) {
        resource.downtime ??= [];
        resource.downtime.push(downtime);
    }
}

function updateNodeJson(node_values, form_values) {
    const {site, resourceType, specificResource, type, date_range, reason} = form_values;

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
            addDowntime(affectedSite?.compute, specificResource, downtime)
            break;
        case 'storages'  :
            addDowntime(affectedSite?.storages, specificResource, downtime)
            break;
        case 'storage_areas'  :
            affectedSite?.storages.forEach(storage => {
                addDowntime(storage.areas, specificResource, downtime)
            })
            break;
        case 'compute_local_services'  :
            affectedSite?.compute.forEach(compute => {
                addDowntime(compute.associated_local_services, specificResource, downtime)
            })
            break;
        case 'compute_global_services'   :
            affectedSite?.compute.forEach(compute => {
                addDowntime(compute.associated_global_services, specificResource, downtime)
            })
            break;
    }
    console.log(node_values);
}

