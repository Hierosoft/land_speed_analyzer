# Land Speed Analyzer
Add-on for Blender

Prevent foot sliding ("moonwalking") in your game by analyzing the foot speed (while touching ground) in Blender &amp; using the value in your game! Be sure to also scale the rate by the scale of the character if scaled in your 3D/game engine.

NOTE: If your feet do not move at a constant rate, you will still have the problem at different parts of your animation that do not match the average. To fix the sliding issue entirely in that case you will have to make foot motion linear while on the ground.

If you have changed defaults, you must enable "Rest Position" in the Armature object's "Data" tab and similar pose features such as the Armature modifier to ensure this add-on can read your poses.

This add-on has only been tested on "actions" in the NLA. In other cases if the land speed is not found please report an issue at <https://github.com/Hierosoft/land_speed_analyzer/issues> and provide an example file.
