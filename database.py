import pymongo
import bcrypt

# specification of database
CONNECTION_STRING = "mongodb://localhost:27017/"
CURRENT_DATABASE = "pathFinderDB"

# collection names
USERS_COLLECTION = "users"

myclient = pymongo.MongoClient(CONNECTION_STRING)  # connect to the mongoDB
    
db = myclient[CURRENT_DATABASE]  # connect to the Database

"""
Connect to the mongoDb
"""
def get_db():
    myclient = pymongo.MongoClient(CONNECTION_STRING)  # connect to the mongoDB
    
    return myclient[CURRENT_DATABASE]  # connect to the Database
    
"""
Encrypt Password
"""
def password_hashing(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
"""
Store Registraion Data into the database
"""
def store_register_data(form_data):

    columns = ['firstName', 'lastName', 'dateOfBitrh', 'role', 'email', 'password']
    
    # bcrypt.checkpw(password.encode('utf-8'), user['password'])
    form_data[-1] = password_hashing(form_data[-1])  # encrypt password
    insert_data = dict(zip(columns, form_data))

    print(insert_data)
    
    db_collection = db[USERS_COLLECTION]
    
    db_collection.insert_one(insert_data)
    
    
"""
Check Login Credential
"""
def check_login(form_data):
    
    email = form_data[0]
    password = form_data[1]
    
    db_collection = db[USERS_COLLECTION]
    db_user_data = db_collection.find_one({"email": email})
        
    if db_user_data and bcrypt.checkpw(password.encode('utf-8'), db_user_data['password']):
        return True
    else:
        return False
    
    