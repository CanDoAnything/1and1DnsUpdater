import requests
import io
from pyquery import PyQuery  
import os
import secrets
import sys


lastknown1and1Entry = ''

try:
    lastknown1and1Entry =  open( os.getcwd() + r'/' + 'lastknown1and1Entry.txt','r').read()
except:
    pass

publicIp = requests.get('https://api.ipify.org').text

if publicIp != lastknown1and1Entry:
    print("last known 1and1 ip entry doesn't match, will update")
else:
    print("The last known 1and1 ip entry matches your public IP address. If you want to force an update to 1and1, delete the file 'lastknown1and1Entry.txt'. Now Exiting...")
    sys.exit()

userAgent = r"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36"

loginUrl = r'https://account.ionos.com'

              
headers = {
    'User-Agent':userAgent
}

with requests.Session() as s:
    print('Getting login page payload')
    loginPage = s.get(loginUrl, headers=headers)
    filePath = os.getcwd() + r'/' + '1-loginPage.html'
    f = open(filePath, 'w')
    f.write(loginPage.text)
    f.close()    

    pq = PyQuery(loginPage.text)
    csrf = pq('#login-form > input[type="hidden"]:nth-child(4)').attr('value')
    fp = pq('#login-form-fp').attr('value')

    loginPayload = {
        '__lf': 'login',
        '__sendingdata':'1',
        'oaologin.username': secrets.domainName,
        'oaologin.password': secrets.pw,
        'oaologin.rememberme': 'true',
        'oaologin.csrf': csrf,
        'oaologin.fp': fp
    }

    print('Posting back login info')
    welcomePage = s.post(loginUrl, data=loginPayload, headers=headers)
    filePath = os.getcwd() + r'/' + '2-welcomePage.html'
    f = open(filePath, 'w')
    f.write(welcomePage.text)
    f.close()  

    print('Getting dns settings from 1and1')
    dnsEditPage = s.get(secrets.editPageURL, headers=headers)
    filePath = os.getcwd() + r'/' + '3-dnsEditPage.html'
    f = open(filePath, 'w')
    f.write(dnsEditPage.text)
    f.close()  

    pq2 = PyQuery(dnsEditPage.text)
    oneAnd1Ip = pq2('#recordValue').attr('value')
    
    if  oneAnd1Ip is None:
        print("problem getting IP from 1and1, try manually logging in.")
        sys.exit()

    filePath = os.getcwd() + r'/' + 'lastknown1and1Entry.txt'
    f = open(filePath, 'w')
    f.write(oneAnd1Ip)
    f.close()  


    print('My public IP address is:', publicIp)
    print('The DNS entry on 1and1 is:', oneAnd1Ip)

    if publicIp != oneAnd1Ip:
        print("IP addresses differ, updating 1and1")
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
   