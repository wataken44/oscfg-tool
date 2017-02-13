#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" extract_opts.py


"""

import json
import os
import sys

from optparse import OptionParser
from importlib.machinery import SourceFileLoader

from oslo_config import cfg

def main():
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="input_filename")
    parser.add_option("-I", dest="input_base_dir")
    parser.add_option("-O", dest="output_base_dir")

    (options, args) = parser.parse_args()

    if len(args) == 3:
        input_filename = os.path.abspath(args[0])
        input_base_dir = os.path.abspath(args[1])
        output_base_dir = os.path.abspath(args[2])
    else:
        input_filename = os.path.abspath(options.input_filename)
        input_base_dir = os.path.abspath(options.input_base_dir)
        output_base_dir = os.path.abspath(options.output_base_dir)

    check_input_in_base(input_filename, input_base_dir)

    output_dir = get_output_dir(input_filename, input_base_dir, output_base_dir)
    create_output_dir(output_dir)

    extract_opts(input_filename, input_base_dir, output_dir)

def check_input_in_base(input_filename, input_base_dir):
    rel = os.path.relpath(input_filename, input_base_dir)
    if rel.find("..") >= 0:
        sys.exit(1)

def get_output_dir(input_filename, input_base_dir, output_base_dir):
    rel = os.path.relpath(input_filename, input_base_dir)
    return os.path.dirname(os.path.join(output_base_dir, rel))

def create_output_dir(output_dir):
    os.system("mkdir -p %s" % output_dir)

lfp = None
def log_open(filename):
    global lfp
    lfp = open(filename, "w")

def log_write(s):
    global lfp
    lfp.write(s)

def log_close():
    global lfp
    lfp.close()
    
def extract_opts(input_filename, input_base_dir, output_dir):
    r = os.path.splitext(os.path.basename(input_filename))[0]
    output_filename = output_dir + "/" + r + ".json"
    log_filename = output_dir + "/" + r + ".log.txt"

    log_open(log_filename)
    
    sfl = None

    
    try:
        rp = os.path.relpath(input_filename, input_base_dir)
        mn = os.path.splitext(rp)[0].replace("/",".")

        log_write('SourceFileLoader("dummy_module", input_filename).load_module() : ')
        dummy_module = SourceFileLoader(mn, input_filename).load_module()
        log_write("succeeded\n")
    except Exception as e:
        log_write("failed\n" + str(e) + "\n")
        log_close()
        return

    opts_arr = [list_opts_from_conf(cfg.CONF)]
    function_appended = False
    
    try:
        for fn in dir(dummy_module):
            if fn.find("register") < 0 or fn.find("opts") < 0:
                continue
            conf = cfg.ConfigOpts()

            log_write('dummy_module.%s(conf) : ' % fn)
            dummy_module.__getattribute__(fn)(conf)
            log_write("succeeded\n")

            opts_arr.append( list_opts_from_conf(conf) )
            function_appended = True
    except Exception as e:
        log_write("failed\n" + str(e) + "\n")


    try:
        if not function_appended:
            for gv in dir(dummy_module):
                if not gv.endswith("OPTS"):
                    continue
                conf = cfg.ConfigOpts()
                log_write('conf.register_opts(%s) : ' % gv)
                conf.register_opts(dummy_module.__getattribute__(gv))
                log_write("succeeded\n")

                opts_arr.append( list_opts_from_conf(conf) )
        else:
            log_write('global variable search skipped \n')

    except Exception as e:
        log_write("failed\n" + str(e) + "\n")

    try:
        opts2 = {}
        log_write('opts = dummy_module.list_opts() : ')
        opts2 = list_opts_from_opts(dummy_module.list_opts())
        log_write("succeeded\n")

        opts_arr.append(opts2)
    except Exception as e:
        log_write("failed\n" + str(e) + "\n")

    log_write("merge: \n")
    groups, options = merge_opts(opts_arr)

    data = {
        "In": os.path.relpath(input_filename, input_base_dir),
        "Out": {
            "groups": object_to_data(groups),
            "options": object_to_data(options)
        }
    }

    if len(data["Out"]["groups"]) > 0:
        ofp = open(output_filename, "w")
        json.dump(data, ofp, indent=2, sort_keys=True)
        ofp.close()

    log_write("debug: \n")
    for i in range(len(opts_arr)):
        o = opts_arr[i]
        log_write(("opts%d = " % i) + json.dumps(object_to_data(o), indent=2, sort_keys=True) + "\n")
    log_close()
    
def list_opts_from_conf(conf):
    """

    conf: ConfigOpts
    ret: { 'DEFAULT' or ConfigGroup : [ConfigOpt] } # output of dummy_module.list_opts()

    """
    
    ret = {}

    default_opts = []
    for k in conf._opts.keys():
        default_opts.append(conf._opts[k]["opt"])

    if len(default_opts) > 0:
        ret['DEFAULT'] = default_opts

    for n in conf._groups.keys():
        g = conf._groups[n]
        ret[g] = []
        for k in g._opts.keys():
            ret[g].append(g._opts[k]["opt"])

    return ret

def list_opts_from_opts(opts):
    """

    opts: 
      { 'DEFAULT' or ConfigGroup : [ConfigOpt] }
      or
      [('DEFAULT' or ConfigGroup or None, [ConfigOpt])]
    ret: 
      { 'DEFAULT' or ConfigGroup : [ConfigOpt] }
    """

    if type(opts) == dict:
        return opts

    ret = {}
    for opt in opts:
        key = opt[0]
        if key is None:
            key = "DEFAULT"
        ret[key] = opt[1]
    return ret

def merge_opts(opts_arr):
    groups = {}
    options = {}

    for opts in opts_arr:
        for kg in opts.keys(): # kg: str or OptGroup
            name = ""
            if type(kg) == str:
                name = kg
            else:
                name = kg.name # OptGroup.name
            if name not in groups:
                groups[name] = kg
                options[name] = {}

            for ko in opts[kg]:
                if ko.name in options[name]:
                    continue
                options[name][ko.name] = ko
            
    return (groups, options)

def object_to_data(obj):
    if type(obj) == dict:
        data = {}
        for k in obj.keys():
            data[str(k)] = object_to_data(obj[k])
        return data
    elif type(obj) == list or type(obj) == tuple:
        data = []
        for item in obj:
            data.append(object_to_data(item))
        return data
    elif type(obj) == type(type(int)):
        return str(obj)
    elif type(obj) in [type(None), bool, int, type(1<<65), float,
                       complex, type(''), type(u''), type(b'')]:
        return obj
    else:
        data = {}
        for k in dir(obj):
            if k[0] == "_":
                continue
            data[k] = object_to_data(obj.__getattribute__(k))
        data["__class__"] = str(type(obj))
        return data


if __name__ == "__main__":
    main()
