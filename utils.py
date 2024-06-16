import pymongo
import bcrypt
from flask_mail import Mail, Message
import secrets
from datetime import datetime, timedelta
from flask import url_for, flash, render_template_string, session
from reset_password_email_template import reset_password_mail_template 
from account_revoke_email_template import account_revoke_mail_template 
import random


#Mail Sender 
MAIL_SENDER = "pathfinder@gmail.com"
FORGET_PASSWORD_EXPIRY_HOURS = 1

# specification of database
CONNECTION_STRING = "mongodb://localhost:27017/"
CURRENT_DATABASE = "pathFinderDB"

# collection names
USERS_COLLECTION = "users"
RESET_TOKENS_COLLECTION = "reset_tokens"
SCHOOLS_DATA_COLLECTION = "schools"
KINDERGARDEN_DATA_COLLECTION = "kindergarden"
SOCIAL_CHILD_PROJECTS_DATA_COLLECTION = "social_child_projects"
SOCIAL_TEENAGER_PROJECTS_DATA_COLLECTION = "social_teenager_projects"

myclient = pymongo.MongoClient(CONNECTION_STRING)  # connect to the mongoDB
    
db = myclient[CURRENT_DATABASE]  # connect to the Database

"""
Connect to the mongoDb
"""
def get_db():
    myclient = pymongo.MongoClient(CONNECTION_STRING)  # connect to the mongoDB
    
    return myclient[CURRENT_DATABASE]  # connect to the Database
   
   
"""    
Function to generate a random numeric ID
"""
def generate_numeric_id(length=5):
    range_start = 10**(length-1)
    range_end = (10**length) - 1
    return random.randint(range_start, range_end)
    
    
"""
Check Unique id exists or not
"""
def id_exists(new_id):
    return db[USERS_COLLECTION].find_one({'_id': new_id}) is not None
    
    
"""
Function to generate a unique numeric ID
"""
def generate_unique_numeric_id(length=5):
    new_id = generate_numeric_id(length)
    while id_exists(new_id):
        new_id = generate_numeric_id(length)
    return new_id
    
    
