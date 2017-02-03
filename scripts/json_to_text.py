#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" json_to_text.py


"""

import json
import os
import sys
import glob

class Data(object):
    def __init__(self):
        self.groups = {}
        self.options = {}

class OptData(object):
    def __init__(self, group, source, name, klass, default, deprecated, helpstr, multi, required):
        self.group = group
        self.sources = [source]
        self.name = name
        self.klass = klass
        self.default = default
        self.deprecated = deprecated
        self.helpstr = helpstr
        self.multi = multi
        self.required = required
        
        
def main():

    data = Data()
    
    for file_or_dir in sys.argv[1:]:
        if not os.path.exists(file_or_dir):
            continue
        if os.path.isfile(file_or_dir):
            data = load_file(data, file_or_dir)
        elif os.path.isdir(file_or_dir):
            data = walk_dir(data, file_or_dir)

    dump(data)
            
def load_file(data, filename):
    fp = open(filename)
    js = json.load(fp)
    fp.close()

    source = js["In"]

    for gn in js["Out"]["groups"].keys():
        if gn not in data.groups:
            data.groups[gn] = js["Out"]["groups"][gn]
            data.options[gn] = {}

    for gn in js["Out"]["options"].keys():
        for on in js["Out"]["options"][gn].keys():
            if on not in data.options[gn]:
                data.options[gn][on] = []
            append = True
            info = js["Out"]["options"][gn][on]
            for opt in data.options[gn][on]:
                if info["help"] == opt.helpstr:
                    opt.sources.append(source)
                    append = False
            if append:
                data.options[gn][on].append(
                    OptData(source, gn, on, info["__class__"], info["default"],
                            info["deprecated_for_removal"], info["help"],
                            info["multi"], info["required"])
                )
    return data
            
def walk_dir(data, directory):
    pattern = directory + "/*"
    for path in glob.glob(pattern):
        if os.path.isdir(path):
            data = walk_dir(data, path)
        elif path.endswith(".json"):
            data = load_file(data, path)
    return data

def dump(data):
    for gn in sorted(data.groups.keys()):
        print("[%s]" % gn)
        if type(data.groups[gn]) == dict:
            print(co(data.groups[gn]["title"]))
            print(co(data.groups[gn]["help"]))
        print("")
        for on in sorted(data.options[gn]):
            for op in data.options[gn][on]:
                print("%s = %s" % (op.name, op.default))
                print(co("class:      %s" % op.klass))
                print(co("deprecated: %s" % op.deprecated))
                print(co("multi:      %s" % op.multi))
                print(co("required:   %s" % op.required))
                print(co("help:"))
                print(co(op.helpstr))
                print("")
        print("\n")
                              
def co(s, prefix="# "):
    return prefix + str(s).strip().replace("\n", "\n" + prefix)
        
if __name__ == "__main__":
    main()
