from flask import Flask, session, render_template, request, redirect, url_for, flash, jsonify
import utils
from flask_mail import Mail, Message
import json

app = Flask(__name__, static_url_path="/static", static_folder='static')
app.secret_key = "super secret key"
app.config['MAIL_SERVER']='sandbox.smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = '39d9715821bda1'
app.config['MAIL_PASSWORD'] = '5d452e5ec20435'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail_object = Mail(app)

@app.route("/")
def index():
    return render_template("index.html")
    
    
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle POST request
        form_data = [x for x in request.form.values()]
         
        # store data to database
        if utils.check_login(form_data):
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            message = "invalid email or password!"
            return render_template("login.html", message=message)
    
    return render_template("login.html")
    
 
@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Handle POST request
        form_data = [x for x in request.form.values()]
        
        # store data to database
        user_id = utils.store_register_data(form_data)  
        
        session['logged_in'] = True
        session['user_name'] = form_data[0]
        session['user_id'] = user_id
        
        return redirect(url_for('index'))
    
    return render_template("register.html")
    

@app.route("/email_validation", methods=['GET'])
def email_validation():
    email = request.args.get('email')
    return jsonify({'valid': utils.email_validation(email)})
    
    
@app.route("/logout", methods=['GET'])
def logout():  
    session.clear()
    return redirect(url_for('index'))
    
    
@app.route("/forget_password", methods=['GET', 'POST'])
def forget_password():  
    if request.method == 'POST':
        if utils.forget_password(request.form['email'], mail_object):
            message = "A password reset link has been sent to your email."
            return render_template('forget_password.html', success_message=message)  
        else:
            message = "Invalid Email."
            return render_template('forget_password.html', message=message)  
        
    return render_template('forget_password.html')
    
    
@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    
    if not utils.reset_password_token_verify(token):
        flash('Invalid or expired token.', 'error')
        return redirect(url_for('forget_password'))
    
    if request.method == 'POST':
        utils.reset_password(request.form['password'], token)
        return redirect(url_for('login'))
    
    return render_template("reset_password.html", token=token)


@app.route("/user_profile", methods=['GET'])
def user_profile():
    user_data = utils.auth_user_data()
    return render_template("user_profile.html", user_data=user_data)
    

@app.route("/edit_profile", methods=['GET', 'POST'])
def edit_profile():
    if request.method == 'POST':
            
        form_data = [x for x in request.form.values()]
        utils.update_user(form_data)
        
        return redirect(url_for('user_profile'))
    
    user_data = utils.auth_user_data()
    return render_template("edit_profile.html", user_data=user_data)


@app.route("/email_validation_for_update", methods=['GET'])
def email_validation_for_update():
    email = request.args.get('email')
    return jsonify({'valid': utils.email_validation_for_update(email)})


@app.route("/delete_profile", methods=['GET'])
def delete_profile():
    if utils.delete_user_data(mail_object):
        session.clear()
        return redirect(url_for('index'))
    
    return redirect(url_for('user_profile'))
    

@app.route("/revoke_delete_user/<user_id>/<email>", methods=['GET'])
def revoke_delete_user(user_id, email):
    if utils.revoke_delete_user(user_id, email):
        return redirect(url_for('login'))
    else:
        return redirect(url_for('register'))
   

@app.route("/map", methods=['GET', 'POST'])
def map():    
    favorite_facility = utils.fetch_favorite_facility()
    home_address = utils.fetch_user_home_address()
    
    return render_template("map.html", favorite_facility_id=favorite_facility[0],favorite_facility_collection =favorite_facility[1], home_address=home_address)


@app.route("/map-json-data", methods=['GET'])
def map_json_data():
    facility = request.args.getlist('type')
    
    data = utils.fetch_all_map_points(facility)
    
    favorite_facility = utils.fetch_favorite_facility() 
    
    # data['favorite_facility_id'] = favorite_facility[0]
    # data['favorite_facility_collection'] = favorite_facility[1]
    
    return jsonify({ 'data': data, 'favorite_facility_id': favorite_facility[0], 'favorite_facility_collection': favorite_facility[1] })
    
    

@app.route("/mark-as-favorite-facility/<facility_id>/<facility_name>", methods=["POST"])
def mark_as_favorite_facility(facility_id, facility_name):
    
    data = utils.mark_as_favorite_facility(facility_id, facility_name)
    return data
    

@app.route("/remove-as-favorite-facility/<facility_id>/<facility_name>", methods=["GET" ,"POST"])
def remove_as_favorite_facility(facility_id, facility_name):
    
    data = utils.remove_as_favorite_facility(facility_id, facility_name)
    return data
    
    
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")