function getStartEndDates(downtime) {
    const [start, end] = downtime.date_range.split(' to ')
        .map(dateStr => new Date(dateStr.trim()));

    return {start, end};
}

function getStatus(start, end) {
    const now = new Date();
    if (now < new Date(start)) {
        return "upcoming";
    } else if (now >= new Date(start) && now <= new Date(end)) {
        return "ongoing";
    } else {
        return "completed";
    }
}


function getDowntimes(node_values) {
    const downtimes = {
        upcoming: [],
        ongoing: [],
        completed: []
    };

    function collect(resourceType, items, getName, getId) {
        (items || []).forEach(item => {
            (item.downtime || []).forEach(downtime => {
                const {start, end} = getStartEndDates(downtime);
                const status = getStatus(start, end);
                downtimes[status].push({
                    resourceType,
                    resourceName: getName(item),
                    resourceId: getId(item),
                    start: start.toLocaleString(),
                    end: end.toLocaleString(),
                    ...downtime
                });
            });
        });
    }

    node_values.sites.forEach(site => {
        collect('sites', [site], s => s.name, s => s.id);
        collect('compute', site.compute, c => c.name || c.description, c => c.id);
        collect('storages', site.storages, s => s.host, s => s.id);

        (site.storages || []).forEach(storage => {
            collect('storage_areas', storage.areas, a => `${a.name} ${a.type}`, a => a.id);
        });

        (site.compute || []).forEach(compute => {
            collect('compute_local_services', compute.associated_local_services, s => `${s.name} ${s.host}`, s => s.id);
            collect('compute_global_services', compute.associated_global_services, s => `${s.name} ${s.host}`, s => s.id);
        });
    });

    return downtimes;
}


function createDowntimeRows(values, table) {
    values.forEach(downtime => {
        const row = document.createElement('tr');
        row.setAttribute('data-type', downtime.resourceType);
        row.setAttribute('data-resource-id', downtime.resourceId);
        row.setAttribute('data-downtime-id', downtime.id);
        const impactClass = downtime.type === 'Planned' ? 'impact-Degraded' : 'impact-Downtime';
        row.innerHTML = `
              <td>${downtime.resourceType}</td>
              <td>${downtime.resourceName}</td>
              <td><span class="badge impact-badge ${impactClass}">${downtime.type}</span></td>
              <td style="max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; cursor:pointer" title="${downtime.reason}">${downtime.reason}</td>
              <td>${downtime.start}</td>
              <td>${downtime.end}</td>
              <td><span class="delete-btn text-danger" role="button" style="cursor:pointer" aria-label="Delete Downtime"><i
                        class="bi bi-trash me-1"></i><span> Delete</span></span></td>
        `;
        table.appendChild(row);
    })
}




function deleteDowntimeEntry(node_values, resourceType, resourceId, downtimeId) {
    function removeDowntimeFromList(items) {
        items.forEach(item => {
            if (item.id === resourceId) {
                item.downtime = item.downtime.filter(downtime => downtime.id !== downtimeId);
            }
        });
    }

    node_values.sites.forEach(site => {
        switch (resourceType) {
            case 'sites':
                if (site.id === resourceId) {
                    site.downtime = site.downtime.filter(downtime => downtime.id !== downtimeId);
                }
                break;
            case 'compute':
                removeDowntimeFromList(site.compute || []);
                break;
            case 'storages':
                removeDowntimeFromList(site.storages || []);
                break;
            case 'storage_areas':
                (site.storages || []).forEach(storage => {
                    removeDowntimeFromList(storage.areas || []);
                });
                break;
            case 'compute_local_services':
                (site.compute || []).forEach(compute => {
                    removeDowntimeFromList(compute.associated_local_services || []);
                });
                break;
            case 'compute_global_services':
                (site.compute || []).forEach(compute => {
                    removeDowntimeFromList(compute.associated_global_services || []);
                });
                break;
        }
    });
    return node_values;
}


function deleteDowntimeHandler(node_values, token, editNodeUrl, downtime) {
    if (downtime.id === "undefined") {
        console.log("in heree")
        showAndDismissAlert('danger', 'Downtime ID is undefined. Cannot proceed with deletion.');
        return;
    }

    const updatedNodeValues = deleteDowntimeEntry(node_values, downtime.resourceType, downtime.resourceId, downtime.id);
    let jsonParsingErrors = parseOtherAttributes(updatedNodeValues);

    if (jsonParsingErrors.length > 0) {
        let message = `The field <b>${jsonParsingErrors[0].uri}</b> failed validation: ${jsonParsingErrors[0].message}.`;
        showAndDismissAlert('danger', message);
        return;
    }

    fetch(editNodeUrl, {
        method: 'POST',
        headers: {
            "Authorization": token,
            "Content-Type": "application/json"
        },
        body: JSON.stringify(updatedNodeValues)
    })
        .then(response => {
            if (!response.ok) {
                return response.json().then(text => {
                    throw new Error(text)
                });
            }
            downtime.row.remove()
        })
        .then(data => {
            showAndDismissAlert('success', 'Downtime successfully deleted.')
        })
        .catch(error => {
            showAndDismissAlert('danger', error.message)
        });
}