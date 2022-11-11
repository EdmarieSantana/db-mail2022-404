from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from handler.user import UserHandler
from handler.email import EmailHandler


# Activate
app = Flask(__name__)
# Apply CORS to this app
CORS(app)



@app.route('/')
def greeting():
    return 'Hello, this is the Email DB App 404!'


# USER SERVICES
@app.route('/EmailApp/user/create', methods=['POST'])
def insertNewUser():
    print("REQUEST: ", request.json)
    user_data = request.json
    return UserHandler().insertUser(user_data);

@app.route('/EmailApp/user/<int:id_user>/friend/add', methods=['POST'])
def addFriend(id_user):
    print("REQUEST: ", request.json)
    user_data = request.json
    return UserHandler().addFriend(id_user,user_data);

@app.route('/EmailApp/user/<int:id_user>/friend/remove', methods=['POST'])
def removeFriend(id_user):
    print("REQUEST: ", request.json)
    user_data = request.json
    return UserHandler().removeFriend(id_user,user_data);


# END USER SERVICES

# EMAIL SERVICES

@app.route('/EmailApp/user/<int:id_user>/email/send', methods=['POST'])
def createNewEmail(id_user):
    print("REQUEST: ", request.json)
    email_data = request.json
    return EmailHandler().createEmail(email_data,id_user);

@app.route('/EmailApp/user/<int:id_user>/email/inbox', methods=['GET'])
def retreiveInbox(id_user):
    return EmailHandler().retreiveInbox(id_user);


# END USER SERVICES





if __name__ == '__main__':
    app.run()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
