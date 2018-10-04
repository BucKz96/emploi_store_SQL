""" warnings: to ignore warning sql
    pymysql: to connect DB MySQL
"""
import warnings
import pymysql

# SQL CONNECTION #
def connect_db(host, port, user, passwd, db_name):
    """ Connect to db and create db_name if not exists.
    """
    try:
        database = pymysql.connect(db=db_name, user=user, passwd=passwd, host=host, port=port)
        cursor = database.cursor()
        cursor.execute("SELECT VERSION()")
        db_v = cursor.fetchone()
        print("DATABASE VERSION : {} \nCONNECTION OK".format(db_v))
    except pymysql.err.InternalError:
        database = pymysql.connect(user=user, passwd=passwd, host=host, port=port)
        cursor = database.cursor()
        cursor.execute("SELECT VERSION()")
        db_v = cursor.fetchone()
        cursor.execute("CREATE DATABASE IF NOT EXISTS {}"\
            .format(db_name))
        cursor.execute("USE {}".format(db_name))
        print("Connection : OK \nDATABASE VERSION : {} \nCREATING DATABASE {} OK"\
            .format(db_v, db_name))
    return database


def create_tables(cursor):
    """ Create tables and iterate on 'tables' dict to execute query.
    """
    tables = {}
    tables['o_salary'] = (
        "CREATE TABLE IF NOT EXISTS `o_salary` ("
        "  `slry_o_id` VARCHAR(45) NOT NULL ,"
        "  `slry_min_salary` INT ,"
        "  `slry_max_salary` INT ,"
        "  PRIMARY KEY (`slry_o_id`)"
        ") ENGINE=INNODB")

    tables['o_geoloc'] = (
        "CREATE TABLE IF NOT EXISTS `o_geoloc` ("
        "  `g_o_id` VARCHAR(45) NOT NULL ,"
        "  `g_gps_latitude` FLOAT(10,6) ,"
        "  `g_gps_longitude` FLOAT(10,6) ,"
        "  PRIMARY KEY (`g_o_id`)"
        ") ENGINE=INNODB")

    tables['offer'] = (
        "CREATE TABLE IF NOT EXISTS `offer` ("
        "  `o_id` VARCHAR(45) NOT NULL ,"
        "  `o_search_keyword` VARCHAR(100) NOT NULL ,"
        "  `o_title` VARCHAR(100) NOT NULL ,"
        "  `o_department_code` INT ,"
        "  `o_city_code` INT ,"
        "  `o_city` VARCHAR(100) ,"
        "  `o_company_name` VARCHAR(100) ,"
        "  `o_description` TEXT ,"
        "  `o_contract` VARCHAR(45) ,"
        "  `o_contact_mail` VARCHAR(255) ,"
        "  `g_o_id` VARCHAR(45) ,"
        "  `slry_o_id` VARCHAR(45) ,"
        "  `o_added_at` DATETIME DEFAULT CURRENT_TIMESTAMP ,"
        "  `o_updated_at` DATETIME ON UPDATE CURRENT_TIMESTAMP ,"
        "  PRIMARY KEY (`o_id`) ,"
        "  FOREIGN KEY (g_o_id) REFERENCES o_geoloc(g_o_id) ,"
        "  FOREIGN KEY (slry_o_id) REFERENCES o_salary(slry_o_id) "
        ") ENGINE=INNODB")

    tables['o_skills'] = (
        "CREATE TABLE IF NOT EXISTS `o_skills` ("
        "  `s_id` INT NOT NULL AUTO_INCREMENT ,"
        "  `s_skill_name`  VARCHAR(255) NULL ,"
        "  `o_id`  VARCHAR(45) NOT NULL ,"
        "  PRIMARY KEY (`s_id`) ,"
        "  FOREIGN KEY (`o_id`) REFERENCES `offer` (`o_id`) "
        ") ENGINE=INNODB")

    with warnings.catch_warnings():
        warnings.simplefilter('ignore', pymysql.Warning)
        for name, ddl in tables.items():
            try:
                cursor.execute(ddl)
                success = ['TABLE : {} CREATED'.format(name)]
                print(success)
            except pymysql.err as error:
                print(error.args)


def initialize_db(config):
    """ General execution
    """
    host = config['host']
    port = config['port']
    user = config['user']
    passwd = config['passwd']
    db_name = config['db']
    database = connect_db(host, port, user, passwd, db_name)
    cursor = database.cursor()
    create_tables(cursor)
    return database
