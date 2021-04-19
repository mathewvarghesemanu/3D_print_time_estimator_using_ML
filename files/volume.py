import numpy as np
from stl import mesh
import sqlite3
import math
import os
# Using an existing closed stl file:
filename='1.stl'
stl_filepath="stls/"
gcode_filepath="gcodes/"



infill=20
layer_height=.2
def get_params(filename,infill,layer_height):
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

def write_param_db(print_params):
    connection=sqlite3.connect('data.db')
    cursor=connection.cursor()
    query1="create table if not exists print_estimator (filename text,volume float,model_height float, model_radius float,infill float, layer_height float,est_time text) "
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
        print_params=get_params(file,infill,layer_height)
        db_response=write_param_db(print_params)
        print(db_response)
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
    for file in stl_files:
        print(file)
        os.system('..\slic3r-console --no-gui -o gcodes/ --load ../config.ini {}'.format(file)) 

def est_printtime():
    gcode_files=get_files(gcode_filepath)
    for file in gcode_files:
        print(file)
        os.system('gcoder.py {}'.format(file)) 
        
        # db_response=write_estimate_db(print_params)     
        # print(db_response)
# execute_stl()
# create_gcode()
est_printtime()
read_db()
os.system('cmd /k')
# current_dir=os.getcwd()
# parent_dir=os.path.dirname(os.path.dirname(current_dir))

