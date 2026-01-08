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


                node.previewImg = new Image();


                const origOnDrawBackground = node.onDrawBackground;
                node.onDrawBackground = function (ctx) {
                    origOnDrawBackground?.apply(this, arguments);

                    if (this.previewImg && this.previewImg.complete && this.previewImg.naturalWidth > 0) {
                        // Estimate where widgets end so we can draw below them
                        let top = 40; // Default header height approx
                        if (this.widgets) {
                            for (const w of this.widgets) {
                                if (w.last_y != null) {
                                    top = Math.max(top, w.last_y + (w.computeSize ? w.computeSize()[1] : 20));
                                }
                            }
                        }
                        top += 10; // Padding

                        const margin = 10;
                        const drawWidth = this.size[0] - (margin * 2);
                        
                        // Calculate height based on aspect ratio
                        const aspectRatio = this.previewImg.naturalHeight / this.previewImg.naturalWidth;
                        const drawHeight = drawWidth * aspectRatio;

                        // Draw the image
                        ctx.drawImage(this.previewImg, margin, top, drawWidth, drawHeight);
                    }
                };


                const updatePreview = () => {
                    const dirWidget = node.widgets.find(w => w.name === "directory");
                    const imgWidget = node.widgets.find(w => w.name === "image");

                    if (dirWidget && imgWidget && imgWidget.value) {
                         const subfolder = dirWidget.value;
                         const filename = imgWidget.value;
                         
                         // Construct URL for standard ComfyUI view endpoint
                         // timestamps used to prevent caching if the file is overwritten
                         const url = api.apiURL(`/view?filename=${encodeURIComponent(filename)}&subfolder=${encodeURIComponent(subfolder)}&type=output&t=${Date.now()}`);
                         
                         node.previewImg.src = url;
                         
                         node.previewImg.onload = () => {
                             // Resize node to fit image
                             // Simple estimation of widget area height
                             const widgetAreaHeight = (node.widgets?.length || 0) * 30 + 40; 
                             
                             const margin = 10;
                             const drawWidth = node.size[0] - (margin * 2);
                             const aspectRatio = node.previewImg.naturalHeight / node.previewImg.naturalWidth;
                             const drawHeight = drawWidth * aspectRatio;
                             
                             const totalHeight = widgetAreaHeight + drawHeight + 20;

                             // Only resize if the node is too small to fit the image
                             if (node.size[1] < totalHeight) {
                                 node.setSize([node.size[0], totalHeight]);
                             }
                             
                             node.setDirtyCanvas(true, true);
                         };
                    } else {
                        // Clear preview if no valid image selected
                        node.previewImg.removeAttribute("src");
                        node.setDirtyCanvas(true, true);
                    }
                };

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
                            

                            updatePreview();
                            
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


                const imgWidget = this.widgets.find(w => w.name === "image");
                if (imgWidget) {
                    imgWidget.callback = () => {
                        updatePreview();
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


                // Small delay to ensure widgets are initialized
                setTimeout(() => {
                    updatePreview();
                }, 100);
            };
        }
    }
});