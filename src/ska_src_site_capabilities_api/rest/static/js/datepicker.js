function initialiseDatePickers(dateElementDivSelector, easepickCssUrl) {
    document.querySelectorAll(dateElementDivSelector + " input").forEach(input => {
        if (!input.classList.contains("easepick-initialised")) {
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
                    format: "HH:mm:ss",
                    hours: { step: 1 },
                    minutes: { step: 1 },
                    seconds: { step: 1 }
                },
                format: "YYYY-MM-DD HH:mm:ss",
                setup(picker) {
                    picker.on("select", (evt) => {
                        input.value = evt.detail.start + " to " + evt.detail.end;
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
    // ✅Create MutationObserver to detect dynamically added date inputs
    const observer = createNewMutationObserver(dateElementDivSelector, easepickCssUrl)
    observer.observe(document.body, { childList: true, subtree: true });
}

