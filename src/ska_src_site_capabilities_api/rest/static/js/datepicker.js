function initialiseDatePickers(dateElementDivSelector, easepickCssUrl) {
    document.querySelectorAll(dateElementDivSelector + " input").forEach(input => {
        if (!input.classList.contains("easepick-initialised")) {

const existingValue = input.value;
            const picker = new easepick.create({
                autoApply: false,
                element: input,
                css: [
                    easepickCssUrl
                ],
                plugins: ["RangePlugin", "TimePlugin", "AmpPlugin"],
                RangePlugin: {
                    delimiter: " to "
                },
                TimePlugin: {
                    format: "HH:mm",
                    hours: { step: 1 },
                    minutes: { step: 1 }
                },
                setup(picker) {
                    // set the input to any existing date range
                    let startDate = null;
                    let endDate = null;
                    if (existingValue && existingValue.includes("to")) {
                        const dateRange = existingValue.split(" to ");
                        if (dateRange.length === 2) {
                            startDate = new Date(dateRange[0]).toISOString();
                            endDate = new Date(dateRange[1]).toISOString();
                            input.value = `${startDate} to ${endDate}`;
                        }
                    }
                    picker.on("select", (evt) => {
                        const start = evt.detail.start.toJSDate();
                        const end = evt.detail.end.toJSDate();
                        input.value = `${start.toISOString()} to ${end.toISOString()}`;
                    });
                }
            });
            input.classList.add("easepick-initialised");
        }
    });
}

function createNewMutationObserver(dateElementDivSelector, easepickCssUrl) {
    const observer = new MutationObserver((mutations) => {
        mutations.forEach(mutation => {
            mutation.addedNodes.forEach(node => {
                if (node.nodeType === 1) {
                    let newPickers = node.querySelectorAll(dateElementDivSelector);
                    if (newPickers.length > 0) {
                        initialiseDatePickers(dateElementDivSelector, easepickCssUrl);
                    }
                }
            });
        });
    });
    return observer;
}

function startWatchingForNewDateElements(dateElementDivSelector, easepickCssUrl) {
    // Create MutationObserver to detect dynamically added date inputs
    const observer = createNewMutationObserver(dateElementDivSelector, easepickCssUrl)
    observer.observe(document.body, { childList: true, subtree: true });
}

