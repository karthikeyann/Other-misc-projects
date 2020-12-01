# -*- coding: utf-8 -*-
"""
Created on Tue May 19 05:32:29 2015

@author: Karthikeyan
"""

import urllib
import cookielib, urllib2
import os
import re
import time

class WayManager:
   'Common base class for all WayManagers'
   loggedin = 0
   loggedinUser = ""
   loginurl= "site21.way2sms.com/Login1.action"
   logindata = "username=9876543210&password=********" #POST
   mainurl = "site21.way2sms.com/main.action?section=s&Token=E401969F43956BE9E610815A4512EB09.w807&vfType=register_verify"
   sendsmsurl = "site21.way2sms.com/smstoss.action"
   #POST
   sendsmsdata= "ssaction=ss&Token=E401969F43956BE9E610815A4512EB09.w807&mobile=9876543210&message=test+sms7&msgLen=131"
   confirmurl = "site21.way2sms.com/smscofirm.action"
   confirmdata= "SentMessage=test+sms7&Token=E401969F43956BE9E610815A4512EB09.w807&status=0"
   logouturl  = "site21.way2sms.com/entry?ec=0080&id=jtni"
   log = 0
   #POST
   COOKIEFILE = 'cookies.txt'
   def __init__(self, name, passwd):
      self.userName = name
      self.password = passwd
      WayManager.loggedin = 0
      self.JSESSIONID = ""
      self.cj = cookielib.LWPCookieJar()
      if os.path.isfile(WayManager.COOKIEFILE):
        self.cj.load(WayManager.COOKIEFILE, ignore_discard=True, ignore_expires=False)
        self.extract_JSESSIONID()
        print self.JSESSIONID
        WayManager.loggedin = 1
        WayManager.loggedinUser = name
        #TODO validate cookie valid?
      self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
      #self.opener.addheaders = [('User-agent', 'Mozilla/5.0 (iPhone; U; CPU iPhone OS 3_0 like Mac OS X; en-us) AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0 Mobile/7A341 Safari/528.16')]
      self.opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0')]
      
      
   # HELPER FUNCTIONS
   def extract_JSESSIONID(self):
      for cookie in self.cj:
           print cookie.name, cookie.value, cookie.domain #etc etc
           if cookie.name == "JSESSIONID":
               self.JSESSIONID = cookie.value
      if(self.JSESSIONID == ""):
          raise ValueError('JSESSIONID is empty in cookiejar')
   
   @staticmethod
   def get_tag(htmldata, tag_start, tag_stop):
       start_loc = htmldata.find(tag_start)
       stop_loc  = htmldata.find(tag_stop, start_loc+len(tag_start))       
       if ( start_loc == -1 or stop_loc == -1):
           return [htmldata,""]
       else:
           return [ htmldata[0:start_loc]+htmldata[stop_loc+len(tag_stop):], htmldata[start_loc:stop_loc+len(tag_stop)] ]
   
   @staticmethod
   def get_field(htmldata, field):
       #field = field +  "="
       start_loc = htmldata.find(field)
       if(start_loc==-1):
           return ""
       if ( htmldata[start_loc+len(field)] == "\""):
           start_loc = start_loc + 1+ len(field)
           stop_loc = htmldata.find("\"", start_loc)
       elif(htmldata[start_loc+len(field)] == "\'" ):
           start_loc = start_loc + 1+ len(field)
           stop_loc = htmldata.find("\'", start_loc)
       else:
           start_loc = start_loc + len(field)
           stop_loc = htmldata.find(" ", start_loc)
       if (stop_loc == -1):
           return ""
       return htmldata[start_loc:stop_loc]
   
   @staticmethod
   def GetMobNo(MobNo):
       m = re.match("^(91|\+91|0|\+0|\+)?([987][0-9]{9})$", MobNo)
       if (m != None ) :
           return m.group(2)
       else:
           return None
   
   # CORE FUNCTIONS
   def Login_URL(self):
       values = {'username': self.userName, 'password': self.password}
       data = urllib.urlencode(values) 
       # Error handling
       try:
           self.response = self.opener.open("http://"+WayManager.loginurl, data)
       except urllib2.URLError, e:
           print e.reason
           return 0
       if WayManager.log:
           #print self.response.read()
           print self.response.info()
       #save cookie to file and revert back while openning app again.
       #TODO set extra username Cookie
       #TODO extract logged in username also from cookie
       self.cj.save(WayManager.COOKIEFILE, ignore_discard=True, ignore_expires=False)
       self.extract_JSESSIONID()
       return 1

   def SendSMS_URL(self, MobileNo, Message):
       values = self.sendsmsdata
       validMobNo = self.GetMobNo(MobileNo)
       if validMobNo == None:
           print "Invalid Mobile number:", MobileNo
           return 0
       if len(Message)>140:
           print "Message length > 140 not accepted. length=", len(Message)
           return 0
       #TODO split and send longer messages
       #http://site24.way2sms.com/smstoss.action
       #ssaction=ss&Token=365BE1AFD809BABBBF9B1368E4DE2079.w813&mobile=9876543210&message=test+sms5&msgLen=131
       self.extract_JSESSIONID()
       Token = self.JSESSIONID.split('~')[1]
       values = {'ssaction' : 'ss'}
       values["ssaction"]="ss"
       values["mobile"]=validMobNo
       values["Token"]=Token
       values["message"]=Message
       values["msgLen"]=140-len(Message)
       data = urllib.urlencode(values) 
       # Error handling
       try:
           self.response = self.opener.open("http://"+WayManager.sendsmsurl, data)
       except urllib2.URLError, e:
           print e.reason
           return 0
       if WayManager.log:
           print self.response.info()
           text_response = self.response.read()
           with open("Response.txt", "w") as text_file:
               text_file.write(text_response)
               # Display all POST data.
               for keys in values:
                   print keys,":",values[keys]
       '''
       values = {'Token': Token, 'SentMessage' : Message, 'status' : "0"}
       data = urllib.urlencode(values) 
       # Error handling
       try:
           self.response = self.opener.open("http://"+WayManager.confirmurl, data)
       except urllib2.URLError, e:
           print e.reason
           return 0
       if WayManager.log:
           text_response = self.response.read()
           with open("confirm.txt", "w") as text_file:
               text_file.write(text_response)
       '''
       return 1

   def Logout_URL(self):
       try:
           self.response = self.opener.open("http://"+WayManager.logouturl)
           if os.path.isfile(WayManager.COOKIEFILE):
               os.remove(WayManager.COOKIEFILE)
       except urllib2.URLError, e:
           print e.reason
           return 0
       return 1

   # INTERFACE FUNCTIONS
   def displayCredentials(self):
      print "User Name : ", self.userName,  ", Password: ", self.password
      
   def Login(self):
       print "Login try for user ", self.userName
       if(WayManager.loggedin):
           print "Already Logged in user:",WayManager.loggedinUser
           if (WayManager.loggedinUser != self.userName):
               print "Logging out"
               self.Logout()
           else:
               #TODO validate login
               return 1;
       print "Logging in(web) new user ", self.userName
       WayManager.loggedin = self.Login_URL()
       #TODO validate login
       return WayManager.loggedin;

   def printLoggedStatus(self):
     if WayManager.loggedin:
         print "Logged in"
     else:
         print "Logged out"
 
   def SendSMS(self, MobileNumber, Message):
       if self.SendSMS_URL(MobileNumber, Message):
           return 1
       else:
           print "Sending SMS failed"
           return 0
       
   def Logout(self):
      if self.Logout_URL():
          #TODO delete previous saved userdata.
          WayManager.loggedin = 0;
          return 1
      else:
          return 0

   def CheckLogin(self):
       return WayManager.loggedin


way1 = WayManager("9876543210", "password")
way1.displayCredentials()
way1.Login()
way1.printLoggedStatus()
num = str(input("Mobile  Number :"))
msg = str(raw_input("Message to send:"))
#way1.Necessary_URL()
way1.SendSMS(num, msg)
#way1.SendSMS("9876543210", "Test SMS sent by Karthik at:" + time.strftime("%c"))
#print way1.Logout()
way1.printLoggedStatus()