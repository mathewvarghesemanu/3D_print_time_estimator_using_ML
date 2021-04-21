# print_estimator
The idea is to create an API for estimating the time for 3D printing without actually slicing the G code.

Gcode slicing needs compute power and complicated softwares with complicated printing profiles. This is hard to implement on a Web server.

The approach- 
1.using Numpy-stl, estimate the volume and dimensions of the 3D model.
2.Compute the parameters for a cylinder with the same height and volume of the 3D model that we are considering.
3.save the parameters like volume of the model, height of the model, radius of the cylinder, infill, layer height, in an SQlite db.
4.use slic3r slicer invoked from command line to slice the STL files and save in a G code folder.
5.Using gcoder.py, compute the estimated print time using the parameters of a supplied model.
6.Save the estimated print time in the database corresponding to its respective file name.
7.Use supervised learning ( regression) to train a model with the input parameters that was computed earlier, and output parameter as the estimated print time.
8.Use this model to predict Print-time in the API.
