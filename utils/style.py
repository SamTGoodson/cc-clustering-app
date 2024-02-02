from dash_extensions.javascript import assign,arrow_function
from matplotlib import pyplot as plt


def generate_colorscale(num_clusters, geojson_data):
    cmap = plt.get_cmap('tab20')
    colorscale = [
        "rgba({},{},{},{})".format(int(r * 255), int(g * 255), int(b * 255), a)
        for r, g, b, a in (cmap(i / num_clusters) for i in range(num_clusters))
    ]
    return colorscale

style_handle = assign("""function(feature, context){
    const {num_clusters, colorscale, style} = context.hideout;  // get properties from hideout
    const value = feature.properties.h_cluster;   // get the cluster number
    for (let i = 0; i < num_clusters; ++i) {      // iterate over the number of clusters
        if (value === i) {                        // compare with the cluster index
            style.fillColor = colorscale[i];      // set the fill color according to the index
            break;                                // break after setting the color
        }
    }
    // Debugging log
    console.log('Feature ID: ' + feature.id + ', Cluster: ' + value + ', Color: ' + style.fillColor);
    return style;
}""")
