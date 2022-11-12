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
        result['email'] = row[4]
        result['friendship'] = row[5]
        if row[6] is None:
            result['categories'] = [];
        else:
            result['categories'] = row[6].split(",");

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
            result = self.build_inbox_dict(row)
            result_list.append(result)
        return jsonify(Outbox=result_list)





    def setCategoryEmail(self,id_user,id_email,json):
        schema = EmailCategorySchema()
        try:
            result = schema.load(json)
        except ValidationError as err:
            return jsonify(err.messages), 400
        dao = EmailDAO()
        result = dao.setCategoryEmail(id_user,id_email,json['category'])
        return jsonify(Categories=result)










