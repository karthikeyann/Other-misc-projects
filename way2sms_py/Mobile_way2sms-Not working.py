# -*- coding: utf-8 -*-
"""
Created on Tue May 19 05:32:29 2015

@author: Karthikeyan
"""

import urllib
import cookielib, urllib2
import os
import re


class WayManager:
   'Common base class for all WayManagers'
   loggedin = 0
   loggedinUser = ""
   loginurl= "m1.way2sms.com/Login1.action"
   logindata = "username=9876543210&password=password" #POST
   necessaryurl = "m1.way2sms.com/jsp/SingleSMS.jsp"
   necessarydata = "Token=5BAE9A6D7FCA89B5B2A640AB0874C930.w802" #GET
   #sendsmsurl = "m1.way2sms.com/jsp/smstoss.action"
   sendsmsurl = "m1.way2sms.com/jsp/"
   #POST
   sendsmsdata = "smsActTo=smstoss&t_15_k_5=bUkTpP&a_m_p=snsms&w2sms=w2sms&pjkdws=sdfa43gf35f&m_15_b=BJTgHMSt&girkuTG=&bUkTpP=5BAE9A6D7FCA89B5B2A640AB0874C930.w802&adno=1&Token=5BAE9A6D7FCA89B5B2A640AB0874C930.w802&textfield2=%2B91&BJTgHMSt=9876543210&textArea=hi+this+is+karthik.+%0D%0ACheck+your+message.+&txtLen=98"
   logouturl = "m1.way2sms.com/LogOut"
   #POST
   COOKIEFILE = 'cookies.txt'
   def __init__(self, name, passwd):
      self.userName = name
      self.password = passwd
      WayManager.loggedin = 0
      self.JSESSIONID = ""
      self.cj = cookielib.LWPCookieJar()
      '''if os.path.isfile(WayManager.COOKIEFILE):
        self.cj.load(WayManager.COOKIEFILE, ignore_discard=True, ignore_expires=False)
        self.extract_JSESSIONID()
        print self.JSESSIONID
        WayManager.loggedin = 1
        WayManager.loggedinUser = name
        #TODO validate cookie valid?
      '''
      self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
      self.opener.addheaders = [('User-agent', 'Mozilla/5.0 (iPhone; U; CPU iPhone OS 3_0 like Mac OS X; en-us) AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0 Mobile/7A341 Safari/528.16')]
      
      
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
       #print self.response.read()
       print self.response.info()
       #save cookie to file and revert back while openning app again.
       self.cj.save(WayManager.COOKIEFILE, ignore_discard=True, ignore_expires=False)
       self.extract_JSESSIONID()
       return 1
       
   def Necessary_URL(self):
       #TODO
       self.extract_JSESSIONID()
       Token = self.JSESSIONID.split('~')[1]
       values = {'Token': Token}
       data = urllib.urlencode(values) 
       # Error handling
       try:
           self.response = self.opener.open("http://"+WayManager.necessaryurl, data)
       except urllib2.URLError, e:
           print e.reason
           return 0
       text_response = self.response.read()
       with open("Output.txt", "w") as text_file:
           text_file.write(text_response)
       # process text_response
       self.sendsmsdata = {}
       [_, formval] = self.get_tag(text_response, "<form", "</form>")
       [formval, script] = self.get_tag(formval, "<script", "</script>")
	   # TODO FIXME fields parsing has some problem. (sometimes the fields or values are missing during parsing.)
       #TODO test this. (tricky code)
       '''while True:
           [script, secval] =  self.get_tag(script, "var", 'id", "')
           if secval == "":
               break
           name  = self.get_field(secval, 'setAttribute("name", ')
           value = self.get_field(secval, 'setAttribute("value", ')
           if name != "":
               self.sendsmsdata[name]=value'''
       while True:
           [formval, secval] =  self.get_tag(formval, "<input", ">")
           if secval == "":
               break
           name  = self.get_field(secval, "name=")
           value = self.get_field(secval, "value=")
           if name != "":
               self.sendsmsdata[name]=value
       while True:
           [formval, secval] =  self.get_tag(formval, "<textarea", "</textarea>")
           if secval == "":
               break
           name  = self.get_field(secval, "name=")
           #TODO get value correctly
           value = self.get_field(secval, "value=")
           if name != "":
               self.sendsmsdata[name]=value
       # post processing (javascript magic from way2sms)
       # document.getElementById(document.getElementById("t_15_k_5").value).value = tkn;
       self.sendsmsdata[self.sendsmsdata["t_15_k_5"]]=self.sendsmsdata["Token"]
       #print formval
       print self.sendsmsdata
       #TODO after processing
       if self.sendsmsdata == {}:
           return 0
       return 1

   def SendSMS_URL(self, MobileNo, Message):
       values = self.sendsmsdata
       validMobNo = self.GetMobNo(MobileNo)
       if validMobNo == None:
           raise("Invalid Mobile number:"+MobileNo)
       if len(Message)>140:
           raise("Message length > 140 not accepted")
       #TODO split and send longer messages
       #var reqMob = document.getElementById(document.getElementById("m_15_b").value).value;
       values[values["m_15_b"]]=validMobNo
       values["Send"]="Sending.."
       values["textArea"]=Message
       values["txtLen"]=len(Message)
       Finalsendsmsurl = WayManager.sendsmsurl + values["smsActTo"] + ".action"
       data = urllib.urlencode(values) 
       # Error handling
       
       #http://site24.way2sms.com/smstoss.action
       #ssaction=ss&Token=365BE1AFD809BABBBF9B1368E4DE2079.w813&mobile=9876543210&message=test+sms5&msgLen=131
       '''
       try:
           self.response = self.opener.open("http://"+Finalsendsmsurl, data)
       except urllib2.URLError, e:
           print e.reason
           return 0
       print self.response.info()
       text_response = self.response.read()
       with open("Response.txt", "w") as text_file:
           text_file.write(text_response)
       '''
       # Display all POST data.
       for keys in values:
           print keys,":",values[keys]
       return 1

       self.extract_JSESSIONID()
       Token = self.JSESSIONID.split('~')[1]
       values = {'Token': Token, 'SentMessage' : 'Message has been submitted successfully'}
       data = urllib.urlencode(values) 
       # Error handling
       #url = "http://site24.way2sms.com/smscofirm.action"
       #"?SentMessage=test+sms2&Token=6A9940A236C56B49901F353895AF76B7.w802&status=0
       #url = "m1.way2sms.com/singles.action"
       #?Token="+document.getElementById("Token").value+"&conf=1";
       url = 'm1.way2sms.com/generalconfirm.action'
       #?SentMessage=Message+has+been+submitted+successfully&Token=A9E25703D5A3D14888C209BE67F00867.w801
       try:
           self.response = self.opener.open("http://"+url, data)
       except urllib2.URLError, e:
           print e.reason
           return 0
       text_response = self.response.read()
       with open("confirm.txt", "w") as text_file:
           text_file.write(text_response)
       
       return 1

   def Logout_URL(self):
       try:
           self.response = self.opener.open("http://"+WayManager.logouturl)
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
       #TODO
       WayManager.loggedin = self.Login_URL()
       #save cookie data to file and revert back while openning app again.
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
way1.Necessary_URL()
way1.SendSMS("9876543210", "This is test sms3")
print way1.Logout()
way1.printLoggedStatus()
