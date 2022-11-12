from conf.dbconfig import pg_config
import psycopg2


class EmailDAO:
    def __init__(self):

        connection_url = "dbname=%s user=%s password=%s host=%s" % (pg_config['dbname'],
                                                                    pg_config['user'],
                                                                    pg_config['passwd'],
                                                                    pg_config['host'])
        self.conn = psycopg2._connect(connection_url)

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
        query = "select e.id_email,subject,date_sended,e.id_user_from,u.email," \
                "(friends.id_user_tagged is not null) as friendship," \
                "STRING_AGG(distinct category.name,',' order by category.name ASC),is_readed" \
                " from receive inner join email e on receive.id_email = e.id_email" \
                " inner join \"user\" u on u.id_user = e.id_user_from" \
                " left join tags_friends friends on receive.id_user = friends.id_user_who_tag and e.id_user_from = friends.id_user_tagged" \
                " left join category on receive.id_email = category.id_email" \
                " where receive.id_user = %s" \
                " and is_deleted is false" \
                " group by receive.id_email,e.id_email,subject,date_sended,e.id_user_from,u.email," \
                " friends.id_user_tagged,is_readed" \
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

        query = "select e.id_email,subject,date_sended,e.id_user_from,u.email," \
                "(friends.id_user_tagged is not null) as friendship," \
                "STRING_AGG(distinct category.name,',' order by category.name ASC),is_readed" \
                " from receive inner join email e on receive.id_email = e.id_email" \
                " inner join \"user\" u on u.id_user = e.id_user_from" \
                " left join tags_friends friends on receive.id_user = friends.id_user_who_tag and e.id_user_from = friends.id_user_tagged" \
                " left join category on receive.id_email = category.id_email" \
                " where receive.id_user = %s" \
                " and is_deleted is false" + filterSection + ""  \
                " group by receive.id_email,e.id_email,subject,date_sended,e.id_user_from,u.email," \
                " friends.id_user_tagged,is_readed" \
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

    def retreiveOutbox(self, id_user):
        cursor = self.conn.cursor()
        query = "select email.id_email,subject,date_sended," \
                "STRING_AGG(distinct u.email,',' order by u.email ASC) " \
                "from email " \
                "inner join receive e on email.id_email = e.id_email " \
                "inner join \"user\" u on u.id_user = e.id_user " \
                "where email.id_user_from = %s " \
                "and email.is_deleted_outbox is false " \
                "group by email.id_email,subject,date_sended " \
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

        query = "select email.id_email,subject,date_sended," \
                "STRING_AGG(distinct u.email,',' order by u.email ASC) " \
                "from email " \
                "inner join receive e on email.id_email = e.id_email " \
                "inner join \"user\" u on u.id_user = e.id_user " \
                "where email.id_user_from = %s " \
                "and email.is_deleted_outbox is false " + filterSection + ""  \
                "group by email.id_email,subject,date_sended " \
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
        query = "update email set subject = %s, raw_content = %s where id_email = %s and id_user_from = %s;"
        cursor.execute(query, (subject,raw_content,id_email,id_user))
        self.conn.commit()

        query = "select email.id_email,subject,date_sended," \
                "STRING_AGG(distinct u.email,',' order by u.email ASC),raw_content,u.email " \
                "from email " \
                "inner join receive e on email.id_email = e.id_email " \
                "inner join \"user\" u on u.id_user = e.id_user " \
                "where email.id_email = %s " \
                "group by email.id_email,subject,date_sended,raw_content,u.email " \
                "order by email.id_email desc"
        cursor.execute(query, (id_email,))
        email_info = cursor.fetchone()
        return email_info

    def viewInboxEmail(self,id_user,id_email):
        cursor = self.conn.cursor()
        query = "select email.id_email,subject,date_sended," \
                "STRING_AGG(distinct u_receiver.email,',' order by u_receiver.email ASC),raw_content,u_sender.email," \
                "e.is_readed,u_sender.id_user " \
                "from email " \
                "inner join receive e on email.id_email = e.id_email " \
                "inner join \"user\" u_receiver on u_receiver.id_user = e.id_user " \
                "inner join \"user\" u_sender on u_sender.id_user = email.id_user_from " \
                "where e.is_deleted is false and e.id_email = %s and e.id_user = %s" \
                "group by email.id_email,subject,date_sended,raw_content,u_sender.email,e.is_readed,u_sender.id_user " \
                "order by email.id_email desc"
        cursor.execute(query, (id_email,id_user))
        email_info = cursor.fetchone()
        if email_info is None:
            raise ValueError('The email info doesn´t exits')
        if email_info[6] is False:
            query = "insert into \"email\"(subject, raw_content, date_sended,id_user_from)" \
                    " values (%s, %s,current_timestamp, %s) returning id_email;"
            cursor.execute(query, ("Email read alert:"+str(email_info[0]),
                                   "The email with subject:\""+str(email_info[1])+"\" has been readed ",
                                   0))
            id_email_acknowled = cursor.fetchone()[0]
            query = "insert into \"receive\"(id_user, id_email)" \
                    " values (%s, %s);"
            cursor.execute(query, (email_info[7], id_email_acknowled))

            query = "update receive set is_readed = true where id_user=%s and id_email=%s;"

            cursor.execute(query, (id_user,id_email))

            self.conn.commit()
        return email_info





















