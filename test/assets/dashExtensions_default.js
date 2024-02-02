window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(feature, context) {
            const value = feature.properties.h_cluster; // get h_cluster value
            let color = '#FFEDA0'; // default color
            // Define colors based on h_cluster value
            if (value === 1) {
                color = '#FED976';
            } else if (value === 2) {
                color = '#FC4E2A';
            } // Add more conditions as needed
            return {
                ...context.hideout.style,
                fillColor: color
            }; // return the style
        },
        function1: function(feature) {
            const h_cluster = feature.properties.h_cluster;
            let color = '#FFEDA0'; // Default color

            if (h_cluster === 1) {
                color = '#FED976'; // Color for h_cluster 1
            } else if (h_cluster === 2) {
                color = '#FC4E2A'; // Color for h_cluster 2
            } // Add more conditions as needed

            return {
                fillColor: color,
                weight: 1,
                opacity: 1,
                color: 'black',
                fillOpacity: 0.7
            };
        },
        function2: function(feature, context) {
            const h_cluster = feature.properties.h_cluster;
            const colors = context.hideout.colors;
            const numClusters = context.hideout.numClusters;
            let color = colors[h_cluster % numClusters]; // Use modulo to wrap around the color palette

            return {
                fillColor: color,
                weight: 1,
                opacity: 1,
                color: 'black',
                fillOpacity: 0.7
            };
        },
        function3: function(feature, context) {
            const {
                num_clusters,
                colorscale,
                style,
                colorProp
            } = context.hideout; // get props from hideout
            const value = feature.properties[colorProp]; // get value the determines the color
            for (let i = 0; i < num_clusters; ++i) {
                if (value > classes[i]) {
                    style.fillColor = colorscale[i]; // set the fill color according to the class
                }
            }
            return style;
        },
        function4: function(feature, context) {
            const {
                num_clusters,
                colorscale,
                style,
                colorProp
            } = context.hideout; // get props from hideout
            const value = feature.properties[colorProp]; // get value the determines the color
            for (let i = 0; i < num_clusters; ++i) {
                if (value > num_clusters[i]) {
                    style.fillColor = colorscale[i]; // set the fill color according to the class
                }
            }
            return style;
        },
        function5: function(feature, context) {
            const {
                num_clusters,
                colorscale,
                style
            } = context.hideout; // get props from hideout
            const colorProp = feature.properties.h_cluster;
            const value = feature.properties[colorProp]; // get value the determines the color
            for (let i = 0; i < num_clusters; ++i) {
                if (value > num_clusters[i]) {
                    style.fillColor = colorscale[i]; // set the fill color according to the class
                }
            }
            return style;
        },
        function6: function(feature, context) {
            const {
                num_clusters,
                colorscale,
                style
            } = context.hideout; // get props from hideout
            const value = feature.properties.h_cluster;
            for (let i = 0; i < num_clusters; ++i) {
                if (value === num_clusters[i]) {
                    style.fillColor = colorscale[i]; // set the fill color according to the class
                }
            }
            return style;
        },
        function7: function(feature, context) {
            const {
                colorscale,
                style
            } = context.hideout; // get colorscale and style from hideout
            const value = feature.properties.h_cluster; // get the cluster number
            for (let i = 0; i < colorscale.length; ++i) {
                if (value === i) { // compare with index
                    style.fillColor = colorscale[i]; // set the fill color according to the index
                    break; // break after setting the color
                }
            }
            return style;
        },
        function8: function(feature, context) {
            const {
                num_clusters,
                colorscale,
                style
            } = context.hideout; // get properties from hideout
            const value = feature.properties.h_cluster; // get the cluster number
            for (let i = 0; i < num_clusters; ++i) { // iterate over the number of clusters
                if (value === i) { // compare with the cluster index
                    style.fillColor = colorscale[i]; // set the fill color according to the index
                    break; // break after setting the color
                }
            }
            // Debugging log
            console.log('Feature ID: ' + feature.id + ', Cluster: ' + value + ', Color: ' + style.fillColor);
            return style;
        },
        function9: function(feature, latlng) {
            return {
                weight: 5,
                color: '#666',
                dashArray: ''
            };
        }
    }
});