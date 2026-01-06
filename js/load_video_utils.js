import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

app.registerExtension({
    name: "MyCustomNodes.LoadVideoFromOutput",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "LoadVideoFromOutput") {
            
            // Hook into the node creation to add our widget
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                onNodeCreated?.apply(this, arguments);

                const refreshButton = this.addWidget("button", "Refresh List", null, () => {
                    // When clicked, fetch the list from our Python API
                    api.fetchApi("/my_custom_nodes/refresh_video_list")
                        .then(response => response.json())
                        .then(files => {
                            // Find the 'video' dropdown widget
                            const videoWidget = this.widgets.find(w => w.name === "video");
                            
                            if (videoWidget) {
                                // Update the options
                                videoWidget.options.values = files;
                                
                                // Optional: If current value is invalid, reset it
                                if (!files.includes(videoWidget.value)) {
                                    videoWidget.value = files[0] || "";
                                }
                                
                                // Force a redraw of the node to show changes
                                this.setDirtyCanvas(true, true);
                            }
                        })
                        .catch(err => {
                            console.error("Error fetching video list:", err);
                        });
                });
            };
        }
    }
});
