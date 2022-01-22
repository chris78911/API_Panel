from flask import Flask, render_template, request
import sqlite3
import datetime
import os.path
import similarity
import similarityTFIDF

app = Flask(__name__)

@app.route('/services')
def services():
    argsList = request.args

    application = argsList.get('application')
    apiName = argsList.get('apiName')
    serviceLine = argsList.get('serviceLine')
    targetapi = argsList.get('targetapi')
    # print("--------------------------------------------------------")
    # print(targetapi)

    apiName = "%" + str(apiName) + "%"

    argsList = []
    argsList.append(apiName)
    sql = "select * from cmb_production_apis where API like ?"
    if (serviceLine):
        argsList.append(serviceLine)
        sql = sql + " and service_line = ?"
    if (application):
        argsList.append(application)
        sql = sql + " and application = ?"
    sql =sql + " limit 0,20"
    # sql = "select * from cmb_production_apis where service_line = ? and API like ? limit 0,20"
    print(sql)
    query_result = []
    con = sqlite3.connect("API_DATA.db")
    cur = con.cursor()
    data = cur.execute(sql, argsList)
    for item in data:
        query_result.append(item)
    cur.close()
    con.close()

    # similarity_list = []
    if ((targetapi != None) and (len(targetapi) != 0)):
        print(targetapi)
        print(1)
        # similarity_list = similarity.main_process(targetapi)
        similarity_list = similarityTFIDF.main_process(targetapi)
        api = similarity_list[0][0]
    else:
        api = None
        print(targetapi)
        print(2)
        similarity_list = []
    return render_template("services.html", infos=query_result, similarity=similarity_list, api=api)

@app.route('/index')
def index():
    usage_by_serviceline_list = []
    usage_by_app_list = []
    risk_list = []
    sub_risk_list = []
    application_list = []

    infos = query("select * from cmb_production_apis limit 0,10", "API_DATA.db")
    usage_by_serviceline_list1 = query("select count(*), service_line from cmb_production_apis group by service_line", "API_DATA.db")
    usage_by_app_list1 = query("select count(*) c, application from cmb_production_apis group by application order by c desc", "API_DATA.db")
    risk_list1 = query("select Last_Update_Date, num_callers, API, service_line, application, service_line_owner from cmb_production_apis where has_weak_security = 'Y'", "API_DATA.db")
    ea_list1 = query("select count(*), application from cmb_production_apis where type = 'ea' group by application", "API_DATA.db")
    pa_list1 = query("select count(*), application from cmb_production_apis where type = 'pa' group by application", "API_DATA.db")
    sa_list1 = query("select count(*), application from cmb_production_apis where type = 'sa' group by application", "API_DATA.db")
    unknown_list1 = query("select count(*), application from cmb_production_apis where type not in ('ea','pa','sa') group by application", "API_DATA.db")
    springboot_list1 = query("select count(*), application from cmb_production_apis where is_springboot = 'Y' group by application", "API_DATA.db")
    mule_list1 = query("select count(*), application from cmb_production_apis where is_springboot = 'N' group by application", "API_DATA.db")




    # print(usage_by_serviceline_list1)
    for item in usage_by_serviceline_list1:
        dic = {}
        dic["value"] = item[0]
        dic["name"] = item[1]
        usage_by_serviceline_list.append(dic);
    # print(usage_by_serviceline_list)

    risk_api_detail_list = []
    for item in risk_list1:
        unmodified_days = unUpdatedDaysCalculate(item[0])
        number_of_call = item[1]
        risk_list.append([unmodified_days, number_of_call])
        if 850 - 25 * number_of_call < unmodified_days:
            sub_risk_list.append([unmodified_days, number_of_call])
            risk_api_detail_list.append(item)

    # sub_risk_list.append(risk_list[0])


    count = 0
    for i in range(len(usage_by_app_list1)):
        if i <= 6:
            dic = {"value": usage_by_app_list1[i][0], "name": usage_by_app_list1[i][1]}
            usage_by_app_list.append(dic)
        elif i == len(usage_by_app_list1)-1:
            dic = {"value": count, "name": "others"}
            usage_by_app_list.append(dic)
        else:
            count += usage_by_app_list1[i][0]

    for item in usage_by_app_list:
        application_list.append(item['name'])
    application_list.remove('others')

    ea_list = fetch_count(ea_list1, application_list)
    pa_list = fetch_count(pa_list1, application_list)
    sa_list = fetch_count(sa_list1, application_list)
    unknown_list = fetch_count(unknown_list1, application_list)
    mule_list = fetch_count(mule_list1, application_list)
    springboot_list = fetch_count(springboot_list1, application_list)

    return render_template("index.html", infos=infos, usage1=usage_by_serviceline_list, usage2=usage_by_app_list,
                           risk1=risk_list, risk_sub=sub_risk_list, ea_list=ea_list, sa_list=sa_list, pa_list=pa_list,
                           unknown_list=unknown_list, mule_list=mule_list, springboot_list=springboot_list,
                           application_list=application_list, risk_api_detail_list=risk_api_detail_list)

def fetch_count(source_list, application_list):
    result_list = []
    dic = {}
    for item in source_list:
        dic[item[1]] = item[0]
    for item in application_list:
        if item in dic:
            result_list.append(dic[item])
        else:
            result_list.append(0)
    return result_list

def query(sql, db):
    query_result = []
    con = sqlite3.connect(db)
    cur = con.cursor()
    data = cur.execute(sql)
    for item in data:
        query_result.append(item)
    cur.close()
    con.close()
    return query_result

def unUpdatedDaysCalculate(str1):
    year1 = str1.split('/')[0]
    month1 = str1.split('/')[1]
    day1 = str1.split('/')[-1]

    date1 = datetime.date(year=int(year1), month=int(month1), day=int(day1))
    date2 = datetime.datetime.now()
    year2 = date2.year
    month2 = date2.month
    day2 = date2.day
    date_current = datetime.date(year=year2, month=month2, day=day2)

    return (date_current - date1).days + 1

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
