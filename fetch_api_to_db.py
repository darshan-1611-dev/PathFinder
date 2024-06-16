import requests
from utils import db, SCHOOLS_DATA_COLLECTION, KINDERGARDEN_DATA_COLLECTION, SOCIAL_CHILD_PROJECTS_DATA_COLLECTION, SOCIAL_TEENAGER_DATA_COLLECTION

SCHOOLS = 'SCHOOLS'
KINDERGARDEN = 'KINDERGARDEN'
SOCIAL_CHILD_PROJECTS = 'SOCIAL_CHILD_PROJECTS'
SOCIAL_TEENAGER_PROJECTS = 'SOCIAL_TEENAGER_PROJECTS'

SCHOOL_DATA_API_ENDPOINT = "https://services6.arcgis.com/jiszdsDupTUO3fSM/arcgis/rest/services/Schulen_OpenData/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson"

KINDERGARDEN_API_ENDPOINT = "https://services6.arcgis.com/jiszdsDupTUO3fSM/arcgis/rest/services/Kindertageseinrichtungen_Sicht/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson"

SOCIAL_CHILD_PROJECTS_API_ENDPOINT ="https://services6.arcgis.com/jiszdsDupTUO3fSM/arcgis/rest/services/Schulsozialarbeit_FL_1/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson"

SOCIAL_TEENAGER_PROJECTS_API_ENDPOINT ="https://services6.arcgis.com/jiszdsDupTUO3fSM/arcgis/rest/services/Jugendberufshilfen_FL_1/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson"


def transform_to_lowercase(data):
    return {k.lower(): v for k, v in data if k != 'ID'}
    

def fetch_data(API_ENDPOINT):
    response = requests.get(API_ENDPOINT) 
    return response.json()
    

def generate_dic_data_for_db(response_data, data_about):
    
    data_dic = []
    
    for data in response_data['features']:
        data_dic.append(
            {'id' : data['id'],
            'dataAbout': data_about,
            'lat': data["geometry"]["coordinates"][1],
            'lng': data["geometry"]["coordinates"][0],
            **transform_to_lowercase(data['properties'].items())
            })
            
    return data_dic


def fetch_and_insert_data_to_db(api_endpoint, collection_name, data_about):
    
    # delete data from database for new data points
    db[collection_name].delete_many({})
    
    response_data = fetch_data(api_endpoint)  # fetch data from API
    
    # generate dic data from API response
    result_dic_data = generate_dic_data_for_db(response_data, data_about)  
    
    # insert data into database
    result = db[collection_name].insert_many(result_dic_data)

    print(f"{data_about} Data is inserted with total rows {len(result.inserted_ids)}")
    

def main():
    
    # schools 
    fetch_and_insert_data_to_db(SCHOOL_DATA_API_ENDPOINT, SCHOOLS_DATA_COLLECTION, SCHOOLS)
    
    # kindergarden
    fetch_and_insert_data_to_db(KINDERGARDEN_API_ENDPOINT, KINDERGARDEN_DATA_COLLECTION, KINDERGARDEN)
    
    # social child projects
    fetch_and_insert_data_to_db(SOCIAL_CHILD_PROJECTS_API_ENDPOINT, SOCIAL_CHILD_PROJECTS_DATA_COLLECTION, SOCIAL_CHILD_PROJECTS)

    # social teenager projects
    fetch_and_insert_data_to_db(SOCIAL_TEENAGER_PROJECTS_API_ENDPOINT, SOCIAL_TEENAGER_DATA_COLLECTION, SOCIAL_TEENAGER_PROJECTS)

if __name__ == '__main__':
    main()