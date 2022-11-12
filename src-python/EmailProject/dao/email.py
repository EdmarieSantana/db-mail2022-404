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


            #row = cursor.fetchone()
            #if row is None:
            #    raise ValueError('The email doesn´t exits')
            #id_user_to = row[0];
            #cursor = self.conn.cursor()
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
                "STRING_AGG(distinct category.name,',' order by category.name ASC)" \
                " from receive inner join email e on receive.id_email = e.id_email" \
                " inner join \"user\" u on u.id_user = e.id_user_from" \
                " left join tags_friends friends on receive.id_user = friends.id_user_who_tag and e.id_user_from = friends.id_user_tagged" \
                " left join category on receive.id_email = category.id_email" \
                " where receive.id_user = %s" \
                " and is_deleted is false" \
                " group by receive.id_email,e.id_email,subject,date_sended,e.id_user_from,u.email, friends.id_user_tagged" \
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
                "STRING_AGG(distinct category.name,',' order by category.name ASC)" \
                " from receive inner join email e on receive.id_email = e.id_email" \
                " inner join \"user\" u on u.id_user = e.id_user_from" \
                " left join tags_friends friends on receive.id_user = friends.id_user_who_tag and e.id_user_from = friends.id_user_tagged" \
                " left join category on receive.id_email = category.id_email" \
                " where receive.id_user = %s" \
                " and is_deleted is false" + filterSection + ""  \
                " group by receive.id_email,e.id_email,subject,date_sended,e.id_user_from,u.email, friends.id_user_tagged" \
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
        query = "select e.id_email,subject,date_sended,e.id_user_from,u.email," \
                "(friends.id_user_tagged is not null) as friendship," \
                "STRING_AGG(distinct category.name,',' order by category.name ASC)" \
                " from receive inner join email e on receive.id_email = e.id_email" \
                " inner join \"user\" u on u.id_user = e.id_user_from" \
                " left join tags_friends friends on receive.id_user = friends.id_user_who_tag and e.id_user_from = friends.id_user_tagged" \
                " left join category on receive.id_email = category.id_email" \
                " where receive.id_user = %s" \
                " and is_deleted is false" \
                " group by receive.id_email,e.id_email,subject,date_sended,e.id_user_from,u.email, friends.id_user_tagged" \
                " order by receive.id_email desc;"
        cursor.execute(query, (id_user,))
        result = []
        for row in cursor:
            result.append(row)
        return result;




















