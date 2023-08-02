# -*- coding: utf-8 -*-
"""
Created on Tue Aug  1 15:04:03 2023

@author: Dan
"""

#%% Libraries needed
import numpy as np
import anypytools.h5py_wrapper as h5py2
from anypytools.datautils import read_anyoutputfile

import numpy as np
import math

import matplotlib.pyplot as plt

import os

#%% Load h5 function
"""
-------------------------------------------------------------------------------
LOAD H5 DATA FUNCTIONS
-------------------------------------------------------------------------------
"""

"""

Uses the Anypytool function to load a model variable from an .anydata.h5 file by using the anybody variable path in the study with . instead of /
h5path is the path of the file to load
Failed : removes the 0 in the results in case the simulation failed after a certain time
Failed : is the first step number that failed


Ex: to load the variable  : Seg.Scapula.ghProth.Axes
    VariablePath = "Output.Seg.Scapula.ghProth.Axes"
"""
def LoadAnyVariable(h5Path, VariablePath):
    h5Path += '.anydata.h5'
    with h5py2.File(h5Path, "r") as f:
        Output = np.array(f[VariablePath]) 
     
    return Output





#%% Load h5 data
"""
Reads variables from an anydata.h5 file

if Resultats.anydata.h5 is in the Output directory
h5Path = "Output/Resultats"

Sums the total variable for a muscle in multiple parts
AddConstants : adds the constants that are not stored in the h5 file by reading them in the FileOut file  
"""

def LoadResultsh5(h5Path,AddConstants = True):

     # Load les Variables
    
    Temps = LoadAnyVariable(h5Path,'Output.Abscissa.t')
     
     # Angle d'abduction en °
    Angle =  LoadAnyVariable(h5Path,'Output.Model.BodyModel.Right.ShoulderArm.InterfaceFolder.GlenohumeralAbduction.Pos') / np.pi*180
     
    PlinePos = LoadAnyVariable(h5Path, "Output.Model.ShoulderPE.pline.Pos")
     
    SpherePos = LoadAnyVariable(h5Path, "Output.Model.GH_2spheres.gh_2spheres.Pos")
    
    
    Results = {"Temps":Temps,
            "Angle":Angle,
            "PlinePos":PlinePos,
            "SpherePos":SpherePos
            }
    
        
    # Load les constantes
    Constants = LoadAnyFileOut(h5Path,LoadConstantsOnly=True)
     
    Results["Model informations"] = Constants
     
    return Results

#%% Load AnyFileOut File
"""
Loads a specific variable from an AnyFileOut file
Or can load only the constants
"""
def LoadAnyFileOutVariable(FileOutPath,FileType,VariablePath=str,LoadConstantsOnly = False):
    data, dataheader, constantsdata = read_anyoutputfile(FileOutPath + "." + FileType)
    

    if LoadConstantsOnly == False:
        
        
        
        # Constructs a dictionary with all the variables and constants
        DataDictionary = {}
        for index,Variable in enumerate(dataheader):
            
            # Deletes the anybody path of the variable name to only keep the variable name 
            Variable = Variable.replace("Main.Study.FileOut.","")
            
            DataDictionary[Variable] = data[:,index]
        
        # adds the variable to DataDictionary 
        for index,Variable in enumerate(list(constantsdata.keys())):
    
            DataDictionary[Variable] = constantsdata[Variable]
        
        # Loads every variable and constants
        if VariablePath == "all":
            Output = DataDictionary
        else:
            # Loads a specific variable 
            Output = DataDictionary[VariablePath]
    
    # Loads only the constants 
    if LoadConstantsOnly == True:
        Output = constantsdata
    
    return Output

