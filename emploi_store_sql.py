import requests
import json
import numpy
import json
import time
import db_init

# CREATE TABLES SQL #
TABLES = {}
TABLES['offer'] = (
    "CREATE TABLE IF NOT EXISTS `offer` ("
    "  `o_id` varchar(255) COLLATE utf8_bin NOT NULL,"
    "  `o_title` varchar(255) COLLATE utf8_bin DEFAULT NULL,"
    "  `o_city_code` int COLLATE utf8_bin DEFAULT NULL,"
    "  `o_city` varchar(255)COLLATE utf8_bin DEFAULT NULL,"
    "  `o_company_name` varchar(155) COLLATE utf8_bin DEFAULT NULL,"
    "  `o_description` text COLLATE utf8_bin DEFAULT NULL,"
    "  `o_contract` varchar(100) COLLATE utf8_bin DEFAULT NULL,"
    "  `o_contact_mail` nvarchar(320) COLLATE utf8_bin DEFAULT NULL,"
    "  PRIMARY KEY (`o_id`)"
    ") ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin")

TABLES['o_salary'] = (
    "CREATE TABLE IF NOT EXISTS `o_salary` ("
    "  `o_id` varchar(10) NOT NULL,"
    "  `o_min_salary` float NOT NULL,"
    "  `o_max_salary` float NOT NULL,"
    "  PRIMARY KEY (`o_id`), UNIQUE KEY `o_id` (`o_id`)"
    ") ENGINE=InnoDB")

TABLES['o_skills'] = (
    "CREATE TABLE IF NOT EXISTS `o_skills` ("
    "  `o_id` varchar(10) NOT NULL,"
    "  `o_skills1` varchar(75),"
    "  `o_skills2` varchar(75),"
    "  `o_skills3` varchar(75),"
    "  `o_skills4` varchar(75),"
    "  `o_skills5` varchar(75),"
    "  PRIMARY KEY (`o_id`)"
    ") ENGINE=InnoDB")

TABLES['o_geoloc'] = (
    "CREATE TABLE IF NOT EXISTS `o_geoloc` ("
    "  `o_id` varchar(10) NOT NULL,"
    "  `o_gps_lat` float NOT NULL,"
    "  `o_gps_long` float NOT NULL,"
    "  PRIMARY KEY (`o_id`)"
    ") ENGINE=InnoDB")

for name, ddl in TABLES.items():
    try:
        cursor.execute(ddl)
        row = cursor.fetchone()
    except pymysql.Error as e:
        print(e)

# API CONNECTION #
client_id="PAR_idedataskills_ff9af1db81dd556671117874e2785cfb7744be3b25148a472f2d29a5b00b4126" # Your API ID Here
client_secret="ea2d066069be79cec2299c0b1081063c7a070b531d36ec6fd7144b74f6ddd5ae" # Your API Secret Here
response=requests.post(
    "https://entreprise.pole-emploi.fr/connexion/oauth2/access_token",
    data={
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope':'api_offresdemploiv1 o2dsoffre application_{}'.format(client_id),
        'realm':'partenaire'
    },
    headers={'Content-Type':'application/x-www-form-urlencoded','Accept':'application/json'}
    , params={"technicalParameters":{"page":1}}
).json()
token=response['access_token']

# INITILIZATION TO LIST DEPARTMENTS #
listdept= [i for i in range(1,96) if i!=20] 
listdept.extend(["2A","2B",971,972,973,974,976])
for i,j in enumerate(listdept[0:9]):
    listdept[i]=str(0)+str(j)

# REQUEST API #
for iteration in listdept:    
    url='https://api.emploi-store.fr/partenaire/offresdemploi/v1/rechercheroffres'
    arguments = {"criterias":{"departmentCode": "{}".format(iteration), "keywords":"Python"}}
    result=requests.post(url,
                         params={"technicalParameters":{"page":1}},
        headers={'Authorization': 'Bearer {}'.format(token),'Content-Type':'application/json','Accept':'application/json'        
                },     
                json=arguments)
    time.sleep(2)
    data = json.loads(result.text)

    # EXTRACT USEFUL DATA FROM JSON AND INSERT TO DB #
    tempo_dict = {}
    list_skill = []
    criteria = ['offerId', 'title', 'cityCode', 'cityName', 'companyName', 'description', 'contractTypeCode',
                'companyContactEmail', 'minSalary', 'maxSalary', 'gpsLatitude', 'gpsLongitude']
    for item in data['results']:
        for target in criteria:
            if target in item:
                tempo_dict.update({target : item[target]})
            else:
                tempo_dict.update({target : None})
        for skill in item['skills']:
            list_skill.append(skill['skillName'])
            tempo_dict.update({'skills' : list_skill})
        try:
            cursor.execute("""
                INSERT INTO
                    offer(o_id, o_title, o_city_code, o_city, o_company_name, o_description, o_contract,
                    o_contact_mail)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    o_title=%s, o_city_code=%s, o_city=%s, o_company_name=%s,o_description=%s, o_contract=%s,
                    o_contact_mail=%s""", (tempo_dict['offerId'], tempo_dict['title'], tempo_dict['cityCode'],
                                           tempo_dict['cityName'], tempo_dict['companyName'],
                                           tempo_dict['description'], tempo_dict['contractTypeCode'], 
                                           tempo_dict['companyContactEmail'], tempo_dict['title'], 
                                           tempo_dict['cityCode'], tempo_dict['cityName'], 
                                           tempo_dict['companyName'], tempo_dict['description'], 
                                           tempo_dict['contractTypeCode'], tempo_dict['companyContactEmail']))
            cursor.execute("""
                INSERT INTO
                    o_geoloc(o_id, o_gps_lat, o_gps_long)
                VALUES
                    (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    o_gps_lat=%s, o_gps_long=%s""", (tempo_dict['offerId'], tempo_dict['gpsLatitude'],
                                                     tempo_dict['gpsLongitude'], tempo_dict['gpsLatitude'],
                                                     tempo_dict['gpsLongitude']))
            db.commit()
        except pymysql.Error as e:
            print(e)
db.close()