"""
Encrypt Password
"""
def password_hashing(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    
"""
Store Registraion Data into the database
"""
def store_register_data(form_data):

    columns = ['firstName', 'lastName', 'dateOfBirth', 'role', 'email', 'password', '_id']
    
    new_user_id = generate_unique_numeric_id()
    
    # bcrypt.checkpw(password.encode('utf-8'), user['password'])
    form_data[-1] = password_hashing(form_data[-1])  # encrypt password
    form_data.append(new_user_id)
    insert_data = dict(zip(columns, form_data))
    
    db_collection = db[USERS_COLLECTION]
    
    db_collection.insert_one(insert_data)
    
    return new_user_id
   
    
    
"""
Check Login Credential
"""
def check_login(form_data):
    
    email = form_data[0]
    password = form_data[1]
    
    db_collection = db[USERS_COLLECTION]
    
    db_user_data = db_collection.find_one({ "$and": [ 
    {"email": email},
    { "deleted_at": { "$exists": False } }
    ]})
        
    if db_user_data and bcrypt.checkpw(password.encode('utf-8'), db_user_data['password']):
        session['user_id'] = db_user_data['_id']
        session['user_name'] = db_user_data['firstName']
        return True
    else:
        return False
    
    
"""
Forget Password
"""
def forget_password(email, mail_object):
    
    db_collection = db[USERS_COLLECTION]
    db_user_email = db_collection.find_one({ "$and": [ 
    {"email": email},
    { "deleted_at": { "$exists": False } }
    ]})
    
    if db_user_email:
        token = secrets.token_urlsafe(16)
        
        db[RESET_TOKENS_COLLECTION].insert_one({'email': email, 'token': token, 'expires_at': datetime.utcnow() + timedelta(hours=FORGET_PASSWORD_EXPIRY_HOURS)})
        
        # Send the email with the reset link
        reset_link = url_for('reset_password', token=token, _external=True)
        msg = Message('Password Reset Request', sender=MAIL_SENDER, recipients=[email])
        
        html_body = render_template_string(reset_password_mail_template, reset_link=reset_link)
        
        msg.html = html_body
        mail_object.send(msg)
           
        return True
    else:
        return False
        
"""
reset password token verify
"""        
def reset_password_token_verify(token):
    token_record = db[RESET_TOKENS_COLLECTION].find_one({'token': token})
    
    if not token_record or token_record['expires_at'] < datetime.utcnow():
        flash('Invalid or expired token.', 'error')
        return False
    
    return True


"""
reset Password
"""
def reset_password(new_password, token):
    token_record = db[RESET_TOKENS_COLLECTION].find_one({'token': token})
    hashed_password = password_hashing(new_password)
        
    # Update the user's password in the database
    db[USERS_COLLECTION].update_one({'email': token_record['email']}, {'$set': {'password': hashed_password}})
        
    # Remove the token from the database
    db[RESET_TOKENS_COLLECTION].delete_one({'token': token})
       
    return True 
   
   
"""
Email Validation    
"""
def email_validation(email):
    db_user_email = db[USERS_COLLECTION].find_one({"email": email})
    
    if not db_user_email:
        return True
    
    return False
    

"""
Fetch User Profile
"""
def auth_user_data():
    return db[USERS_COLLECTION].find_one({ "$and": [ 
    {"_id": session['user_id']},
    { "deleted_at": { "$exists": False } }
    ]})
    

"""
Update User
"""
def update_user(form_data):
    # Construct update data dictionary
    update_data = {
        'firstName': form_data[0],
        'lastName': form_data[1],
        'dateOfBirth': form_data[2],
        'role': form_data[3],
        'email': form_data[4],
        'password': form_data[5]
    }
    
    # Remove empty password field if it exists
    if update_data['password'] == '':
        del update_data['password']
    else:
        update_data['password'] = password_hashing(update_data['password'])
    
    # Perform database update
    db[USERS_COLLECTION].update_one({'_id': session['user_id']}, {'$set': update_data})

"""
Email Validation for Update
"""
def email_validation_for_update(email):
    query = {"email": email, "_id": {"$ne": session['user_id']}}
    result  = db[USERS_COLLECTION].find_one(query)
    if not result:
        return True
    
    return False
    

"""
Delete Profile
"""
def delete_user_data(mail_object):
    user_id = session['user_id']
    
    result = db[USERS_COLLECTION].update_one({'_id': user_id}, {'$set': {'deleted_at': datetime.utcnow()}})
    
    if result.modified_count > 0:
        # Send email to the user with a link to revoke deletion
        send_revocation_email(user_id, mail_object)
        return True
    else:
        flash("User not found or already deleted.")
        return False
        

"""
Send revocation mail
"""
def send_revocation_email(user_id, mail_object):

    user_data = db[USERS_COLLECTION].find_one({'_id': user_id})

    # Construct revocation link
    revocation_link = url_for('revoke_delete_user', user_id=user_id, email=user_data['email'], _external=True)

    msg = Message("Account Deletion Confirmation", sender=MAIL_SENDER, recipients=[user_data['email']])
    
    html_body = render_template_string(account_revoke_mail_template, revocation_link=revocation_link, first_name=user_data['firstName'])
        
    msg.html = html_body
    
    mail_object.send(msg)
    
    
"""
Revoke Deleted User
"""
def revoke_delete_user(user_id, email):
    result = db[USERS_COLLECTION].update_one({'email': email}, {'$unset': {'deleted_at': ''}})
    print("Modified Count:", result.modified_count) 
    if result.modified_count > 0:
        return True
    else:
        flash("Something went wrong with revoking the user account. Please register a new one.")
        return False
    
    
"""
Fetch all map points from DB
"""
def fetch_all_map_points(facility_types):
    COLLECTIONS_FOR_MAP_POINTS = {
    "schools": SCHOOLS_DATA_COLLECTION,
    "kindergarden": KINDERGARDEN_DATA_COLLECTION,
    "social_child_projects": SOCIAL_CHILD_PROJECTS_DATA_COLLECTION,
    "social_teenager_projects": SOCIAL_TEENAGER_PROJECTS_DATA_COLLECTION
    }

    if facility_types:
        
        data = {}
        
        for facility in facility_types:
            if facility in COLLECTIONS_FOR_MAP_POINTS:
                data[facility] = list(db[COLLECTIONS_FOR_MAP_POINTS[facility]].find({}, {'_id': 0}))
        
        return data

    return []
  
  
def mark_as_favorite_facility(facility_id, facility):
    user_id = session['user_id']
    facility_id = int(facility_id)
    facility = str(facility)
    
    # update facility table 
    # db[facility].update_one({'id': facility_id}, {'$addToSet': { 'user_favorite': user_id }})

    # update user table
    db[USERS_COLLECTION].update_one({'_id': user_id}, {'$set': { 'facility_id': facility_id, 'facility_collection': facility }})

    session['favorite_facility_id'] = facility_id
    session['favorite_facility_collection'] = facility
    
    return db[facility].find_one({'id': facility_id}, {'lat':1, 'lng':1, '_id':0})
    
    
def remove_as_favorite_facility(facility_id, facility):
    user_id = session['user_id']
    
    # unset facility
    result = db[USERS_COLLECTION].update_one({'_id': user_id}, {'$unset': { 'facility_id': '', 'facility_collection': '' }})
    
    if result.modified_count > 0:
        return [True]
    else:
        flash("* Something went wrong with remove favorite facility. Please refresh the page.")
        return [False]
    

    
def fetch_favorite_facility():
    data = auth_user_data()
    
    if data.get("facility_id") and data.get("facility_collection"):
        return [
            data["facility_id"],
            data["facility_collection"]
            ]
    
        
    return [0, '']