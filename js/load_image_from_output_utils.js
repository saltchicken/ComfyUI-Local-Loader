import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

app.registerExtension({
    name: "MyCustomNodes.LoadImageFromOutput",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "LoadImageFromOutput") {
            
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                onNodeCreated?.apply(this, arguments);

                const node = this;

                // Function to fetch images for a specific directory and update the image widget
                const updateImagesForDirectory = async (dirName) => {
                    try {
                        // Call Python API with the selected directory
                        const response = await api.fetchApi(`/my_custom_nodes/output_images?dir=${encodeURIComponent(dirName)}`);
                        const images = await response.json();

                        const imageWidget = node.widgets.find(w => w.name === "image");
                        if (imageWidget) {
                            imageWidget.options.values = images;
                            
                            // If current value isn't in the new list, select the first one or empty
                            if (!images.includes(imageWidget.value)) {
                                imageWidget.value = images.length > 0 ? images[0] : "";
                            }
                            
                            // Redraw
                            node.setDirtyCanvas(true, true);
                        }
                    } catch (err) {
                        console.error("Error fetching images for dir:", err);
                    }
                };

                // 1. Setup Directory Widget Callback
                const dirWidget = this.widgets.find(w => w.name === "directory");
                if (dirWidget) {
                    // Standard ComfyUI callback for dropdown changes
                    dirWidget.callback = (value) => {
                        updateImagesForDirectory(value);
                    };
                }

                // 2. Add Refresh Button
                this.addWidget("button", "Refresh List", null, () => {
                    // Refresh Directories
                    api.fetchApi("/my_custom_nodes/output_directories")
                        .then(response => response.json())
                        .then(dirs => {
                            if (dirWidget) {
                                dirWidget.options.values = dirs;
                                // If current dir is invalid, reset to root or first available
                                if (!dirs.includes(dirWidget.value)) {
                                    dirWidget.value = dirs.includes("") ? "" : (dirs[0] || "");
                                }
                                
                                // After refreshing directories, refresh the images for the currently selected dir
                                updateImagesForDirectory(dirWidget.value);
                            }
                        })
                        .catch(err => console.error("Error fetching directories:", err));
                });
            };
        }
    }
});
