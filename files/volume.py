import numpy as np
from stl import mesh
import sqlite3
import math
import os

# Using an existing closed stl file:
filename='1.stl'
filepath="stls/"



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
def write_db(print_params):
    connection=sqlite3.connect('data.db')
    cursor=connection.cursor()
    query1="create table if not exists print_estimator (filename text,volume float,model_height float, model_radius float,infill float, layer_height float,est_time float) "
    cursor.execute(query1)
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

stl_files=get_files(filepath)
for file in stl_files:
    print_params=get_params(file,infill,layer_height)
    db_response=write_db(print_params)
    print(db_response)
read_db()

gcode_files=
os.system('cmd /k "slic3r-console --no-gui -o --load config.ini 1.stl"')