from __future__ import division
import requests, json
from shutil import copyfile
from yattag import Doc, indent
from datetime import datetime
import configparser


environment = ['ppcub16', 'x86ub16','ppcub18', 'x86ub18', 'ppcrh7', 'x86rh7','ppcrh75','x86rh75']
summary_name = ['ppc ubuntu16', 'x86 ubuntu16','ppc ubuntu18','x86 ubuntu18', 'ppc rhel72','x86 rhel72', 'ppc rhel75', 'x86 rhel75']


developer = ['Alisha' ,'Pravin','Prajyot', 'Yussuf' ]
devs = {'accumulo':'Prajyot','ambari':'Prajyot','atlas':'Yussuf','falcon':'Yussuf','flume':'Pravin','hadoop':'Pravin','hbase':'Prajyot','hive':'Alisha','kafka':'Prajyot','knox':'Yussuf','metron':'Pravin','oozie':'Alisha','phoenix':'Prajyot','pig':'Yussuf','ranger':'Yussuf','slider':'Yussuf','spark':'Prajyot','sqoop':'Yussuf','storm':'Alisha','tez':'Prajyot','zeppelin':'Alisha','zookeeper':'Pravin','calcite':'Pravin'}

                
def getBuild(resp):
    max_depth = 20
    a_j="/api/json"
    all_builds = resp['builds']
    i = 0
    build_url = ""
    for build in all_builds:
        if (i < max_depth):
            i += 1
            try:
                build_age = 0
                x = set([])
                builds_status_resp = requests.get(build['url'] + a_j + "", auth=(user, password))
                if builds_status_resp.json()['result'] != 'ABORTED' and  builds_status_resp.json()['result'] != 'FAILURE' and builds_status_resp.json()['building'] == False  :
                    if build_url == "":
                        build_url = build['url']
                    builds_job_resp = requests.get(build['url'] + 'testReport' + a_j + "", auth=(user, password))
                    builds_job_resp = json.loads(builds_job_resp.text, strict=False)
                    build_date = builds_status_resp.json()['timestamp'] 
                    converted_date = datetime.fromtimestamp(round(build_date/ 1000))
                    current_time_utc = datetime.utcnow()
                    build_age = (current_time_utc - converted_date).days
                    for test in builds_job_resp['suites']:
                        for env in environment:
                             if test['enclosingBlockNames'][1] == env:
                                x.add(env)
                    if len(x) == 8  :
                        return build['url']
            except Exception as e: print(e)
    return  build_url

def getResult(total_count ,failed_count):
    if total_count == 0:
        result = 'FAILURE'
    if failed_count == 0 and total_count > 0:
        result = 'SUCCESS'  
    if failed_count > 0  and total_count > 0:
        result = 'UNSTABLE'
    return result

def getResultImage(res) :
    ur = "resources/{0}.png"
    if res == "UNSTABLE" :
        return ur.format('yellow')
    if res == "SUCCESS" :
        return ur.format('blue')
    if res == "FAILURE" :
        return ur.format('red')
    if res == "ABORTED" :
        return ur.format('aborted')
        
testResults = {}
def getFailures(url, os, job) :
    buildsummary = {}
    buildsummary['name'] = str(job).upper()
    buildsummary['job'] = job
    totalTests = 0
    skippedTests = 0
    failedTests = 0
    testNames = []
    testErrs = []
    try:
        if url in testResults:
            testresult = testResults[url]
        else:
            testresult = requests.get(url,auth=(user, password))
            testresult = json.loads(testresult.text,strict=False)
            testResults[url] = testresult

        for test in testresult['suites'] :
            if test['enclosingBlockNames'][1] == os:
                for case in test['cases'] :
                    totalTests += 1
                    if case['skipped']  ==  True: 
                        skippedTests += 1
                    if case['status'] != 'PASSED' and case['status'] != 'SKIPPED' and case['status'] != 'FIXED' :
                        error = case['stdout']
                        testNames.append(case['className']+"."+case['name'])
                        failedTests +=1
                    
                        if case['errorDetails'] :
                            testErrs.append(case['errorDetails'][:400])
                        else :
                            testErrs.append(case['errorStackTrace'][:400])
        buildsummary['testErrorName'] = testNames
        buildsummary['testErrorDesc'] = testErrs
        buildsummary['totalCount'] = totalTests
        buildsummary['failedCount'] = failedTests
        buildsummary['skippedCount'] = skippedTests
        buildsummary['result'] = getResult(totalTests, failedTests)
        return buildsummary
    except:
        return buildsummary

