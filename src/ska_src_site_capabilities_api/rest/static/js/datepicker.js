function initialiseDatePickers(dateElementSelector, easepickCssUrl) {
    console.log(dateElementSelector);
    document.querySelectorAll(dateElementSelector + " input").forEach(input => {
        if (!input.classList.contains("easepick-initialised")) {
            const picker = new easepick.create({
                autoApply: false,
                element: input,
                css: [
                    cssUrl
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

function createNewMutationObserver(dateElementSelector, easepickCssUrl) {
    const observer = new MutationObserver((mutations) => {
        mutations.forEach(mutation => {
            mutation.addedNodes.forEach(node => {
                if (node.nodeType === 1 && node.matches(dateElementSelector)) {
                    console.log("1");
                    initialiseDatePickers(dateElementSelector, easepickCssUrl);
                } else if (node.nodeType === 1) {
                    let newPickers = node.querySelectorAll(dateElementSelector + " input");
                    if (newPickers.length > 0) {
                        console.log("2");
                        initialiseDatePickers(dateElementSelector, easepickCssUrl);
                    }
                }
            });
        });
    });
    return observer;
}

function startWatchingForNewDateElements(dateElementSelector, easepickCssUrl) {
    // ✅Create MutationObserver to detect dynamically added date inputs
    const observer = createNewMutationObserver(dateElementSelector, easepickCssUrl)
    observer.observe(document.body, { childList: true, subtree: true });

    // ✅Run once for existing elements
    document.addEventListener("DOMContentLoaded", () => {
        initialiseDatePickers(dateElementSelector, easepickCssUrl);
    });
}

