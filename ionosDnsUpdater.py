import requests
import io
from pyquery import PyQuery  
from datetime import datetime
import os
import secrets
import sys



fn = os.getcwd() + r'/' + '1-1_loginPage.html'
if os.path.exists(fn):
    os.remove(fn)

fn = os.getcwd() + r'/' + '1-2_loginPageRobotCheck.html'
if os.path.exists(fn):
    os.remove(fn)

fn = os.getcwd() + r'/' + '2-welcomePage.html'
if os.path.exists(fn):
    os.remove(fn)

fn = os.getcwd() + r'/' + '3-dnsEditPage.html'
if os.path.exists(fn):
    os.remove(fn)

fn = os.getcwd() + r'/' + '4-dnsPostPage.html'
if os.path.exists(fn):
    os.remove(fn)



lastKnownIonosEntry = ''

try:
    lastKnownIonosEntry =  open( os.getcwd() + r'/' + 'lastKnownIonosEntry.txt','r').read()
except:
    pass

publicIp = requests.get('https://api.ipify.org').text

if publicIp != lastKnownIonosEntry:
    print("last known IONOS ip entry doesn't match, will update")
else:
    print("The last known IONOS ip entry matches your public IP address. If you want to force an update to IONOS, delete the file 'lastKnownIonosEntry.txt'. Now Exiting...")
    sys.exit()

userAgent = r"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36"
#userAgent = r"Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko"

fn = os.getcwd() + r'/' + 'account-locked'
if os.path.exists(fn):
    print("your account is locked. Delete the 'account-locked' file once you unlock your account...exiting")
    sys.exit()


loginUrl = r'https://login.ionos.com'

              
headers = {
    'User-Agent':userAgent
}

