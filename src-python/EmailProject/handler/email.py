from flask import jsonify
from dao.email import EmailDAO;
from marshmallow import Schema, fields, ValidationError
import json



class EmailSchema(Schema):
    subject = fields.String(required=True)
    raw_content = fields.String(required=True)
    to = fields.List(fields.String(),required=True)

class EmailCategorySchema(Schema):
    category = fields.String(required=True)

class EmailDeleteSchema(Schema):
    id_email = fields.Int(required=True)

class EmailUpdateSchema(Schema):
    subject = fields.String(required=True)
    raw_content = fields.String(required=True)
    id_email = fields.Int(required=True)




class EmailHandler:

    def build_email_dict(self, row):
        result = {}
        result['id_email'] = row[0]
        result['subject'] = row[1]
        result['raw_content'] = row[2]
        result['to'] = row[3]
        return result

    def build_inbox_dict(self, row):
        result = {}
        result['id_email'] = row[0]
        result['subject'] = row[1]
        result['date_sended'] = row[2]
        result['id_user_from'] = row[3]
        result['from'] = row[4]
        result['friendship'] = row[5]
        if row[6] is None:
            result['categories'] = [];
        else:
            result['categories'] = row[6].split(",");
        result['is_readed'] = row[7]

        return result

    def build_outbox_dict(self, row):
        result = {}
        result['id_email'] = row[0]
        result['subject'] = row[1]
        result['date_sended'] = row[2]
        result['to'] = row[3].split(",");
        return result

    def build_email_view_dict(self, row):
        result = {}
        result['id_email'] = row[0]
        result['subject'] = row[1]
        result['date_sended'] = row[2]
        result['to'] = row[3].split(",")
        result['raw_content'] = row[4]
        result['from'] = row[5]
        return result



    def createEmail(self,json_data,id_user):
        schema = EmailSchema()
        try:
            result = schema.load(json_data)
        except ValidationError as err:
            return jsonify(err.messages), 400

        subject = json_data['subject']
        raw_content = json_data['raw_content']
        to = (json_data['to'])
        if len(to) < 1:
            return jsonify("No email addresses to send"), 400

        dao = EmailDAO()
        try:
            (id_email) = dao.createEmail(subject, raw_content, to, id_user)
            result = self.build_email_dict((id_email, subject, raw_content, json_data['to']))
            return jsonify(Email=result), 201
        except ValueError as err:
            return jsonify(str(err)), 409

    def retreiveInbox(self, id_user):
        dao = EmailDAO()
        result_dao = dao.retreiveInbox(id_user)
        result_list = []
        for row in result_dao:
            result = self.build_inbox_dict(row)
            result_list.append(result)
        return jsonify(Inbox=result_list)

    def searchInbox(self, id_user,field,value):
        if field is not None and (field == 'category' or field == 'email' ):
                if value is None:
                    return jsonify("Query param 'value' expected"), 400
                value = "%"+value+"%"
                dao = EmailDAO()
                result_dao = dao.searchInbox(id_user,field,value)
                result_list = []
                for row in result_dao:
                    result = self.build_inbox_dict(row)
                    result_list.append(result)
                return jsonify(Inbox=result_list)
        else:
            return jsonify("Query param 'field' expects: 'category' or 'to'"), 400

    def retreiveOutbox(self, id_user):
        dao = EmailDAO()
        result_dao = dao.retreiveOutbox(id_user)
        result_list = []
        for row in result_dao:
            result = self.build_outbox_dict(row)
            result_list.append(result)
        return jsonify(Outbox=result_list)


    def searchOutbox(self, id_user,field,value):
        if field is not None and (field == 'email' ):
                if value is None:
                    return jsonify("Query param 'value' expected"), 400
                value = "%"+value+"%"
                dao = EmailDAO()
                result_dao = dao.searchOutbox(id_user,field,value)
                result_list = []
                for row in result_dao:
                    result = self.build_outbox_dict(row)
                    result_list.append(result)
                return jsonify(Inbox=result_list)
        else:
            return jsonify("Query param 'field' expects: 'category' or 'to'"), 400





    def setCategoryEmail(self,id_user,id_email,json):
        schema = EmailCategorySchema()
        try:
            result = schema.load(json)
        except ValidationError as err:
            return jsonify(err.messages), 400
        dao = EmailDAO()
        result = dao.setCategoryEmail(id_user,id_email,json['category'])
        return jsonify(Categories=result)

    def deleteInbox(self, id_user, email_data):
        schema = EmailDeleteSchema()
        try:
            result = schema.load(email_data)
        except ValidationError as err:
            return jsonify(err.messages), 400
        id_email = email_data['id_email']
        dao = EmailDAO()
        try:
            dao.deleteInbox(id_user, id_email)
            return jsonify("Email deleted"), 204
        except ValueError as err:
            return jsonify(str(err)), 409

    def deleteOutbox(self, id_user, email_data):
        schema = EmailDeleteSchema()
        try:
            result = schema.load(email_data)
        except ValidationError as err:
            return jsonify(err.messages), 400
        id_email = email_data['id_email']
        dao = EmailDAO()
        try:
            dao.deleteOutbox(id_user, id_email)
            return jsonify("Email deleted"), 204
        except ValueError as err:
            return jsonify(str(err)), 409

    def updateOutbox(self, id_user, email_data):
        schema = EmailUpdateSchema()
        try:
            result = schema.load(email_data)
        except ValidationError as err:
            return jsonify(err.messages), 400
        subject = email_data['subject']
        raw_content = email_data['raw_content']
        id_email = email_data['id_email']
        dao = EmailDAO()
        try:
            email_info = dao.updateOutbox(id_user, id_email,subject,raw_content)
            print("Email updated",email_info)
            email_info_response = self.build_email_view_dict(email_info)
            return jsonify(Email=email_info_response), 200
        except ValueError as err:
            return jsonify(str(err)), 409

    def viewInboxEmail(self, id_user, id_email):
        dao = EmailDAO()
        try:
            email_info = dao.viewInboxEmail(id_user, id_email)
            email_info_response = self.build_email_view_dict(email_info)
            return jsonify(Email=email_info_response), 200
        except ValueError as err:
            return jsonify(str(err)), 409










