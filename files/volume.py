import numpy as np
from stl import mesh
import sqlite3
import math
import os
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 
warnings.filterwarnings("ignore")
from subprocess import STDOUT, check_output
import subprocess
import threading

# Using an existing closed stl file:
filename='1.stl'
stl_filepath="stls/"
gcode_filepath="gcodes/"
import shutil


infill=20
layer_height=.2
def get_params(filename,infill,layer_height):
    try:
        your_mesh = mesh.Mesh.from_file(filename)
        volume, cog, inertia = your_mesh.get_mass_properties()
        # print("Volume                                  = {0}".format(volume))
        
        x_dim=your_mesh.x.max()-your_mesh.x.min()
        y_dim=your_mesh.y.max()-your_mesh.y.min()
        z_dim=your_mesh.z.max()-your_mesh.z.min()
        dimensions=(x_dim,y_dim,z_dim)
        h=float(z_dim)
        r=float(math.sqrt(volume/(math.pi*h)))
        learning_parameters=(filename,volume,h,r,infill,layer_height,None)

        return learning_parameters
    except:
        shutil.move(filename, "bad_stls/"+filename)
        print("bad_stl moved")
        return(None,None,None,None,None,None,None)

def write_param_db(print_params):
    connection=sqlite3.connect('data.db')
    cursor=connection.cursor()
    query1="create table if not exists print_estimator (filename text,volume float,model_height float, model_radius float,infill float, layer_height float,est_time float) "
    cursor.execute(query1)
    connection.commit()
    query2="insert into print_estimator values(?,?,?,?,?,?,?)"
    cursor.execute(query2,print_params)
    connection.commit()
    connection.close()
    return "written to db"

def read_db():
    connection=sqlite3.connect('data.db')
    cursor=connection.cursor()
    for row in cursor.execute("select * from print_estimator"):
        print(row)
    connection.commit()
    connection.close()

def get_files(filepath):
    file=[]
    for root, dirs, files in os.walk(filepath, topdown=False):
        for name in files:
            file.append(os.path.join(root, name))
    return file

def execute_stl():
    stl_files=get_files(stl_filepath)
    for file in stl_files:
        print(str(stl_files.index(file))+" / "+str(len(stl_files)))
        print_params=get_params(file,infill,layer_height)
        if print_params[1]!=None:
            db_response=write_param_db(print_params)
            print(db_response)
            os.system('cls')
    read_db()

def write_estimate_db(print_params):
    connection=sqlite3.connect('data.db')
    cursor=connection.cursor()
    query2="insert into print_estimator values(?) where filename=?"
    cursor.execute(query2,print_params)
    connection.commit()
    connection.close()
    return "written to db"




def create_gcode(split_index):
    split_index=int(split_index)
    stl_files=get_files(stl_filepath)
    stl_files=stl_files[split_index:]
    gcode_files=get_files(gcode_filepath)
    stl_files.reverse()
    for file in stl_files:
        if file.replace('stl','gcode') not in gcode_files:
            print(str(stl_files.index(file))+" / "+str(len(stl_files)))
            print(file)
            try:
                CMDCommand = '..\slic3r-console --no-gui -o gcodes/ --load  ../config.ini {}'.format(file)
                timeoutSeconds = 15
                subprocess.check_output(CMDCommand, shell=True, timeout=timeoutSeconds)
                # os.system('..\slic3r-console --no-gui -o gcodes/ --load  ../config.ini {}'.format(file)) 
            except:
                print("skipped")
        else:
            print("Already done")

def repair_stl():
    stl_files=get_files(stl_filepath)
    gcode_files=get_files(gcode_filepath)
    for file in stl_files:
        if file.replace('stl','gcode') not in gcode_files:
            print(str(stl_files.index(file))+" / "+str(len(stl_files)))
            print(file)
            try:
                CMDCommand = '..\slic3r-console --no-gui --repair {}'.format(file)
                timeoutSeconds = 10
                subprocess.check_output(CMDCommand, shell=True, timeout=timeoutSeconds)
                # os.system('..\slic3r-console --no-gui --repair {}'.format(file)) 
                
            except:
                print("skipped")

                
def delete_fixed_stl():
    stl_files=get_files(stl_filepath)
    for file in stl_files:
        if 'obj' in file:
            stl_file=file.replace('_fixed','')
            stl_file=stl_file.replace('obj','stl')
            print(stl_file)
            if stl_file in stl_files:
                print(str(stl_files.index(file))+" / "+str(len(stl_files)))
                print(file)
                shutil.move(file, "bad_stls/"+file)
                shutil.move(stl_file, "bad_stls/"+stl_file)
                print("bad_stl moved")
            else:
                pass

def est_printtime():
    gcode_files=get_files(gcode_filepath)
    for file in gcode_files:
        print(str(gcode_files.index(file))+" / "+str(len(gcode_files)))
        print(file)
        try:
            CMDCommand = 'python gcoder.py {}'.format(file)
            timeoutSeconds = 10
            subprocess.check_output(CMDCommand, shell=True, timeout=timeoutSeconds)
        except:
            print('Gcode creation failed')

        # os.system('python gcoder.py {}'.format(file)) 
        # db_response=write_estimate_db(print_params)     
        # print(db_response)
def clear_db():
    try:
        query="drop table print_estimator"
        connection=sqlite3.connect("data.db")
        cursor=connection.cursor()
        cursor.execute(query)
        print("***************db creared***************")
        connection.commit()
        connection.close()
    except:
        pass
def multithread_gcode_creation():
    stl_files=get_files(stl_filepath)
    stl_length=len(stl_files)
    div=stl_length/5
    x1 = threading.Thread(target=create_gcode, args=(stl_length/8,))
    x2=threading.Thread(target=create_gcode, args=(2*stl_length/8,))
    x3=threading.Thread(target=create_gcode, args=(3*stl_length/8,))
    x4=threading.Thread(target=create_gcode, args=(4*stl_length/8,))
    x5=threading.Thread(target=create_gcode, args=(5*stl_length/8,))
    x6=threading.Thread(target=create_gcode, args=(6*stl_length/8,))
    x7=threading.Thread(target=create_gcode, args=(7*stl_length/8,))
    x8=threading.Thread(target=create_gcode, args=(8*stl_length/8,))
    x1.start()
    x2.start()
    x3.start()
    x4.start()
    x5.start()
    x6.start()
    x7.start()
    x8.start()
clear_db()
# repair_stl()
# delete_fixed_stl()
execute_stl()

# execute_stl()
multithread_gcode_creation()

# create_gcode(0)
est_printtime()
read_db()
os.system('cmd /k')
