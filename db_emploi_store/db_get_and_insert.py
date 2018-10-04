import requests
import json
import time
from db_emploi_store.db_init import initialize_db
import pymysql

def api_init(client_secret, client_id):
    # API CONNECTION #
    try:
        response=requests.post(
            "https://entreprise.pole-emploi.fr/connexion/oauth2/access_token",
            data={
                'grant_type': 'client_credentials',
                'client_id': client_id,
                'client_secret': client_secret,
                'scope':'api_offresdemploiv1 o2dsoffre application_{}'
                        .format(client_id),
                'realm':'partenaire'
            },
            headers={'Content-Type':'application/x-www-form-urlencoded',
                                    'Accept':'application/json'}
            , params={"technicalParameters":{"page":1}}
        ).json()
        token = response['access_token']
        return token
    except requests.exceptions.RequestException as error:
        print(error)


def list_dept_init():
# INITILIZATION TO LIST DEPARTMENTS #
    listdept = [i for i in range(1,96) if i!=20]
    for i,j in enumerate(listdept[0:9]):
        listdept[i]=str(0)+str(j)
    return listdept


def send_request_api(token, search_keyword, listdept, cursor):
    # REQUEST API #
    url = """
    https://api.emploi-store.fr/partenaire/offresdemploi/v1/rechercheroffres"""
    criteria = ['offerId', 'title', 'departmentCode', 'cityCode', 'cityName', 'companyName',
            'description', 'contractTypeCode', 'companyContactEmail',
            'minSalary', 'maxSalary', 'gpsLatitude', 'gpsLongitude', 'skills']
    for iteration in listdept:
        arguments = {"criterias":{"departmentCode": "{}".format(iteration),
                                    "keywords":"{}".format(search_keyword)}}
        result=requests.post(url,
                            params={"technicalParameters":{"page":1}},
            headers={'Authorization': 'Bearer {}'.format(token),
                    'Content-Type':'application/json',
                    'Accept':'application/json'        
                    },
                    json=arguments)
        time.sleep(2)
        data = json.loads(result.text)
        for item in data['results']:
            tempo_dict = {}
            list_skill = []
            for target in criteria:
                tempo_dict.update({target : item.get(target)})
                tempo_dict.update({'description' : item['description']
                .replace("\n", "")})
            if tempo_dict['minSalary'] is None or tempo_dict['maxSalary'] is None \
            or tempo_dict['minSalary'] == 9.76:
                tempo_dict.update({'minSalary' : None})
                tempo_dict.update({'maxSalary' : None})
            elif tempo_dict['minSalary'] >10000 and \
                tempo_dict['maxSalary'] is not None or \
                tempo_dict['maxSalary'] >10000 and \
                tempo_dict['minSalary'] is not None:
                tempo_dict.update({'minSalary' : int(item['minSalary']/12)})
                tempo_dict.update({'maxSalary' : int(item['maxSalary']/12)})
            else:
                tempo_dict.update({'minSalary' : int(item['minSalary'])})
                tempo_dict.update({'maxSalary' : int(item['maxSalary'])})
            for skill in item['skills']:
                list_skill.append(skill['skillName'])
                tempo_dict.update({'skills' : list_skill})
            try:
                cursor.execute("""
                    INSERT INTO
                        o_geoloc(g_o_id, g_gps_latitude, g_gps_longitude)
                    VALUES
                        (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        g_gps_latitude=%s, g_gps_longitude=%s""", (
                            tempo_dict['offerId'], tempo_dict['gpsLatitude'],
                            tempo_dict['gpsLongitude'], tempo_dict['gpsLatitude'],
                            tempo_dict['gpsLongitude']))
                cursor.execute("""
                    INSERT INTO
                        o_salary(slry_o_id, slry_min_salary, slry_max_salary)
                    VALUES
                        (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        slry_min_salary=%s, slry_max_salary=%s""", (
                            tempo_dict['offerId'], tempo_dict['minSalary'],
                            tempo_dict['maxSalary'], tempo_dict['minSalary'],
                            tempo_dict['maxSalary']))
                cursor.execute("""
                    INSERT INTO
                        offer(o_id, o_search_keyword, o_title, o_department_code, 
                        o_city_code, o_city, o_company_name, o_description, o_contract,
                        o_contact_mail, g_o_id, slry_o_id, o_added_at)
                    VALUES
                        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, o_id, o_id, NOW())
                    ON DUPLICATE KEY UPDATE
                        o_title=%s, o_city_code=%s, o_city=%s, o_company_name=%s,\
                        o_description=%s, o_contract=%s, o_contact_mail=%s,
                        o_updated_at=NOW()""", (
                            tempo_dict['offerId'], search_keyword, tempo_dict['title'],
                            tempo_dict['departmentCode'], tempo_dict['cityCode'],
                            tempo_dict['cityName'],
                            tempo_dict['companyName'], tempo_dict['description'],
                            tempo_dict['contractTypeCode'], ['companyContactEmail'],
                            tempo_dict['title'], tempo_dict['cityCode'],
                            tempo_dict['cityName'], tempo_dict['companyName'],
                            tempo_dict['description'],
                            tempo_dict['contractTypeCode'],
                            tempo_dict['companyContactEmail']))
                for skill in list_skill:
                    req_skills = """INSERT INTO o_skills (s_skill_name, o_id)
                    VALUES (%s, %s)"""
                    cursor.execute(req_skills, (skill, tempo_dict['offerId']))
            except pymysql.Error as e:
                print(e)


def get_data(client_secret, client_id, search_keyword, db_config):
    database = initialize_db(db_config)
    cursor = database.cursor()
    token = api_init(client_secret, client_id)
    listdept = list_dept_init()
    send_request_api(token, search_keyword, listdept, cursor)
    database.commit()
    return database
