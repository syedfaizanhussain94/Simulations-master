## Overview  
This is a library of tools that lets you write high-level methods to build and animate objects in Blender. It's has not been made to run from the command line. Alternatively, it uses a Script Runner addon of Blender, which lets you execute scripts by pressing buttons within Blender itself. Which makes it easier to view the effects of your scripts and to experiment with parameters before performing them on the script.

The primary script run by Script Runner in my workflow is draw_scenes.py, whose main() function can be used to call test scripts or run a script from another file.

Much of the structure comes from [manim](https://github.com/3b1b/manim), 3blue1brown's animation engine.

## Using simulations
The root object class used for defining and manipulating objects in Blender is called Bobject (blender object). It initializes an object in Blender and defines simple functions for changing the parameters and adding keyframes.

The best scene to try when getting started is probably tex_test(), defined in draw_scenes.py. It creates a TexBobject and morphs through a few strings.

There isn't a best practice for creating a series of scenes in a new file. As you'll see, the files from past primer videos are all structured fairly differently. I haven't landed on a steady-state workflow here. So if you're confused, that might be why.

## Requirements  
Blender 2.79 (Not 2.8+, the api has changed)
- [Download](https://www.blender.org/)  
- [API](https://docs.blender.org/api/2.79/)  

Script Runner addon for Blender 
- [Download](http://goodspiritgraphics.com/software/products/script-runner-addon/)  

TeX  

dvisvgm  
- https://dvisvgm.de/  

OpenBabel if you want to do the molecule stuff http://openbabel.org/wiki/Main_Page  
- Chem stuff adapted from here: https://github.com/patrickfuller/blender-chemicals
- Also helpful: https://patrickfuller.github.io/molecules-from-smiles-molfiles-in-blender/

## Gotchas  
Blender comes packaged with its own version of python, so your local python installation and your favorite packages won't be there unless you install them to Blender's version.

Many of the slides from my presentations depend on specific blend files that are imported for use as common objects or components of them. For example, the blob creatures and components of the graphs. If at some point I try to turn this into a more broadly accessible tool, I'll have to include those files in the repo or procedurally generate them.
