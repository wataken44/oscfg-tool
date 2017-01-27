#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" setup_env.py


"""

import json
import os
import shutil
import sys

base_dir = os.path.dirname(__file__) + "/"

def main():
    global base_dir 

    create_work_dirs()
    prepare_env_file()

    ifp = open(base_dir + "env.json")
    js = json.load(ifp)
    ifp.close()

    fetch_and_setup(js["openstack"])
    install_package(js["package"])
    
def create_work_dirs():
    for d in ["openstack", "output"]:
        if os.path.exists(d):
            continue
        os.mkdir(d)

def prepare_env_file():
    if (not os.path.exists(base_dir + "env.json")) and os.path.exists(base_dir + "env-sample.json"):
        shutil.copy(base_dir + "env-sample.json", base_dir + "env.json")

def fetch_and_setup(repos):
    for repo in repos:
        name = ""
        tag = None
        if type(repo) == str:
            name = repo
        elif type(repo) == type([]):
            name = repo[0]
            if len(repo) == 2:
                tag = repo[1]
        if not os.path.exists("openstack/" + name):
            os.system("cd openstack; git clone https://github.com/openstack/%s.git; cd .." % name)
        if tag:
            os.system("cd openstack/%s; git checkout refs/tags/%s; cd ../.." % (name, tag))
        os.system("cd openstack/%s; python setup.py install; cd ../.." % name)

def install_package(pkgs):
    for pkg in pkgs:
        os.system("pip install %s " % pkg)
        
if __name__ == "__main__":
    main()
