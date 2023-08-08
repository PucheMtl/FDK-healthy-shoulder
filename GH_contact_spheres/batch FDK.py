#!/usr/bin/env python
# coding: utf-8

# In[3]:


from anypytools import AnyPyProcess
app = AnyPyProcess()
from anypytools import AnyMacro, AnyPyProcess, macro_commands as mc
from anypytools.macro_commands import Load, OperationRun, SaveData
import numpy as np
import matplotlib.pyplot as plt
#import seaborn as sns


# In[4]:


macrolist = [
    [ mc.Load("GH_2spheres.main.any"),
      mc.SetValue("Main.Model.ShoulderPE.F", 0.0 + i*0.5),
      mc.OperationRun ("Main.RunApplication"),
    """  mc.Dump("Main.Study.Output.Abscissa.t"),
      mc.Dump("Main.Study.Output.Model.ShoulderPE.pline.Pos"),
      mc.Dump("Main.HumanModel.BodyModel.Right.ShoulderArm.Mus.deltoideus_lateral_part_3.Activity"),
      mc.SaveData('Main.Study', 'output.anydata.h5'),"""
     ]
    for i in range(2)
]
results = app.start_macro(macrolist)




# In[ ]:




