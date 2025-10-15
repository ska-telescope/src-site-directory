function loadDynamicOptions(resourceType, values) {
    const siteSelected = $('select[name="site"]').val();
    let options = {};
    switch (resourceType) {
        case 'sites':
            values.sites.forEach(site => {
                options[site.id] = site.name;
            })
            return options;
        case 'compute':
            let site = values.sites.find(site1 => site1.name === siteSelected);
            site.compute.forEach(compute => {
                options[compute.id] = compute.name || compute.description;
            })
            return options;
        case 'storages':
            let siteForStorage = values.sites.find(site1 => site1.name === siteSelected);
            siteForStorage.storages.forEach(storage => {
                options[storage.id] = storage.host;
            })
            return options;
        case 'storage-areas':
            let siteForStorageArea = values.sites.find(site1 => site1.name === siteSelected);
            siteForStorageArea.storages.forEach((storage) => {
                storage.areas.forEach(area => {
                    options[area.id] = `${storage.host} - ${area.name}`;
                });
            });
            return options;
    }
}