#%% Load AnyFileOut
"""
Load an AnyFileOut and creates a dictionnary
FileType : says if the FileOut is a .txt,.csv...
LoadConstantsOnly : True if output must only be the constants to complete these missing informations while loading a .h5 file
Ex : FileOut.txt :
     FileOutPath = File Path and Name
     FileType = txt
"""
def LoadAnyFileOut(FileOutPath,FileType="txt",LoadConstantsOnly = False):
    
    # Constantes à charger
    DimensionSpheres = ["rg","rh"]
    
    Force = ["SpringForce"]

    Simulation_Parameters = ["nstep"]    

    InsertionsRessort = ["Ins","Ori"]    
    

            
    # Loads the constants
    constantsdata = LoadAnyFileOutVariable(FileOutPath,FileType,"all")
    
    
    # All the constants names in the .txt file 
    constantsNames = list(dict.keys(constantsdata))
    
    # Initialisation des dictionnaires
    FileOut = {}
    FileOut["Dimensions Sphères"] = {}
    FileOut["Force Ressort"] = {}
    FileOut["Paramètres de simulation"] = {}
    FileOut["Insertion Ressorts"] = {}
    
    # Goes through all constants names
    # Adds constants to the ouptut data and puts it in seperated dictionary keys depending on their names
    for Variable in constantsNames:
        VariableName = Variable.replace("Main.Study.FileOut.","")
        
        if any(i==VariableName for i in DimensionSpheres):
            FileOut["Dimensions Sphères"][VariableName] = constantsdata[Variable]
            
        if any(i==VariableName for i in Force):
            FileOut["Force Ressort"] = constantsdata[Variable][0]
    
        if any(i==VariableName for i in Simulation_Parameters):
            FileOut["Paramètres de simulation"][VariableName] = constantsdata[Variable]
        
 
    FileOut["Insertion Ressorts"]["Origin"] = np.array([constantsdata["Ori[0]"][0],constantsdata["Ori[1]"][0],constantsdata["Ori[2]"][0]]) 
    FileOut["Insertion Ressorts"]["Insertion"] = np.array([constantsdata["Ins[0]"][0],constantsdata["Ins[1]"][0],constantsdata["Ins[2]"][0]]) 
    
    return FileOut

#%% Graphiques Function setup




"""
Setup a subplot of dimension :
    Subplot["Dimension"] = [nrows,ncols]
And defines the active axis as the Subplot["Number"]=number of the plot

example : Dimension = [2,2]
          the grah numbers are 1 2
                               3 4
                               
          Number = 3 corresponds to subplot [1,0]
"""
def SubplotSetup(Subplot):
    global ax
    global fig
    
    
    if Subplot is None:
        plt.figure()
        fig,ax = plt.subplots()
    else:
        # If it's the first subplot then it initializes the graph
        if Subplot["Number"] == 1:

            plt.figure()
            fig,ax = plt.subplots(Subplot["Dimension"][0],Subplot["Dimension"][1],figsize=(13, 8))
        
        # Selects the subplot to draw
        # If subplot on only one dimension
        if len(ax.shape) ==1:
            plt.figure(fig)
            
            plt.axes(ax[Subplot["Number"]-1])
        
        # Selects the subplot to draw    
        # If the subplot is 2 dimension
        else:
            plt.figure(fig)
            # quantity of subplots in the figure
            MaxPlotNumber = Subplot["Dimension"][0] * Subplot["Dimension"][1]
            
            # Creates a 2d matrix that contains the graph number and transforms the number into the axis coordinate in 2d
            # Creates a vector with all the plot numbers
            MatPlotNumber = np.linspace(1, MaxPlotNumber, 4, dtype=int)
            # Reshapes the vector to have a 2d matrix that has the same dimension than the subplot
            MatPlotNumber = np.reshape(MatPlotNumber, (-1, Subplot["Dimension"][1]))
            
            # Finds the coordinate of the wanted subplot to draw
            SubplotCoordinate = np.where(MatPlotNumber==Subplot["Number"])
            
            # Sets the current active subplot
            plt.axes(ax[SubplotCoordinate[0][0],SubplotCoordinate[1]][0])

"""
Fonction qui trace les graphs
"""
def PlotGraph(x,y,label=None,color = None):
    plt.plot(x,y,label = label,color=color)





#%% Fonction Graphique 

