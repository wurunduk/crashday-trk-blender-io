# Creashday trk blender plugin
Blender plugin to create and export crashday .trk maps.  
Auto slices the map and generates all needed .trk, .p3d, .cfl files for you.

## Usage
### Installation
To install, download latest version from github releases  
In Blender go to Edit->Preferences  
Select Add-ons  
Click "Install..." button at the top and select downloaded zip file  
**You need to install blender p3d plugin for model autoexport to work**
[download p3d plugin](https://github.com/wurunduk/blender-p3d-import-export/releases)
### Exporting
**Apply rotation and scaling before export!**  
You can enable export-log which is created in the same folder as the exported file and contains export log as well as meshes list, used in .cca files. This info is also logged in Blender's console.
You can find the export option in File->Export->Crashday Track (.trk)
After selecting a .trk to export, in the same directory a content folder will be made with .p3d and .trk files.  
You can find .trk settings in Blender's scene properties under "CDRE - Track"
After export you will se the map divided into tiles and you can look for any mistakes and export problems. ctrl+z will revert the tiling and you can update the map after that.
## Moddeling guidelines
General CD moddeling guidelines apply.  
You should have a main mesh on every tile after cutting. If no main mesh was present, a suitable one will be selected. If no meshes are present, a void tile will be used.

## FAQ
**Question:** After export some meshes move and change their position?

**Answer:** Apply rotations and scaling to the objects.

## TODO:
- check if properly works with collections e.g. sort parts of a mesh in some collection into that collection
- fully copy original mesh on division
- add option to leave the meshes as they were or to split after export
- rexeporting the map should work faster and deal the same result
- add error checking in crashday .py files
- check length's on export in trk, p3d.py
- need to optimise and clean splitting, need to remove collections.
- Possibly shouldn't actually edit the scene
- add placeholder icons for editor
- add checkpoint stuff
- add limits to the trk options in blender
- APPLY ROTATION N SCALE
- deal with selection only stuff
- connect loose parts inside one tile
 * will fix no collisions on some meshes