import numpy as np
from stl import mesh
import sqlite3
import math
import os
import warnings
warnings.filterwarnings('error')
from subprocess import STDOUT, check_output
import subprocess

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


def create_gcode():
    stl_files=get_files(stl_filepath)
    gcode_files=get_files(gcode_filepath)
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
        stl_file=file.replace('_fixed','')
        stl_file=obj_file.replace('stl','aaaaaaa')
        stl_file=obj_file.replace('obj','stl')
        if stl_file in stl_files:
            print(str(stl_files.index(file))+" / "+str(len(stl_files)))
            print(file)
            shutil.move(file, "bad_stls/"+file)
            stl_file=obj_file.replace('aaaaaaa','stl')
            shutil.move(stl_file, "bad_stls/"+stl_file)
            print("bad_stl moved")

def est_printtime():
    gcode_files=get_files(gcode_filepath)
    for file in gcode_files:
        print(file)
        os.system('python gcoder.py {}'.format(file)) 
        
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

# clear_db()
repair_stl()
delete_fixed_stl()
# execute_stl()
create_gcode()
est_printtime()
read_db()
os.system('cmd /k')