"""
Fonction générale qui gère les graphiques


data : le dictionnaire contenant les data à tracer
     : Soit un jeu de plusieurs datas (Compare = True)
     : Soit un dictionnaire ne contenant qu'une seule simulation
    
Variable_x : Le nom de la variable placée en x sur le graphique
Variable_u : le nom de la variable placée en y sur le graphique

Composantes : Les composantes à tracer 
            : Type = ["composante 1","composante 2","comopsante 3"]
            : Si la variable en y n'a qu'une seule composante, ne pas déclarer ce paramètre
            
            CAS PARTICULIER COMPOSANTES: Si on compare, on ne peut activer qu'une composante
            
            : Si on veut activer x et y entrer : Composantes = ["x","y"]
            : Si on veut activer y entrer : Composantes = ["y"]
            
            
Compare : = True si on veut comparer plusieurs données
          Ne rien mettre (Compare = False par défaut) : on veut tracer qu'une seule donnée 
          
          


"""
def Graph(data,Variable_x,Variable_y,FigureTitle,Composantes = False,Compare = False,Subplot = None,SubplotTitle = False):

    SubplotSetup(Subplot) 
    
    # Si le vecteur en y n'a qu'une composante
    if Composantes == False:
        
        
        if Compare == False:
            PlotGraph(data[Variable_x],data[Variable_y])
        
        elif Compare == True:
            ListSimulations = list(data.keys())
            
            for Simulation in ListSimulations:
                PlotGraph(data[Simulation][Variable_x],data[Simulation][Variable_y],label = Simulation)
                plt.legend()
    

    # Si les composantes sont activées 
    else:
        NumComposantes = [0]*len(Composantes)
        # Convertit le nom de la composante en numéro de colonne (0 pour x, 1 pour y, 2 opur z)
        for i in range(len(Composantes)):
            if Composantes[i] == "x":
                NumComposantes[i]=0
        
            if Composantes[i] == "y":
                NumComposantes[i]=1
        
            if Composantes[i] == "z":
                NumComposantes[i]=2
    
    
    
        if Compare == False:
            
            for Num in NumComposantes: 
                PlotGraph(data[Variable_x],data[Variable_y][:,Num],label = Composantes[Num])
            plt.legend()
        
        elif Compare == True:
            ListSimulations = list(data.keys())
            
            for Simulation in ListSimulations:
                PlotGraph(data[Simulation][Variable_x],data[Simulation][Variable_y][:,NumComposantes[0]],label = Simulation)
            plt.legend()
               
    
    plt.grid()
    plt.xlabel(Variable_x)
    plt.ylabel(Variable_y)  
    

    if Subplot is None:
        plt.title(FigureTitle)
    
    
    # Dans le cas d'un subplot
    else:

            
        # If a subplot title is entered, draws it (SubplotTitle isn't a bool)
        if not type(SubplotTitle) is bool:
            plt.title(SubplotTitle)
   

            
        # Ne trace la légende que si le dernier graphique du subplot est vide
        # Trace le titre du graphique que lorsqu'on trace le dernier graphique du subplot
        if (len(ax.shape) == 1 and ax[-1].lines) or (not len(ax.shape) == 1 and ax[-1,-1].lines):   

            

            # Trace le titre de la figure
            plt.suptitle(FigureTitle)
            
            # Ajuste les distances entre les subplots quand ils sont tous tracés
            plt.tight_layout()
            
    
    

    
    


#%% Codes d'exemple (load et graph)


# Nom du fichier
Results = LoadResultsh5('GH_2spheres.main_F=10')

Studies = {}
Studies["Study 1"] = LoadResultsh5('GH_2spheres.main_F=10')
Studies["Study 2"] = LoadResultsh5('GH_2spheres.main_F=10')


# # importe le nom de tous les fichiers dans le dossier
# FileNames = os.listdir()

# # Ne sélectionne que les fichiers h5
# FileNames = [File for File in FileNames if ".h5" in File]

# Force = 

Graph(Results,"Temps","PlinePos","Results")
Graph(Studies,"Temps","PlinePos","Study",Compare=True)

Graph(Results,"Temps","PlinePos","PlinePos",Subplot = {"Dimension":[1,2],"Number":1},SubplotTitle = "Studies")
Graph(Studies,"Temps","PlinePos","PlinePos",Compare=True,Subplot = {"Dimension":[1,2],"Number":2},SubplotTitle = "Studies")

Graph(Results,"Temps","SpherePos","SpherePos",Subplot = {"Dimension":[1,2],"Number":1},SubplotTitle = "Résultats",Composantes = ["x","y"])
Graph(Studies,"Temps","SpherePos","SpherePos",Compare=True,Subplot = {"Dimension":[1,2],"Number":2},SubplotTitle = "Studies",Composantes =["y"])




