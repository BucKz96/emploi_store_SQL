""" warnings: to ignore warning sql
    pymysql: to connect DB MySQL
"""
import warnings
import pymysql

# SQL CONNECTION #
def connect_db(host, user, passwd, db_name, char):
    """ Connect to db and create db_name if not exists.
    """
    try:
        database = pymysql.connect(host, user, passwd, db_name, charset=char)
        cursor = database.cursor()
        cursor.execute("SELECT VERSION()")
        db_v = cursor.fetchone()
        print("DATABASE VERSION : {} \nCONNECTION OK".format(db_v))
    except pymysql.InternalError:
        database = pymysql.connect(host, user, passwd)
        cursor = database.cursor()
        cursor.execute("SELECT VERSION()")
        db_v = cursor.fetchone()
        cursor.execute("CREATE DATABASE IF NOT EXISTS {} CHARACTER SET {}"\
            .format(db_name, char))
        cursor.select_db(db_name)
        print("Connection : OK \nDATABASE VERSION : {} \nCREATING DATABASE {} OK"\
            .format(db_v, db_name))
    return cursor


def create_tables(cursor):
    """ Create tables and iterate on 'tables' dict to execute query.
    """
    tables = {}
    tables['o_salary'] = (
        "CREATE TABLE IF NOT EXISTS `o_salary` ("
        "  `slry_id` INT NOT NULL AUTO_INCREMENT,"
        "  `slry_min_salary` INT ,"
        "  `slry_max_salary` INT ,"
        "  PRIMARY KEY (`slry_id`)"
        ") ENGINE=INNODB")

    tables['o_geoloc'] = (
        "CREATE TABLE IF NOT EXISTS `o_geoloc` ("
        "  `g_id` INT NOT NULL AUTO_INCREMENT,"
        "  `g_gps_latitude` FLOAT(10,6) ,"
        "  `g_gps_longitude` FLOAT(10,6) ,"
        "  PRIMARY KEY (`g_id`)"
        ") ENGINE=INNODB")

    tables['offer'] = (
        "CREATE TABLE IF NOT EXISTS `offer` ("
        "  `o_id` VARCHAR(45) NOT NULL ,"
        "  `o_title` VARCHAR(100) NOT NULL ,"
        "  `o_city_code` INT ,"
        "  `o_city` VARCHAR(100) ,"
        "  `o_company_name` VARCHAR(100) ,"
        "  `o_description` TEXT ,"
        "  `o_contract` VARCHAR(45) ,"
        "  `o_contact_mail` VARCHAR(255) ,"
        "  `o_update_datetime` DATETIME NOT NULL ,"
        "  `o_fk_salary_id` INT NOT NULL ,"
        "  `o_fk_geoloc_id` INT NOT NULL ,"
        "  PRIMARY KEY (`o_id`),"
        "  KEY `fkIdx_62` (`o_fk_salary_id`),"
        "  CONSTRAINT `FK_62` FOREIGN KEY `fkIdx_62` (`o_fk_salary_id`)\
        REFERENCES `o_salary` (`slry_id`),"
        "  KEY `fkIdx_68` (`o_fk_geoloc_id`),"
        "  CONSTRAINT `FK_68` FOREIGN KEY `fkIdx_68` (`o_fk_geoloc_id`)\
         REFERENCES `o_geoloc` (`g_id`)"
        ") ENGINE=INNODB")

    tables['o_skills'] = (
        "CREATE TABLE IF NOT EXISTS `o_skills` ("
        "  `s_id`          INT NOT NULL AUTO_INCREMENT ,"
        "  `s_skill_name`  VARCHAR(100) UNIQUE NULL,"
        "  `s_fk_offer_id` VARCHAR(45) NOT NULL ,"
        "  PRIMARY KEY (`s_id`),"
        "  KEY `fkIdx_59` (`s_fk_offer_id`),"
        "  CONSTRAINT `FK_59` FOREIGN KEY `fkIdx_59` (`s_fk_offer_id`)\
         REFERENCES `offer` (`o_id`)"
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
    return "All the tables in DB"


def initialize_db(config):
    """ General execution
    """
    host = config['host']
    user = config['user']
    passwd = config['passwd']
    db_name = config['db']
    char = config['char']
    cursor = connect_db(host, user, passwd, db_name, char)
    create_tables(cursor)