def main():
    doc, tag, text = Doc().tagtext()
    jobs = []
    summary = {}

    job_url="/job/"
    a_j="/api/json"
    req=server_url+a_j
    resp = requests.get(req,auth=(user, password))

    for job in resp.json()['jobs'] :
        if 'tmp' in job['name'].lower():
            continue
        #if len(jobs) > 1 : break
        jobs.append(job['name'])

    with tag('html'):
        with tag('head'):
            with tag('script',src="resources/jquery.min.js"):
                text()
            with  tag('link', rel="stylesheet", href="resources/bootstrap.min.css"):
                text()
            with  tag('link', rel="stylesheet",  href="resources/bootstrap-theme.min.css"):
                text()
            with  tag('script', src="resources/bootstrap.min.js"):
                text()
            with tag('script', src='helper.js') :
                text('function hideAll(){console.log("hideAll")}function showme(e){console.log("showme");var l,n=e.substring(7),o=document.getElementsByName("data");for(l=0;l<o.length;l++)o[l].style.display="none";var t=document.getElementsByName("summary");for(l=0;l<t.length;l++)t[l].style.display="none";document.getElementById(n).style.display="block"}')
            with tag('style'):
                text('table, th, td { vertical-align:top; padding: 3px} table {table-layout:fixed} td {word-wrap:break-word} .bs-callout { padding: 5px; margin: 5px 0; border: 1px solid #eee; border-left-width: 5px; border-radius: 3px; font-weight:normal; }.bs-callout-info {border-left-color: #5bc0de;}')

        with tag('body'):
            with tag('nav', klass="navbar navbar-light"  ):
                with tag('div', klass="container-fluid",style="background-color: #F0F8FF;"):
                    with tag('ul', klass="nav nav-pills"):
                        with tag('li', role="presentation"):
                            with tag('a', style="font-weight:bold", href='#', id='anchor_ppcx86', onclick="showme(this.id);"):
                                text('FULL SUMMARY')
                        for i in range(0,len(summary_name),2):
                            key = summary_name[i].split()[1]
                            with tag('li', role="presentation"):
                                with tag('a', style="font-weight:bold", href='#', id='anchor_'+key, onclick="showme(this.id);"):
                                    text(key.upper())
                        with tag('li', role="presentation"):
                            with tag('a', style="font-weight:bold", href='#', id='anchor_developers', onclick="showme(this.id);"):
                                text('DEVELOPERS')
                        with tag('p',role="presentation",style="float:right;color:grey;font-size:13;padding-top:5px"):
                            utcdate = datetime.utcnow().strftime("%d-%m-%Y %H:%M UTC")
                            text(utcdate)
                    with tag('div',style="float:right;color:grey;font-size:12"):
                        text('Notations:')
                        with tag('img',  src=getResultImage("FAILURE"),style="width: 16px; height: 16px;"):
                            text("Build failed ")
                        with tag('img',  src=getResultImage("SUCCESS"),style="width: 16px; height: 16px;"):
                            text("Build success with no failure ")
                        with tag('img',  src=getResultImage("UNSTABLE"),style="width: 16px; height: 16px;"):
                            text("N (M) Build success with N test failures & M unique failures ")
                            
            
            with tag('div', klass="col-sm-2 col-md-2 sidebar",style='table-cell'):
                with tag('div', klass="list-group"):
                    with tag('a', href='#', klass='list-group-item list-group-item-action active', id='anchor_ppcx86', onclick="showme(this.id);"):
                        text('Packages')
                    for job in jobs :
                        job_display_name = str(job).upper()
                        with tag('a', href='#', id='anchor_'+job, klass="list-group-item list-group-item-action", onclick="showme(this.id);",title="Owned by "+devs.get(str(job), "N/A")):
                            j = str(job_display_name)
                            j = j.upper()
                            text(j)
                            
            #Tab for developers list
            with tag('div',style="display: table-cell"):
                with tag('div', klass="panel panel-info" , id='developers', name='summary', style="display:block;font-weight:bold;display:none;"):
                    with tag('div', klass="panel-heading") :
                        with tag('div', klass="panel-title") :
                            text('DEVELOPERS')
                    with tag('div', klass='panel-body') :
                        with tag('table',id="summarytable", klass="table table-striped",style="font-size:15"):
                            for d in developer: 
                                list1 = [key for key,val in devs.items() if d in val]
                                with tag('tr'):
                                    with tag('td',style="width: 100px;font-weight:bold"):
                                        text(d.upper())
                                    with tag('td'):
                                        for s in list1:
                                            with tag('button' ,type="button", klass="btn btn-link btn-xs", id='anchor_'+s,  onclick="showme(this.id);"):
                                                text(s.upper() + " ")
            #This is the main area with the detailed results of the tests                                   
            with tag('div',style="display: table-cell"):
                for job in jobs :
                    print "Procesing Job : " + job
                    xjob = server_url + job_url + job + a_j
                    resp = requests.get(xjob,auth=(user, password)).json()
                    #try:
                    if 'lastCompletedBuild' not in resp.keys() or not resp['lastCompletedBuild']:
                        continue  
                    buildUrl = getBuild(resp)
                    if buildUrl == "" :
                        continue
                    x86_lastBuild=requests.get(buildUrl+a_j,auth=(user, password)).json()
                    env_result = []
                    for env in environment:
                        env_result.append(getFailures(buildUrl+'testReport'+a_j, env, job))
                    
                    with tag('div', id=job, name='data', klass="panel panel-info" ,style="font-weight:bold;display:none;"):
                        with tag('div', klass="panel-heading",style="font-weight:bold;"):
                            text(str(job).upper())
                            with tag('p', role="presentation", align="right",style="padding-left:5px;color:grey;display:inline;font-weight:normal"):
                                text("(",devs.get(job,"N/A"),")")
                        with tag('div', klass='panel-body') :
                            for action in x86_lastBuild['actions'] :
                                if action and action['_class'] == "hudson.plugins.git.util.BuildData" :
                                    revHash = action['lastBuiltRevision']['branch'][0]['SHA1']
                                    revName = action['lastBuiltRevision']['branch'][0]['name']
                                    build_date  = datetime.fromtimestamp(round(x86_lastBuild['timestamp'] / 1000)).strftime("%d-%m-%Y %H:%M UTC")  
                                    with tag('div', klass="bs-callout bs-callout-info"):
                                        with tag('div') :
                                            with tag('b'):
                                                text('Branch Details:')
                                            text( ' {0}'.format(revName))
                                            
                                        with tag('div') :
                                            with tag('b'):
                                                text('Last Revision: ')
                                            text('{0}'.format(revHash))
                                        with tag('div') :
                                            with tag('b'):
                                                text('Last Run: ')
                                            text('{0}'.format(build_date))
                                    break
                            with tag('table' ,width="100%" ,klass="table table-striped",style="font-size:13"):
                                with tag('thead'):
                                    #header
                                    with tag('tr'):
                                        with tag('th', width="10%"):
                                            text('')
                                        for name in summary_name:
                                            with tag('th'):
                                                text(name.upper())
                                                             
                                    #summary
                                with tag('tbody'):
                                    with tag('tr'):
                                        with tag('td'):
                                            text('Summary')
                                        for envDetail in env_result:
                                            with tag('td'):
                                                    with tag('div') :
                                                                text('Total Count : {0}'.format(envDetail['totalCount']))
                                                    with tag('div') :
                                                                text('Failed Count : {0}'.format(envDetail['failedCount']))
                                                    with tag('div') :
                                                                text('Skipped Count : {0}'.format(envDetail['skippedCount']))
                       
                                    #Status
                                    with tag('tr'):
                                        with tag('td'):
                                            text('Result')
                                        i = 0
                                        for envDetail in env_result:
                                            with tag('td'):
                                                if job == "ambari" and i == 0 or job == "ambari" and i == 2:
                                                    text("N/A")
                                                else: 
                                                    with tag('img', src=getResultImage(envDetail['result']),align='top',style="width: 16px; height: 16px;"):
                                                            text()
                                                    text(envDetail['result'])
                                            i += 1
                                    
                                            
                                    #Failures
                                    with tag('tr'):
                                        with tag('td'):
                                            text('Failures')
                                        for envDetail in env_result:   
                                            with tag('td') :
                                                with tag('ol',style="padding-left: 1.0em"):
                                                    for t in envDetail['testErrorName'] :
                                                        with tag('div'):
                                                            with tag('li'):
                                                                text(t)
                                                                                                
                                    #Description
                                    with tag('tr'):
                                        with tag('td'):
                                            text('Description')
                                        for envDetail in env_result:                                        
                                            with tag('td' ) :
                                                with tag('ol',style="padding-left: 1.0em"):
                                                    for t in envDetail['testErrorDesc'] :
                                                        with tag('div'):
                                                            with tag('li'):
                                                                text(t)
                                                                                                

                                    #Unique Failures
                                    with tag('tr'):
                                        with tag('td', style="word-wrap: break-word;min-width: 160px;max-width: 220px;"):
                                            text('Unique Failures')
                                        for i in range(0,len(env_result),2):
                                            with tag('td', style="word-wrap: break-word;min-width: 160px;max-width: 220px;"):
                                                result = [x for x in env_result[i]['testErrorName'] if x not in env_result[i+1]['testErrorName']]
                                                env_result[i]['unique'] = len(result)
                                                with tag('ol',style="padding-left: 1.0em"):
                                                    for t in result :
                                                        with tag('li'):
                                                            with tag('div'):
                                                                text(t)
                                            with tag('td', style="word-wrap: break-word;min-width: 160px;max-width: 220px;"):
                                                result = [x for x in env_result[i+1]['testErrorName'] if x not in env_result[i]['testErrorName']] 
                                                env_result[i+1]['unique'] = len(result)
                                                with tag('ol',style="padding-left: 1.0em"):
                                                    for t in result :
                                                        with tag('li'):
                                                            with tag('div'):
                                                                text(t)
                                                                                
                    z=0
                    for name in summary_name :
                        if name not in summary:
                            summary[name] = []
                        summary[name].append(env_result[z])
                        z += 1
                    #except Exception as e:
                    #    print(e)
                    #    print 'FAILED'

                
                for i in range(0,len(summary_name),2):
                    osname = summary_name[i].split()[1]
                    with tag('div',  klass="panel panel-info" , id=osname, name='summary', style="font-weight:bold;font-size:12;display:none"):
                        with tag('div', klass="panel-heading") :
                            with tag('div', klass="panel-title") :
                                text(osname.upper()+' SUMMARY')
                        with tag('div', klass="bs-callout bs-callout-info"):
                            with tag('div') :
                                with tag('b'):
                                    text('OS: ')
                                if "75" in osname:
                                    text('RHEL 7.5')
                                elif "72" in osname:
                                    text('RHEL 7.2')
                                elif "18" in osname:
                                    text('UBUNTU 18.04')
                                else:
                                    text('UBUNTU 16.04')
                        with tag('table', klass='table table-striped' ,style="font-size:14"):
                            with tag('tbody'):
                                #header
                                with tag('tr'):
                                    with tag('th', ):
                                        text('Package Name')
                                    with tag('th'):
                                        text('PPC')
                                    with tag('th'):
                                        text('X86')
                                    with tag('th'):
                                        text('')
                                for ppc_summary_detail,x86_summary_detail in zip(summary['ppc ' + osname],summary['x86 ' + osname]):
                                    with tag('tr'):
                                        with tag('td'):
                                                with tag('a', href='#', id='anchor_'+ppc_summary_detail['job'], onclick="showme(this.id);"):
                                                    text(ppc_summary_detail['name'])
                                        with tag('td'):
                                            with tag('img', src=getResultImage(ppc_summary_detail['result']),align='top',style="width: 16px; height: 16px;",title=ppc_summary_detail['result']):
                                                text()
                                            if ppc_summary_detail['result'] != "SUCCESS" and ppc_summary_detail['result'] != "ABORTED" :
                                                if ppc_summary_detail['unique'] == 0:
                                                    text(str(ppc_summary_detail['failedCount']))
                                                else:
                                                    text(str(ppc_summary_detail['failedCount']) + " (" + str(ppc_summary_detail['unique']) + ")")
                                        with tag('td'):
                                            with tag('img', src=getResultImage(x86_summary_detail['result']),align='top',style="width: 16px; height: 16px;",title=x86_summary_detail['result']):
                                                text()
                                            if x86_summary_detail['result'] != "SUCCESS" and x86_summary_detail['result'] != "ABORTED" :
                                                if x86_summary_detail['unique'] == 0:
                                                    text(str(x86_summary_detail['failedCount']))
                                                else:
                                                    text(str(x86_summary_detail['failedCount']) + " (" + str(x86_summary_detail['unique']) + ")")
                                        
                                        
                        
                #full summary
                with tag('div', klass="panel panel-info" , id='ppcx86', name='summary', style="display:block;font-weight:bold"):
                    with tag('div', klass="panel-heading") :
                        with tag('div', klass="panel-title") :
                            text('FULL SUMMARY')
                    with tag('table',id="summarytable", klass="table table-striped",style="font-size:14"):
                        with tag('tbody'):
                            #header
                            with tag('tr'):
                                with tag('th'):
                                    text()
                            with tag('tr'):
                                with tag('th'):
                                    text('Package Name')
                                for name in summary_name:
                                    with tag('th'):
                                        text(name.upper())
                            for job_index in range(0, len(summary[name])) :
                                with tag('tr'):
                                    with tag('td'):
                                        with tag('a', href='#', id='anchor_'+summary[name][job_index]['job'], onclick="showme(this.id);"):
                                            text(summary[name][job_index]['name'])
                                    
                                    for name in summary_name :
                                        detail = summary[name][job_index]
                                        res = detail['result']
                                        with tag('td'):
                                            if summary[name][job_index]['name'] == "AMBARI" and name.startswith("ppc ubuntu"):
                                                text("N/A")
                                            else:
                                                with tag('img', title=res, src=getResultImage(res),align='top',style="width: 16px; height: 16px;"):
                                                    text()
                                                if res != "SUCCESS":
                                                    if detail['unique'] == 0:
                                                        text(str(detail['failedCount']))
                                                    else:
                                                        text(str(detail['failedCount']) + " (" + str(detail['unique']) + ")")
                                    


      
    result = doc.getvalue()
    print "Writing result to a file at /var/www/html/ci_report.html"
    with open('/root/poss-ci.github.io/index.html','w') as afile :
        afile.write(result.encode('utf-8'))
    with open('/var/www/html/ci_report.html','w') as afile :
        afile.write(result.encode('utf-8'))

    print 'The script took {0}'.format(datetime.now() - startTime)

startTime = datetime.now()
copyfile("./helper.js", "/var/www/html/helper.js")
config = configparser.ConfigParser()
config.sections()
config.read('ciconfig.ini')
server_url=config['DEFAULT']['server_url']
user=config['DEFAULT']['user']
password=config['DEFAULT']['password']
main()