with requests.Session() as s:
    print('Getting login page payload')
    loginPage = s.get(loginUrl, headers=headers)
    filePath = os.getcwd() + r'/' + '1-1_loginPage.html'
    f = open(filePath, 'w')
    f.write(loginPage.text)
    f.close()    

    pq = PyQuery(loginPage.text)
    #csrf = pq('#login-form > input[type="hidden"]:nth-child(4)').attr('value')#content > div > div > div:nth-child(9) > div:nth-child(1) > div > form > input[type="hidden"]:nth-child(6)
    csrf = pq('#content > div > div > div:nth-child(9) > div:nth-child(1) > div > form > input[type="hidden"]:nth-child(6)').attr('value')
    #fp = pq('#login-form-fp').attr('value')
    fp = pq('#content > div > div > div:nth-child(9) > div:nth-child(1) > div > form > input[type="hidden"]:nth-child(3)').attr('value')
    fp = ''

    loginPayload = {
        '__lf': 'Login',
        '__sendingdata':'1',
        'oaologin.fp': fp,
        'oaologin.autofillUsername' :'',
        'oaologin.autofillPassword' : '',
        'oaologin.csrf': csrf,
        'oaologin.username': secrets.domainName,
        'oaologin.password': secrets.pw,
        'oaologin.rememberme': 'true'
        # '__SBMT:d0e799d0':''
    }

    print('Posting back login info')
    welcomePage = s.post(loginUrl, data=loginPayload, headers=headers)


    additionalData = ''

    if  'Last name' in welcomePage.text:
        additionalData = secrets.lastName
    elif 'First name' in welcomePage.text:
        additionalData = secrets.firstName
    # elif 'City' in welcomePage.text:
    #     additionalData = secrets.cityName
    elif 'zip code of your customer address' in welcomePage.text:
        additionalData = secrets.zip
    elif 'account-locked' in welcomePage.text:
        print('Looks like your account is locked, requesting unlock email')
        loginPayload = {
            '__lf': 'login',
            '__sendingdata':'1',
            'oaologin.fp': fp,
            'oaologin.autofillUsername' :'',
            'oaologin.autofillPassword' : '',
            'oaologin.csrf': csrf,
            'oaologin.username': secrets.domainName,
            'oaologin.password': secrets.pw,
            'oaologin.rememberme': 'true',
            'email.sendUnlockEmail': 'true'
        }
        s.post(loginUrl + '/account-locked', data=loginPayload, headers=headers)
        print('Check your email and try again later.')
        filePath = os.getcwd() + r'/' + 'account-locked'
        f = open(filePath, 'w')
        f.write('your account is locked, this wont run again until you delete this file')
        f.close()  
        sys.exit()
        

    if  additionalData == '':
        filePath = os.getcwd() + r'/' + '2-welcomePage.html'
        f = open(filePath, 'w')
        f.write(welcomePage.text)
        f.close()  
    else:
        print('Ionos is doing a robot check...good thing you\'re a klever robot. Posting back additional data: ' + additionalData)
        filePath = os.getcwd() + r'/' + '1-2_loginPageRobotCheck.html'
        f = open(filePath, 'w')
        f.write(welcomePage.text)
        f.close()  

        pq = PyQuery(loginPage.text)
        #csrf = pq('#login-form > input[type="hidden"]:nth-child(4)').attr('value')#content > div > div > div:nth-child(9) > div:nth-child(1) > div > form > input[type="hidden"]:nth-child(6)
        csrf = pq('#content > div > div > div:nth-child(9) > div:nth-child(1) > div > form > input[type="hidden"]:nth-child(6)').attr('value')
        #fp = pq('#login-form-fp').attr('value')
        fp = pq('#content > div > div > div:nth-child(9) > div:nth-child(1) > div > form > input[type="hidden"]:nth-child(3)').attr('value')
        fp = ''

        loginPayload = {
            '__lf': 'login',
            '__sendingdata':'1',
            'oaologin.fp': fp,
            'oaologin.autofillUsername' :'',
            'oaologin.autofillPassword' : '',
            'oaologin.csrf': csrf,
            'oaologin.username': secrets.domainName,
            'oaologin.password': secrets.pw,
            'oaologin.rememberme': 'true',
            'oaologin.additionaldata' :additionalData
        }

        robotCheck = s.post(loginUrl, data=loginPayload, headers=headers)
        filePath = os.getcwd() + r'/' + '2-welcomePage.html'
        f = open(filePath, 'w')
        f.write(robotCheck.text)
        f.close()  

    print('Getting dns settings from IONOS')
    dnsEditPage = s.get(secrets.editPageURL, headers=headers)
    filePath = os.getcwd() + r'/' + '3-dnsEditPage.html'
    f = open(filePath, 'w')
    f.write(dnsEditPage.text)
    f.close()  

    pq2 = PyQuery(dnsEditPage.text)
    oneAnd1Ip = pq2('#recordValue').attr('value')
    
    if  oneAnd1Ip is None:
        print("problem getting IP from IONOS, try manually logging in.")
        sys.exit()

    filePath = os.getcwd() + r'/' + 'lastKnownIonosEntry.txt'
    f = open(filePath, 'w')
    f.write(oneAnd1Ip)
    f.close()

    filePath = os.getcwd() + r'/' + 'log.txt'
    f = open(filePath, 'a')
    f.write(datetime.today().strftime('%Y-%m-%d-%H:%M:%S') +' ' + oneAnd1Ip +'\n')
    f.close()


    print('My public IP address is:', publicIp)
    print('The DNS entry on IONOS is:', oneAnd1Ip)

    if publicIp != oneAnd1Ip:
        print("IP addresses differ, updating IONOS")
        editDnsPayload = {
            '__sendingdata':'1',
            'record.forWwwSubdomain':'true',
            'record.value':publicIp,
            'domainName': secrets.domainName,
            'record.ttl': secrets.ttlInSeconds
        }
        dnsPostPage = s.post(secrets.editPageURL, data=editDnsPayload, headers=headers)
        filePath = os.getcwd() + r'/' + '4-dnsPostPage.html'
        f = open(filePath, 'w')
        f.write(dnsPostPage.text)
        f.close()  
    else:
        print("IP Addresses are the same, no further action required.")
    print('done')
   