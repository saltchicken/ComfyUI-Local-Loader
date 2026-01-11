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

                const node = this;


                const updateVideosForDirectory = async (dirName) => {
                    try {
                        const response = await api.fetchApi(`/my_custom_nodes/output_videos?dir=${encodeURIComponent(dirName)}`);
                        const videos = await response.json();

                        const videoWidget = node.widgets.find(w => w.name === "video");
                        if (videoWidget) {
                            videoWidget.options.values = videos;
                            
                            if (!videos.includes(videoWidget.value)) {
                                videoWidget.value = videos.length > 0 ? videos[0] : "";
                            }
                            
                            node.setDirtyCanvas(true, true);
                        }
                    } catch (err) {
                        console.error("Error fetching videos for dir:", err);
                    }
                };


                const dirWidget = this.widgets.find(w => w.name === "directory");
                if (dirWidget) {
                    dirWidget.callback = (value) => {

                        dirWidget.value = value;
                        updateVideosForDirectory(value);
                    };
                }


                this.addWidget("button", "Refresh List", null, () => {
                    // Fetch Directories first
                    api.fetchApi("/my_custom_nodes/output_video_directories")
                        .then(response => response.json())
                        .then(dirs => {
                            if (dirWidget) {
                                dirWidget.options.values = dirs;
                                
                                // Reset validation
                                if (!dirs.includes(dirWidget.value)) {
                                    dirWidget.value = dirs.includes("") ? "" : (dirs[0] || "");
                                }
                                
                                // Fetch videos for the valid directory
                                updateVideosForDirectory(dirWidget.value);
                            }
                        })
                        .catch(err => {
                            console.error("Error fetching video directories:", err);
                        });
                });
            };
        }
    }
});