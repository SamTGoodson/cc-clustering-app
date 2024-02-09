window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(feature, context) {
            const {
                num_clusters,
                colorscale,
                style
            } = context.hideout; // get properties from hideout
            const value = feature.properties.h_cluster; // get the cluster number
            for (let i = 0; i < num_clusters; ++i) { // iterate over the number of clusters
                if (value === i + 1) { // compare with the cluster index
                    style.fillColor = colorscale[i]; // set the fill color according to the index
                    break; // break after setting the color
                }
            }
            // Debugging log
            console.log('Feature ID: ' + feature.id + ', Cluster: ' + value + ', Color: ' + style.fillColor);
            return style;
        }
    }
});