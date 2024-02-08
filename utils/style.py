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
    const {num_clusters, colorscale, style} = context.hideout; // get properties from hideout
    let value = feature.properties.h_cluster; // get the cluster number
    // Ensure 'value' is treated as a number for accurate comparison
    value = Number(value);

    console.log(`Preparing to assign color. Cluster value: ${value}, Number of clusters: ${num_clusters}`);

    for (let i = 0; i < num_clusters; ++i) { // iterate over the number of clusters
        console.log(`Comparing cluster value ${value} with index ${i}`); // Log directly before comparison

        if (value === i + 1) { // compare with the cluster index
            if (colorscale[i]) { // Check if colorscale entry exists
                style.fillColor = colorscale[i]; // set the fill color according to the index
                console.log(`Assigning color for cluster ${value}: colorscale[${i}] = ${colorscale[i]}`); // Log color assignment
            } else {
                console.log(`No color defined for cluster ${value}`); // Log if no color is defined for this cluster index
            }
            break; // Exit the loop once the color is assigned
        }
    }

    // Log feature details including the district name, number, cluster, and the assigned color
    console.log(`Feature ID: ${feature.id}, District Name: ${feature.properties.OfficeRecordFullName}, District Number: ${feature.properties.District}, Cluster: ${value}, Color: ${style.fillColor}`);
    return style; // Return the style object with the fillColor property set
}""")

