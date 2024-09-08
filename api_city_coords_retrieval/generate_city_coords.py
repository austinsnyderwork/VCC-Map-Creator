import pandas as pd
import requests


cities_file_path = "C:/Users/austisnyder/programming/programming_i_o_files/resources/all_worksite_cities.csv"
cities_df = pd.read_csv(cities_file_path)

subscription_key = '3pg63za6h9pgEr5EyONLcWBpVsyRAGYoxP5dPv6gMeoNJ27G0J5ZJQQJ99AIACYeBjFNuXIHAAAgAZMPRRNZ'
endpoint_url = 'https://atlas.microsoft.com/search/address/json'

city_coords = {
    'city': [],
    'latitude': [],
    'longitude': []
}


def get_city_coords(row):
    api_input_name = f"{row['City']}, {row['State']}"

    output_name = api_input_name.replace(', IA', '')

    params = {
        'subscription-key': subscription_key,
        'api-version': '1.0',
        'query': api_input_name
    }

    # Make the request to Azure Maps
    response = requests.get(endpoint_url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        # Extract the first result from the response
        if 'results' in data and len(data['results']) > 0:
            first_result = data['results'][0]
            coordinates = first_result['position']
            city_coords['city'].append(output_name)
            city_coords['latitude'].append(coordinates['lat'])
            city_coords['longitude'].append(coordinates['lon'])
        else:
            print(f"No results found for {api_input_name}.")
    else:
        print(f"Error: {response.status_code}")


cities_df.apply(get_city_coords, axis=1)

df = pd.DataFrame(city_coords)
df.to_csv("C:/Users/austisnyder/programming/programming_i_o_files/vcc_maps/city_coords.csv")



