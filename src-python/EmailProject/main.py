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
@app.route('/404/user/create', methods=['POST'])
def insertNewUser():
    print("REQUEST: ", request.json)
    user_data = request.json
    return UserHandler().insertUser(user_data);

@app.route('/404/user/<int:id_user>/friend/add', methods=['POST'])
def addFriend(id_user):
    print("REQUEST: ", request.json)
    user_data = request.json
    return UserHandler().addFriend(id_user,user_data);

@app.route('/404/user/<int:id_user>/friend/remove', methods=['POST'])
def removeFriend(id_user):
    print("REQUEST: ", request.json)
    user_data = request.json
    return UserHandler().removeFriend(id_user,user_data);


@app.route('/404/user/getallusers', methods=['GET'])
def users_handler():
    if request.method == 'GET':
        return UserHandler().getAllUsers()
    else:
        return jsonify("Not Supported"), 405


@app.route('/404/user/<int:id_user>', methods=['GET'])
def user_by_id_handler(id_user):
    if request.method == 'GET':
        return UserHandler().getUserbyId(id_user)
    else:
        return jsonify("Not Supported"), 405

@app.route('/404/user/top10usersinbox', methods=['GET'])
def top10inbox_handler():
    if request.method == 'GET':
        return UserHandler().viewTop10UsersWithMoreEmailsOnInbox()
    else:
        return jsonify("Not Supported"), 405

@app.route('/404/user/top10usersoutbox', methods=['GET'])
def top10outbox_handler():
    if request.method == 'GET':
        return UserHandler().viewTop10UsersWithMoreEmailsOnOutbox()
    else:
        return jsonify("Not Supported"), 405

# END USER SERVICES

# EMAIL SERVICES

@app.route('/404/user/<int:id_user>/email/send', methods=['POST'])
def createNewEmail(id_user):
    print("REQUEST: ", request.json)
    email_data = request.json
    return EmailHandler().createEmail(email_data,id_user);

@app.route('/404/user/<int:id_user>/email/inbox', methods=['GET'])
def retreiveInbox(id_user):
    return EmailHandler().retreiveInbox(id_user);

@app.route('/404/user/<int:id_user>/email/inbox/search', methods=['GET'])
def searchInbox(id_user):
    args = request.args;
    field = args.get("field", default=None, type=str)
    value = args.get("value", default=None, type=str)
    return EmailHandler().searchInbox(id_user,field,value);


@app.route('/404/user/<int:id_user>/email/<int:id_email>/setcategory', methods=['POST'])
def setCategory(id_user,id_email):
    json = request.json
    return EmailHandler().setCategoryEmail(id_user,id_email,json);


@app.route('/404/user/<int:id_user>/email/outbox', methods=['GET'])
def retreiveOutbox(id_user):
    return EmailHandler().retreiveOutbox(id_user);


@app.route('/404/user/<int:id_user>/email/outbox/search', methods=['GET'])
def searchOutbox(id_user):
    args = request.args;
    field = args.get("field", default=None, type=str)
    value = args.get("value", default=None, type=str)
    return EmailHandler().searchOutbox(id_user,field,value);

@app.route('/404/user/<int:id_user>/email/inbox/delete', methods=['POST'])
def deleteInbox(id_user):
    email_delete = request.json
    return EmailHandler().deleteInbox(id_user,email_delete);

@app.route('/404/user/<int:id_user>/email/outbox/delete', methods=['POST'])
def deleteOutbox(id_user):
    email_delete = request.json
    return EmailHandler().deleteOutbox(id_user,email_delete);

@app.route('/404/user/<int:id_user>/email/outbox/update', methods=['POST'])
def updateOutbox(id_user):
    email_update = request.json
    return EmailHandler().updateOutbox(id_user,email_update);

@app.route('/404/user/<int:id_user>/email/inbox/<int:id_email>', methods=['GET'])
def viewInboxEmail(id_user,id_email):
    return EmailHandler().viewInboxEmail(id_user,id_email);

@app.route('/404/user/<int:id_user>/email/outbox/<int:id_email>', methods=['GET'])
def viewInboxOutbox(id_user,id_email):
    return EmailHandler().viewOutboxEmail(id_user,id_email);



@app.route('/404/user/<int:id_user>/email/inbox/<int:id_email>/reply', methods=['POST'])
def replyEmail(id_user,id_email):
    print("REQUEST: ", request.json)
    email_data = request.json
    return EmailHandler().createEmailReply(id_user,id_email,email_data);

@app.route('/404/email/getallemails', methods=['GET'])
def emails_handler():
    if request.method == 'GET':
        return EmailHandler().getAllEmails()
    else:
        return jsonify("Not Supported"), 405


@app.route('/404/email/<int:id_email>', methods=['GET'])
def email_by_id_handler(id_email):
    if request.method == 'GET':
        return EmailHandler().getEmailbyId(id_email)
    else:
        return jsonify("Not Supported"), 405

@app.route('/404/email/mostrecipients', methods=['GET'])
def recipients_handler():
    if request.method == 'GET':
        return EmailHandler().viewEmailMostRecipients()
    else:
        return jsonify("Not Supported"), 405

@app.route('/404/email/mostreplies', methods=['GET'])
def replies_handler():
    if request.method == 'GET':
        return EmailHandler().viewEmailMostReplies()
    else:
        return jsonify("Not Supported"), 405

# END EMAIL SERVICES

if __name__ == '__main__':
    app.run()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
