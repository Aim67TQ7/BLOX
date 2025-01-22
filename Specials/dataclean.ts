import * as d3 from 'd3'; // Importing d3 for data manipulation.

interface DataFrame {
    [key: string]: any[];
}

/**
 * Clean and prepare the customer data.
 * @param df - DataFrame representing the customer data.
 */
function cleanData(df: DataFrame): DataFrame {
    // Standardize column names
    const columnMapping: { [key: string]: string } = {
        'lat': 'Latitude',
        'latitude': 'Latitude',
        'lon': 'Longitude',
        'longitude': 'Longitude',
        'phone': 'Phone',
        'territory': 'Territory',
        'sales_rep': 'Sales Rep',
        'prodcode': 'ProdCode',
        'state': 'State/Prov',
        'state/prov': 'State/Prov',
        'stateprov': 'State/Prov',
        'state/province': 'State/Prov',
        'name': 'Name',
        'company name': 'Name',
        'customer name': 'Name',
        '3-year spend': '3-year Spend',
        '3 year spend': '3-year Spend',
        'three year spend': '3-year Spend'
    };

    // Rename columns if they exist (case-insensitive)
    const renamedColumns = Object.keys(df).reduce((acc: DataFrame, key: string) => {
        const lowerKey = key.toLowerCase();
        const newKey = columnMapping[lowerKey] || key;
        acc[newKey] = df[key];
        return acc;
    }, {});

    // Filter rows with valid coordinates
    const filteredRows = renamedColumns.filter(
        (row: any) => row['Latitude'] && row['Longitude']
    );
}
