import cast.analysers.ua
from cast.analysers import log as Print
from cast.application import   ReferenceFinder
import xml.etree.ElementTree as ET
import re
import os
import random
from pathlib import Path


class mqsExtension(cast.analysers.ua.Extension):
    
    def _init_(self):
        self.filename = ""
        self.package = ""
        self.classname = ""
        self.xmlfile = ""
        self.file = ""    
        self.initial_crc =  None
        self.file_ref=""
        self.extnls=[]
        self.parentOBJ=None
        self.parentOBJtwo=None
        self.counter = ""
        return

    def start_analysis(self):
        Print.info("mqs : Running extension code start")
        pass
    
    def start_file(self,file):
        Print.info("file start")
        s= self.get_plugin()
        #logging.info(str(s.get_plugin_directory()))
        self.xmlfile =str(s.get_plugin_directory())+ "\\mqsparsedefine.xml" 
        Print.info(str(self.xmlfile));
        try:
           
            if (os.path.isfile(self.xmlfile)):
                    tree = ET.parse(self.xmlfile, ET.XMLParser(encoding="UTF-8"))
                    root=tree.getroot()
                    
                    for group in root.findall('Search'):
                        sbefore = group.find('RegexPatternBefore').text
                        safter = group.find('RegexPatternAfter').text
                        sregex = group.find('RegexPattern').text
                       
                        if sbefore is None:
                            sbefore=""
                        if  safter is None:
                            safter =""
                        Print.debug(str(sbefore)+"---"+str(sregex)+ "---"+str(safter))
                        
                        sextfile = group.find('RefFileExtension').text
                                        
                        if file.get_name().endswith(sextfile):
                            Print.info('Scanning mqs  file :'+str(Path(file.get_path()).name))
                            if (os.path.isfile(file.get_path())):
                                sobjname = group.find('CastCustomObjName').text 
                                self.parsemqsuses( file.get_path(), file, sobjname,sbefore, safter,sregex );
                                
                                  
                       
             
        except Exception as e:
            Print.info(": Error mqs extension  set : %s", str(e))  
             
              
    
  
    
    def parsemqsuses(self, mqsfile, file, objname, bref,aref, refkey): 
        try :
            #Print.info("file scan uses "+Path(file.get_path()).name)
            rf = ReferenceFinder()
            greferences = []
            rf.add_pattern('usesexport', before= bref, element = refkey, after=aref)
            greferences += [reference for reference in rf.find_references_in_file(mqsfile)]
            for ref in greferences:
                
                try:
                    cleankey= re.sub('[^0-9a-zA-Z]+', '', refkey)
                    if ref.value.find(cleankey) is not -1:
                        response = ref.value.replace(cleankey, '')
                        gsobj = cast.analysers.CustomObject()
                        cleanvalue= re.sub('[^0-9a-zA-Z.]+', '', response)
                        gsobj.set_name(str(response.strip()))
                        gsobj.set_type(objname)
                        gsobj.set_parent(file)
                        parentFile = file.get_position().get_file() 
                        self.fielPath = parentFile.get_fullname()
                        gsobj.set_guid(response+str(Path(file.get_path()).name)+str(random.randint(1, 200))+str(random.randint(1, 200)))
                        gsobj.save()
                        bookmark = cast.analysers.Bookmark(file, 1,1,-1,-1)
                        gsobj.save_position(bookmark)
                        Print.info(file.get_path()+"  Save object "+ objname+" :"+cleanvalue)
                        
                       
                             
                except ValueError:
                    Print.info ("error loading mqs2 uses")
        except:
            return   
     
                
     
    def end_analysis(self):
        Print.info("mqs : Running extension code end") 
       
        pass                             