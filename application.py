#!/usr/bin/env python
#-*- coding: utf-8 -*-

from flask import Flask, render_template, request
from auxiliar import replicationgraphs
import os
import glob
import gzip
import re
import json
import ast

app = Flask(__name__)

@app.route("/",methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route("/second_step",methods=['GET', 'POST'])
def second_step():
    # This is the path that comes from the form
    autosupports_path = request.form.get('autosupports_path')
    if (not autosupports_path):  # if it is empty, we return error
        return (render_template('error.html',error_code="You have not specified any path. Please go back and fill up the field path."))  # Path was empty
    else:
        autosupports_path=autosupports_path+"/"
        
    # This normalizes the path based on the Operating System
    autosupports_path = os.path.normcase(autosupports_path)
  

    files_and_dates_list = []
   
    if not os.path.exists(autosupports_path):
        raise Exception("Path not valid")
    # on the specified path we want to search for all autosupport files
    autosupports_files_path = autosupports_path+"/autosupport*"
    autosupport_files = []
    files_and_dates_list=[]
    found=False # If we find a
    try:
        for file in glob.glob(autosupports_files_path):
            # a list with all the autosupport files present in the path
            autosupport_files.append(file)
    except Exception as e:
        print(e)
  
    if(len(autosupport_files)==0):
        return(render_template('error.html',error_code="The specified path does not contain autosupport files. Please go back and specify a path containing autosupport files."))
        #raise Exception("No autosupport files")
 
    # Now we need to open every file to obtain its generated date
    for index,f in enumerate(autosupport_files): 
        # The could be two types of autosupport files
        # normal files and compressed files .gz
        # We need to detect both of them and proceed

        found=False # For each file we set found = False
        if ".gz" in f:  # gzipped version of autosupport file
            opener = gzip.open
        else:

            opener = open

        try:
            file=opener(f, "rt")
        except Exception as e:
            print(e)
        files_and_dates = {}  # Dictionary with the files and dates
        for line in file:
            # Regular expression for catching the time in the autosupport log
            regexp = r'GENERATED_ON=.*' # We want to search for the GENERATED_ON, on the autosupport files.
            #regexp = r'[0-9][0-9]/[0-9][0-9] [0-9][0-9]:[0-9][0-9]:[0-9][0-9]'
            matchObj = re.match(regexp, line)  # Does it match what we search at the start of the line?
            if matchObj:
                # Add to the dictionary the name of the file and line
                files_and_dates["checkbox"] = os.path.basename(autosupport_files[index])
                files_and_dates["name_of_file"] = os.path.basename(autosupport_files[index])
                files_and_dates["start_date"] = matchObj.group()
                files_and_dates["start_date"]  = files_and_dates["start_date"].split("=")[1] # We just need the date, not the "GENERATED ON" string
                files_and_dates["path"] = autosupports_path
                files_and_dates_list.append(files_and_dates)
                files_and_dates={} #  new reference in memory
                found=True
                break
        

            # If after checking all the files, we have not found a line that matches the date format
            # then we do know the date
    if(not found):
        files_and_dates["checkbox"] = os.path.basename(autosupport_files[index])
        files_and_dates["name_of_file"] = os.path.basename(autosupport_files[index])
        files_and_dates["start_date"] = "UNKNOWN"
        files_and_dates["path"] = autosupports_path
        files_and_dates_list.append(files_and_dates)
        files_and_dates = {}  # new reference in memory

    return render_template('second_step.html',path = autosupports_path,autosupport_files = autosupport_files,files_and_dates = files_and_dates,files_and_dates_list=files_and_dates_list)

@app.route("/third_step",methods=['GET', 'POST'])
def third_step():

    hidden_filed_in_form=request.form["files_and_dates"] # We take the hidden filed
    json_acceptable_string = hidden_filed_in_form.replace("'", "\"") # We want to convert it
    list_of_dicts = json.loads(json_acceptable_string) # We convert it to a list of dics
    print("List of dicts:{}",format(list_of_dicts))
    list_of_selected_asups=[] # We want to have here just the selected
    path = list_of_dicts[0]['path'] # Can this produce an error?
    for a_dic in list_of_dicts: # For each item in the dictionary
        for key,value in a_dic.items():
            if key=="checkbox": # if the key is the checkbox, we check if is was checked in the form
                checked=request.form.get(value)
                if checked: # If string is not empty, then is because it was checked
                    path_plus_value=path+a_dic[key] # We just the path, plus the name of the file
                    list_of_selected_asups.append(path_plus_value) # we add them to the list

    replication_data=[]
    contexts_dic={}
    contexts_dic_list=[]
   
    # Now we need to search into the files selected
    for autosupport in list_of_selected_asups:

        g=replicationgraphs.LogParser(autosupport,'Replication Data Transferred over 24hr','Replication Detailed History')
        generated_on=g.get_generated_on()
        replication_data=g.search_and_return()
        list_of_contexts_in_asup=g.extract_contexts(replication_data)
        contexts_dic['ASUP_FILE']=autosupport
        contexts_dic['GENERATED_ON']=generated_on
        contexts_dic['DETAILS']=list_of_contexts_in_asup
        contexts_dic_list.append(contexts_dic)
        list_of_contexts_in_asup=[]
        contexts_dic={}
        
    print("El diccionario de contextos {}".format(contexts_dic_list))
    context_one=[]   
    for dic in contexts_dic_list: # context_dic_list is a list of dics each one containing the info from an asup file
        for key,value in dic.items(): #dic is a dictionary
            if 'GENERATED_ON' in key:
                generated_on=value
            if 'DETAILS' in key:
                for details in value: # details is a list with the details of each replication context
                    if int(details[0])==1: # the first item of the list details is the replication ctx number
                        details.insert(0,generated_on)
                        context_one.append(details)
                        
    print("Lo que le vamos a pasar al template engine {}".format(context_one))
    return(render_template("third_step.html",context=context_one))

if(__name__== "__main__"):
    app.run(debug=True)
