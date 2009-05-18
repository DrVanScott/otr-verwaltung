#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, os.path, sys
import ConfigParser

import otrpath

class Plugin:       
    Name = "Name of Plugin"
    Desc = "Description of Plugin"
    Author = "Author of Plugin"
    Configurable = False
    Config = { } # key-value-pairs for configuration
    
    def __init__(self, app):
        """ Don't override the constructor. Do the intial work in 'enable'. """
        self.app = app       # for api access        
    
    def enable(self):
        """ This is called when the plugin is enabled. 
            You can connect to callbacks and setup gui elements. """
        pass
        
    def disable(self):
        """ This is called when the plugin is disabled. 
            Revert your actions. """
        pass
        
    def configurate(self):
        """ This is called when the user wants to configure the plugin.
            You might want to display a dialog to the user.
            Note: Set CONFIGURABLE to True.
            Note: Use the Config dict to let the plugin system save your settings. """
        pass        
                
class PluginSystem:
    
    def __init__(self, app, conf_path, enabled_plugins=''):
        self.plugins = {} # name : plugin instance
        self.enabled_plugins = [plugin for plugin in enabled_plugins.split(':') if plugin] # list of names
        self.conf_path = conf_path
       
        # read config
        print "[Plugins] Config path: ", conf_path
        self.parser = ConfigParser.SafeConfigParser()
        if os.path.isfile(conf_path):           
            self.parser.read(conf_path)            
       
        plugin_paths = otrpath.get_plugin_paths()
        print "[Plugins] Paths to search: ", plugin_paths
                              
        for path in plugin_paths:                  
            sys.path.insert(0, path)           
            
            for file in os.listdir(path):
                plugin_name, extension = os.path.splitext(file)
                
                if extension == ".py":                        
                    plugin_module = __import__(plugin_name)
                    # instanciate plugin
                    self.plugins[plugin_name] = getattr(plugin_module, plugin_name)(app)
                    
                    config = {}
                    if self.parser.has_section(plugin_name):
                        for key, value in self.parser.items(plugin_name):
                            self.plugins[plugin_name].Config[key] = value
                    
                    print "[Plugins] Found: ", plugin_name
                        
        for plugin in self.enabled_plugins:
            if not plugin in self.plugins.keys():
                print "[Plugins] Error: Plugin >%s< not found." % plugin
                self.enabled_plugins.remove(plugin)                        
            else:
                self.plugins[plugin].enable()
                print "[Plugins] Enabled: ", plugin

    def enable(self, name):
        if name not in self.enabled_plugins:
            self.enabled_plugins.append(name)
        self.plugins[name].enable()
    
    def disable(self, name):
        self.enabled_plugins.remove(name)
        self.plugins[name].disable()
    
    def save_config(self):
        for plugin_name, plugin in self.plugins.iteritems():
            if not self.parser.has_section(plugin_name):
                self.parser.add_section(plugin_name)
            
            for option, value in plugin.Config.iteritems():                
                self.parser.set(plugin_name, option, value)
                print "[Plugins] Config (%s): set %s to %s" % (plugin_name, option, value)
                
        self.parser.write(open(self.conf_path, 'w'))
        
    def get_enabled_config(self):
        return ":".join(self.enabled_plugins)
