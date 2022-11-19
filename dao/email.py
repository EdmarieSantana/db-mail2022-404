from conf.dbconfig import pg_config
import psycopg2


class EmailDAO:
    def __init__(self):

        connection_url = "dbname=%s user=%s password=%s host=%s" % (pg_config['dbname'],
                                                                    pg_config['user'],
                                                                    pg_config['passwd'],
                                                                    pg_config['host'])
        self.conn = psycopg2._connect(connection_url)

    #get all email in the table
    def getAllEmails(self):
        query = 'select * from "email" WHERE is_deleted_outbox = FALSE order by id_email asc;'
        cursor = self.conn.cursor()
        cursor.execute(query)
        result = []
        for row in cursor:
            print(row)
            result.append(row)
        cursor.close()
        return result

    #get email by id given
    def getEmailbyId(self, id_email):
        query = 'select * from "email" where id_email = %s AND is_deleted_outbox = FALSE;'
        cursor = self.conn.cursor()
        cursor.execute(query, (id_email,))
        return cursor.fetchone()

    # get all categories in the table
    def getAllEmailsCategories(self):
        query = 'select * from "category" WHERE is_deleted = FALSE order by id_category asc;'
        cursor = self.conn.cursor()
        cursor.execute(query)
        result = []
        for row in cursor:
            print(row)
            result.append(row)
        cursor.close()
        return result

    #get category by id given
    def getEmailCategorybyId(self, id_category):
        query = 'select * from "category" WHERE id_category = %s AND is_deleted = FALSE order by id_category asc'
        cursor = self.conn.cursor()
        cursor.execute(query, (id_category,))
        return cursor.fetchone()

    def createEmail(self, subject, raw_content, to, id_user):
        try:

            cursor = self.conn.cursor()
            query = "select id_user,email from \"user\" where email in %s;"
            cursor.execute(query, (tuple(to),))
            resultReceiver = []
            for row in cursor:
                resultReceiver.append(row)
            for receiver in to:
                founded = False
                for receiverBd in resultReceiver:
                    if receiverBd[1]==receiver:
                        founded=True
                        break
                if founded is False:
                    raise ValueError('The email doesn´t exits:'+receiver)



            try:
                query = "insert into \"email\"(subject, raw_content, date_sended,id_user_from)" \
                        " values (%s, %s,current_timestamp, %s) returning id_email;"
                cursor.execute(query, (subject, raw_content, id_user))
            except psycopg2.errors.lookup("23503"):
                raise ValueError('The id user doesn´t exits')

            id_email = cursor.fetchone()[0]

            for receiverBd in resultReceiver:
                query = "insert into \"receive\"(id_user, id_email)" \
                        " values (%s, %s);"
                cursor.execute(query, (receiverBd[0], id_email))

            self.conn.commit()
            return id_email

        except psycopg2.errors.lookup("23505"):
            raise ValueError('The email is already taken')

    def retreiveInbox(self, id_user):
        cursor = self.conn.cursor()
        query = "select e.id_email,e.subject,e.date_sended,e.id_user_from,u.email," \
                "(friends.id_user_tagged is not null) as friendship," \
                "STRING_AGG(distinct category.name,',' order by category.name ASC),is_readed," \
                " email_reply_to.id_email as id_email_reply_to," \
                " email_reply_to.subject as reply_subject" \
                " from receive inner join email e on receive.id_email = e.id_email" \
                " inner join \"user\" u on u.id_user = e.id_user_from" \
                " left join tags_friends friends on receive.id_user = friends.id_user_who_tag and e.id_user_from = friends.id_user_tagged" \
                " left join category on (receive.id_email = category.id_email and category.is_deleted = false) " \
                "left join replies r on receive.id_email = r.id_email " \
                "left join email email_reply_to on email_reply_to.id_email = r.id_email_reply_to" \
                " where receive.id_user = %s" \
                " and receive.is_deleted is false" \
                " group by receive.id_email,e.id_email,e.subject,e.date_sended,e.id_user_from,u.email," \
                " friends.id_user_tagged,is_readed,email_reply_to.id_email,"\
                "email_reply_to.subject" \
                " order by receive.id_email desc;"
        cursor.execute(query, (id_user,))
        result = []
        for row in cursor:
            result.append(row)
        return result;

    def searchInbox(self,id_user,field,value):
        cursor = self.conn.cursor()

        filterSection = ""
        if field == 'category':
            filterSection = " and category.name like %s"
        else:
            filterSection = " and u.email like %s"

        query = "select e.id_email,e.subject,e.date_sended,e.id_user_from,u.email," \
                "(friends.id_user_tagged is not null) as friendship," \
                "STRING_AGG(distinct category.name,',' order by category.name ASC),is_readed," \
                " email_reply_to.id_email as id_email_reply_to," \
                " email_reply_to.subject as reply_subject" \
                " from receive inner join email e on receive.id_email = e.id_email" \
                " inner join \"user\" u on u.id_user = e.id_user_from" \
                " left join tags_friends friends on receive.id_user = friends.id_user_who_tag and e.id_user_from = friends.id_user_tagged" \
                " left join category on receive.id_email = category.id_email and category.is_deleted = false " \
                "left join replies r on receive.id_email = r.id_email "\
                "left join email email_reply_to on email_reply_to.id_email = r.id_email_reply_to"\
                " where receive.id_user = %s" \
                " and receive.is_deleted is false" + filterSection + ""  \
                " group by receive.id_email,e.id_email,e.subject,e.date_sended,e.id_user_from,u.email," \
                " friends.id_user_tagged,receive.is_readed,email_reply_to.id_email,"\
                "email_reply_to.subject" \
                " order by receive.id_email desc;"
        cursor.execute(query, (id_user,value,))
        result = []
        for row in cursor:
            result.append(row)
        return result;

    def setCategoryEmail(self,id_user,id_email,category):
        cursor = self.conn.cursor()
        query = "select 1 from receive where id_user = %s and id_email = %s;"
        cursor.execute(query, (id_user, id_email))
        row = cursor.fetchone()
        if row is None:
            raise ValueError('The email doesn´t exits')
        query = "insert into category(id_email,id_user,name) values(%s,%s,%s);"
        print("REQUEST: ", category)

        cursor.execute(query, (id_email,id_user,category,))

        self.conn.commit()

        query = "select distinct name from category where id_email = %s and id_user= %s"
        cursor.execute(query, (id_email, id_user,))
        result = []
        for row in cursor:
            result.append(row)
        return result;

    def updateCategory (self, id_category, id_email, id_user, name):
        cursor = self.conn.cursor()
        query = "update category set id_email=%s, id_user=%s, name=%s where id_category=%s"
        cursor.execute(query, (id_email, id_user, name, id_category))
        self.conn.commit()
        return id_category

    def deleteCategory (self, id_category):
        cursor  = self.conn.cursor()
        query = "update category set is_deleted = True where id_category=%s"
        cursor.execute(query, (id_category,))
        self.conn.commit()
        return id_category

    def retreiveOutbox(self, id_user):
        cursor = self.conn.cursor()
        query = "select email.id_email,email.subject,email.date_sended," \
                "STRING_AGG(distinct u.email,',' order by u.email ASC), " \
                "email_reply_to.id_email as id_email_reply_to," \
                "email_reply_to.subject as reply_subject " \
                "from email " \
                "inner join receive e on email.id_email = e.id_email " \
                "inner join \"user\" u on u.id_user = e.id_user " \
                "left join replies r on email.id_email = r.id_email " \
                "left join email email_reply_to on email_reply_to.id_email = r.id_email_reply_to " \
                "where email.id_user_from = %s " \
                "and email.is_deleted_outbox is false " \
                "group by email.id_email,email.subject,email.date_sended, " \
                "email_reply_to.id_email," \
                "email_reply_to.subject " \
                "order by email.id_email desc"
        cursor.execute(query, (id_user,))
        result = []
        for row in cursor:
            result.append(row)
        return result;

    def searchOutbox(self, id_user, field, value):
        cursor = self.conn.cursor()

        filterSection = ""
        if field == 'email':
            filterSection = " and u.email like %s"

        query = "select email.id_email,email.subject,email.date_sended," \
                "STRING_AGG(distinct u.email,',' order by u.email ASC), " \
                "email_reply_to.id_email as id_email_reply_to," \
                "email_reply_to.subject as reply_subject " \
                "from email " \
                "inner join receive e on email.id_email = e.id_email " \
                "inner join \"user\" u on u.id_user = e.id_user " \
                "left join replies r on email.id_email = r.id_email "\
                "left join email email_reply_to on email_reply_to.id_email = r.id_email_reply_to "\
                "where email.id_user_from = %s " \
                "and email.is_deleted_outbox is false " + filterSection + ""  \
                "group by email.id_email,email.subject,email.date_sended, " \
                "email_reply_to.id_email,"\
                "email_reply_to.subject "\
                "order by email.id_email desc"
        cursor.execute(query, (id_user, value,))
        result = []
        for row in cursor:
            result.append(row)
        return result;

    def deleteOutbox(self, id_user, id_email):
        cursor = self.conn.cursor()
        query = "select is_premium from \"user\" where id_user = %s;"
        cursor.execute(query, (id_user,))
        row = cursor.fetchone()
        if row is None:
            raise ValueError('The id user doesn´t exits')
        is_premium = row[0]
        cursor = self.conn.cursor()
        query = "update email set is_deleted_outbox = true where id_email = %s and id_user_from = %s;"
        cursor.execute(query, (id_email,id_user))
        if is_premium:
            query = "update receive set is_deleted = true where id_email = %s;"
            cursor.execute(query, (id_email,))
        self.conn.commit()

    def deleteInbox(self, id_user, id_email):
        cursor = self.conn.cursor()
        query = "update receive set is_deleted = true where id_user = %s and id_email = %s;"
        cursor.execute(query, (id_user, id_email))
        self.conn.commit()

    def updateOutbox(self, id_user, id_email,subject,raw_content):
        cursor = self.conn.cursor()
        query = "select is_premium from \"user\" where id_user = %s;"
        cursor.execute(query, (id_user,))
        row = cursor.fetchone()
        if row is None:
            raise ValueError('The id user doesn´t exits')
        is_premium = row[0]
        if is_premium is not True:
            raise ValueError('The user is not premium')
        #we include id_user in where clause to ensure that the requested operation over the email is
        #made by the owner (the premium user).
        query = "update email set subject = %s, raw_content = %s where id_email = %s and id_user_from = %s and is_deleted_outbox = false;"
        cursor.execute(query, (subject,raw_content,id_email,id_user))
        self.conn.commit()

        query = "select email.id_email,subject,date_sended," \
                "STRING_AGG(distinct u.email,',' order by u.email ASC),raw_content,u.email " \
                "from email " \
                "inner join receive e on email.id_email = e.id_email " \
                "inner join \"user\" u on u.id_user = e.id_user " \
                "where email.id_email = %s and is_deleted_outbox = false " \
                "group by email.id_email,subject,date_sended,raw_content,u.email " \
                "order by email.id_email desc"
        cursor.execute(query, (id_email,))
        email_info = cursor.fetchone()
        if email_info is None:
            raise ValueError('The email doesn´t exists')

        return email_info

    def viewInboxEmail(self,id_user,id_email):
        cursor = self.conn.cursor()
        query = "select email.id_email,subject,date_sended," \
                "STRING_AGG(distinct u_receiver.email,',' order by u_receiver.email ASC),raw_content,u_sender.email," \
                "e.is_readed,u_sender.id_user,e.require_ack " \
                "from email " \
                "inner join receive e on email.id_email = e.id_email " \
                "inner join \"user\" u_receiver on u_receiver.id_user = e.id_user " \
                "inner join \"user\" u_sender on u_sender.id_user = email.id_user_from " \
                "where e.is_deleted is false and e.id_email = %s and e.id_user = %s" \
                "group by email.id_email,subject,date_sended,raw_content,u_sender.email," \
                "e.is_readed,u_sender.id_user,e.require_ack " \
                "order by email.id_email desc"
        cursor.execute(query, (id_email,id_user))
        email_info = cursor.fetchone()
        if email_info is None:
            raise ValueError('The email info doesn´t exits')
        if email_info[6] is False and email_info[8] : # If email has not been read and
            # the email requires acknowledgment
            query = "insert into \"email\"(subject, raw_content, date_sended,id_user_from)" \
                    " values (%s, %s,current_timestamp, %s) returning id_email;"
            cursor.execute(query, ("Email read alert:"+str(email_info[0]),
                                   "The email with subject:\""+str(email_info[1])+"\" has been readed ",
                                   0))
            id_email_acknowled = cursor.fetchone()[0]
            query = "insert into \"receive\"(id_user, id_email,require_ack)" \
                    " values (%s, %s,false);"
            cursor.execute(query, (email_info[7], id_email_acknowled))

        if email_info[6] is False:
            query = "update receive set is_readed = true where id_user=%s and id_email=%s;"
            cursor.execute(query, (id_user, id_email))

        self.conn.commit()
        return email_info

    def viewOutboxEmail(self,id_user,id_email):
        cursor = self.conn.cursor()
        query = "select email.id_email,subject,date_sended," \
                "STRING_AGG(distinct u_receiver.email,',' order by u_receiver.email ASC),raw_content,u_sender.email " \
                "from email " \
                "inner join receive e on email.id_email = e.id_email " \
                "inner join \"user\" u_receiver on u_receiver.id_user = e.id_user " \
                "inner join \"user\" u_sender on u_sender.id_user = email.id_user_from " \
                "where email.is_deleted_outbox is false and email.id_email = %s and email.id_user_from = %s" \
                "group by email.id_email,subject,date_sended,raw_content,u_sender.email,e.is_readed,u_sender.id_user " \
                "order by email.id_email desc"
        cursor.execute(query, (id_email,id_user))
        email_info = cursor.fetchone()
        if email_info is None:
            raise ValueError('The email info doesn´t exits')

        return email_info

    def replyEmail(self, id_user, id_email,subject,raw_content):
        try:
            cursor = self.conn.cursor()
            query = "select e.id_user_from,e.subject,u.email from receive r inner join " \
                    "\"email\" e on r.id_email = e.id_email " \
                    "inner join \"user\" u on e.id_user_from = u.id_user " \
                    "where r.id_email = %s and r.id_user = %s and r.is_deleted = false ;"
            cursor.execute(query, (id_email,id_user))
            email_to_reply = cursor.fetchone()
            if email_to_reply is None:
                raise ValueError("The email to reply doesn´t exits")
            if subject is None:
                subject = "Re: "+email_to_reply[1]

            try:
                query = "insert into \"email\"(subject, raw_content, date_sended,id_user_from)" \
                        " values (%s, %s,current_timestamp, %s) returning id_email;"
                cursor.execute(query, (subject, raw_content, id_user))
            except psycopg2.errors.lookup("23503"):
                raise ValueError('The id user doesn´t exits')

            id_email_reply = cursor.fetchone()[0]

            query = "insert into \"replies\"(id_email, id_email_reply_to)" \
                    " values (%s, %s);"
            cursor.execute(query, (id_email_reply, id_email))

            query = "insert into \"receive\"(id_user, id_email)" \
                    " values (%s, %s);"
            cursor.execute(query, (email_to_reply[0], id_email_reply))

            self.conn.commit()
            return (id_email_reply,subject,email_to_reply[2])

        except psycopg2.errors.lookup("23505"):
            raise ValueError('The email is already taken')

    def viewEmailMostRecipients(self):
        query = "SELECT id_email, count(id_email) AS replies from" \
                " \"receive\" group by id_email" \
                " having count(id_email) =(select max(a.counting) from  " \
                " (select id_email, count(id_email) as counting from " \
                " \"receive\"  group by id_email) a)"
        cursor = self.conn.cursor()
        cursor.execute(query)
        result = []
        for row in cursor:
            print(row)
            result.append(row)
        cursor.close()
        return result

    def viewEmailMostReplies(self):
        query = "SELECT id_email_reply_to AS id_email, count(id_email) AS replies from"\
                " \"replies\" group by id_email_reply_to"\
                " having count(id_email) =(select max(a.counting) from  " \
                " (select id_email_reply_to, count(id_email) as counting from "\
                " \"replies\"  group by id_email_reply_to) a)"
        cursor = self.conn.cursor()
        cursor.execute(query)
        result = []
        for row in cursor:
            print(row)
            result.append(row)
        cursor.close()
        return result








