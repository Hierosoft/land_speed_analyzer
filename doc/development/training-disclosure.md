# Training Disclosure for land_speed_analyzer
This Training Disclosure, which may be more specifically titled above here (and in this document possibly referred to as "this disclosure"), is based on **Training Disclosure version 1.1.4** at https://github.com/Hierosoft/training-disclosure by Jake Gustafson. Jake Gustafson is probably *not* an author of the project unless listed as a project author, nor necessarily the disclosure editor(s) of this copy of the disclosure unless this copy is the original which among other places I, Jake Gustafson, state IANAL. The original disclosure is released under the [CC0](https://creativecommons.org/public-domain/cc0/) license, but regarding any text that differs from the original:

This disclosure also functions as a claim of copyright to the scope described in the paragraph below since potentially in some jurisdictions output not of direct human origin, by certain means of generation at least, may not be copyrightable (again, IANAL):

Various author(s) may make claims of authorship to content in the project not mentioned in this disclosure, which this disclosure by way of omission unless stated elsewhere implies is of direct human origin unless stated elsewhere. Such statements elsewhere are present and complete if applicable to the best of the disclosure editor(s) ability. Additionally, the project author(s) hereby claim copyright and claim direct human origin to any and all content in the subsections of this disclosure itself, where scope is defined to the best of the ability of the disclosure editor(s), including the subsection names themselves, unless where stated, and unless implied such as by context, being copyrighted or trademarked elsewhere, or other means of statement or implication according to law in applicable jurisdiction(s).

Disclosure editor(s): Hierosoft LLC

Project author: Hierosoft LLC

This disclosure is a voluntary of how and where content in or used by this project was produced by LLM(s) or any tools that are "trained" in any way.

The main section of this disclosure lists such tools. For each, the version, install location, and a scope of their training sources in a way that is specific as possible.

Subsections of this disclosure contain prompts used to generate content, in a way that is complete to the best ability of the disclosure editor(s).

tool(s) used:
- GPT-4-Turbo (Version 4o, chatgpt.com)

Scope of use: code described in subsections--typically modified by hand to improve logic, variable naming, integration, etc, but in this commit, unmodified.

## __init__.py
- 2025-01-10

Create a Blender script that sets a land speed for each element of a new dictionary where the key is the armature name. It will work by getting the foot speed when it is neither lifted above a threshold nor moving forward (assume lifted off ground due to that). Iterate through every object in the scene. If the object is an armature call a get_foot function. There should be a constant called Z_THRESHOLD . The function should iterate the bones and look for "foot.l" (case insensitive using lower()) and return the bone in such a way that the posed position of the tail can be determined, whether that be the bone name or object whatever will be most easily usable later for that purpose, which will be important in the next call. If it does not return None, use the return to call analyze_walk. The function should accept an armature and the bone as described. First set prev_y = None, deltas = []. Then it should loop through each frame of the "Walk" action of the armature if present, otherwise the main timeline. For each frame, get the absolute tail position in world coordinates, accounting for armature scaling, location, rotation etc and set this_y to the result's y. if prev_y is not None, set delta = abs(this_y - prev_y) and append delta to deltas, unless delta is negative in which case do nothing with the delta (comment that the unused case assumes character faces -y).  Whenever the tail of the bone's z is greater than the threshold, also ignore delta. After the loop, average deltas and place the result in the dictionary as described earlier. In the outer code when all calls are done, show a dialog box displaying a string constructed from the dictionary by iterating each key and value, and adding '{key} land speed: {value}\n'

Instead of just saving value, save a dictionary to each key. The sub-dictionary should collect the average delta, the count of foot bones found, the "count of bones above threshold". Also display the "threshold" itself. Also collect and display "foot bone name". Also display "Facing direction: negative". Display the information on separate lines in the dialog neatly.

The dialog box is only showing "message" followed by "Armature: CharacterArmature
  Average Delta: 0.0000
  Foot Bone Count: 1
  Bones Above Threshold: 0
  Threshold: 0.1
  Foot Bone Names: Foot.L
  Facing Direction: negative
" all in one box so I can't see it all at once. put each element in a separate entry field and line, but in one dialog box or popup window.

Traceback (most recent call last):
  File "<blender_console>", line 1, in <module>
  File "<blender_console>", line 8, in main
  File "/home/owner/Downloads/blendernightly/versions/blender-3.6.19-linux-x64/3.6/scripts/modules/bpy/ops.py", line 111, in __call__
    ret = _op_call(self.idname_py(), C_dict, kw, C_exec, C_undo)
TypeError: Converting py args to operator properties: : keyword "analysis_results" unrecognized

It should be called frames not bones above threshold, my mistake. Also collect and display total frames analyzed for the armature.

Also collect and display the minimum and maximum z of the tail.

Also collect the min y and max y.

Separately check if delta >= 0 and if below threshold, and collect and display a count of "frames with y delta" as well.

We aren't getting the action frames. We are probably going to have to iterate through stacked actions under each armature, and instead of using the armature name as the key, use the armature name + "." + the stacked action name.

It says "AnimData has no attribute named actions. Did you mean action?". Make sure you get all of the stashed actions correctly.

line 91 in <listcomp> KeyError: 'action'

We seem to be getting the right actions now, and some frames have y delta, but there are no frames below the threshold detected. We want to use frames where the tail z is below the threshold, not above it.

It should be y delta > 0, not >= 0. Also, we still are getting no delta after that is fixed, even though when I export a glb all of the actions are there and work. Maybe you have to unstash the action on the track or read the tracks a different way. The output indicates there is no movement, but there demonstrably is.

NlaObject has no attribute is_stale

We still aren't getting any delta. maybe you have to access the strip on each nla track and iterate and unstash those.

NlaStrip has no attribute is_muted

There is still no delta. I had another conversation with you, and you seem to have discovered that to unstash an action you have to make it active, like bpy.context.object.animation_data.action = strip.action

Ok, now make it into an add-on. Add a section to the View panel of the 3D view, where the user can set Z MAX (rename z threshold to z_max and change the check against it from > to >=) and Facing (drop-down, default to "-Y", other option is "+Y", multiply delta by lookup table directions = {"-Y": 1, "+Y": -1} using facing as key before using any delta)

- 2025-01-10

It works!

If this is __init__.py, what should I name the plugin folder, to meet blender plugin folder naming conventions?

Make a docstring for the module, including a GPL 3.0 header for the co-authors Jake Gustafson and ChatGPT, 2025 January 10.

- NOTE: The GPL license header added to the file is authored by humans at or for the Free Software Foundation and co-authored by ChatGPT in words or word order not identical to the FSF version.
