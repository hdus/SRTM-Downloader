# -*- coding: utf-8 -*-
"""
/***************************************************************************
                             -------------------
begin                : 2016-12-02
copyright            : (C) 2016 by Dr. Horst Duester
email                : horst.duester@kappasys.ch
 ***************************************************************************/
"""
from configparser import ConfigParser
import os


class Metadata():
    
    def __init__(self):
        self._read_metadata()
    
    def _read_metadata(self):
        self.result = {}
        with open("%s/metadata.txt" % (os.path.dirname(os.path.dirname( __file__)))) as f:
            config = ConfigParser()
            config.read_file(f)
            options = config.options('general')
            for option in options:
                try:
                    self.result[option] = config.get('general', option)
                except:
                    self.result[option] = ''            
                
    
    def version(self):
        return self.result['version']
        
    def description(self):
        return self.result['description']
        
        
    def name(self):
       return self.result['name']
       
    def date(self):
       return self.result['date']       
       
    def qgisMinimumVersion(self):
       return self.result['qgisMinimumVersion']
       
    def qgisMaximumVersion(self):
       return self.result['qgisMaximumVersion']
       
    def author(self):
       return self.result['author']
       
    def email(self):
       return self.result['email']
       
    def homepage(self):
       return self.result['homepage']
       
    def tracker(self):
        return self.result['tracker']
        
    def repository(self):
        return self.result['repository']               
        
    def changelog(self):
        try:
            return self.result['changelog']        
        except:
            return ''
        
    
