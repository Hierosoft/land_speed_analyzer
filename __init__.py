import bpy
from mathutils import Vector

# Constants
DEFAULT_Z_MAX = 0.1  # Default threshold for foot lift detection
DEFAULT_FACING = "-Y"  # Default facing direction

# Facing direction lookup table
FACING_DIRECTIONS = {
    "-Y": 1,
    "+Y": -1
}

class LandSpeedAnalysisSettings(bpy.types.PropertyGroup):
    """Define the properties for user customization of the analysis."""
    z_max: bpy.props.FloatProperty(
        name="Z Max",
        description="The maximum Z value before foot lift is considered",
        default=DEFAULT_Z_MAX,
        min=0.0,
    )

    facing: bpy.props.EnumProperty(
        name="Facing",
        description="Direction in which the foot should move",
        items=[
            ("-Y", "-Y", "Facing negative Y direction"),
            ("+Y", "+Y", "Facing positive Y direction"),
        ],
        default=DEFAULT_FACING,
    )


class LandSpeedAnalysisPanel(bpy.types.Panel):
    """Add a panel to the 3D View for configuring Land Speed Analysis settings."""
    bl_label = "Land Speed Analysis Settings"
    bl_idname = "VIEW3D_PT_land_speed_analysis"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Land Speed'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        settings = scene.land_speed_analysis_settings

        layout.prop(settings, "z_max")
        layout.prop(settings, "facing")
        layout.operator("object.analyze_land_speed", text="Analyze Land Speed")


class LandSpeedAnalysisOperator(bpy.types.Operator):
    """Operator to analyze land speed."""
    bl_idname = "object.analyze_land_speed"
    bl_label = "Analyze Land Speed"

    def execute(self, context):
        settings = context.scene.land_speed_analysis_settings
        z_max = settings.z_max
        facing = settings.facing
        facing_direction = FACING_DIRECTIONS.get(facing, 1)  # Get facing direction multiplier

        results = {}
        for obj in bpy.data.objects:
            if obj.type == 'ARMATURE' and obj.animation_data:
                foot_bones = get_foot_bones(obj)
                if foot_bones:
                    # Iterate through NLA tracks to get all actions
                    for track in obj.animation_data.nla_tracks:
                        for strip in track.strips:
                            # Check if the strip has an action and ensure it's active
                            action = strip.action
                            if action:
                                # Unstash the action by setting it as the active action
                                bpy.context.view_layer.objects.active = obj
                                bpy.context.object.animation_data.action = strip.action  # Set the strip action as active

                                action_name = f"{obj.name}.{strip.name}"
                                results[action_name] = analyze_walk(
                                    obj, foot_bones, action, strip.name, z_max, facing_direction
                                )

                    # Check if there's a single action not in NLA (just the active one)
                    if obj.animation_data.action:
                        action_key = f"{obj.name}.{obj.animation_data.action.name}"
                        results[action_key] = analyze_walk(
                            obj, foot_bones, obj.animation_data.action, obj.animation_data.action.name, z_max, facing_direction
                        )

        # Prepare display results
        formatted_results = [
            f"Armature: {armature}\n"
            f"  Action: {data['action_name']}\n"
            f"  Average Delta: {data['average_delta']:.4f}\n"
            f"  Foot Bone Count: {data['foot_bone_count']}\n"
            f"  Frames Below Threshold: {data['frames_below_threshold']}\n"
            f"  Frames with Y Delta: {data['frames_with_y_delta']}\n"
            f"  Total Frames Analyzed: {data['total_frames_analyzed']}\n"
            f"  Min Y: {data['min_y']:.4f}\n"
            f"  Max Y: {data['max_y']:.4f}\n"
            f"  Min Z: {data['min_z']:.4f}\n"
            f"  Max Z: {data['max_z']:.4f}\n"
            f"  Threshold: {data['z_max']}\n"
            f"  Foot Bone Names: {', '.join(data['foot_bone_names'])}\n"
            f"  Facing Direction: {data['facing_direction']}"
            for armature, data in results.items()
        ]
        bpy.context.scene['analysis_results'] = formatted_results
        bpy.ops.object.dialog_operator('INVOKE_DEFAULT')

        return {'FINISHED'}


class DialogOperator(bpy.types.Operator):
    """Display analysis results in a structured dialog."""
    bl_idname = "object.dialog_operator"
    bl_label = "Land Speed Analysis Results"

    def draw(self, context):
        layout = self.layout
        results = bpy.context.scene.get('analysis_results', [])
        for result in results:
            box = layout.box()
            for line in result.split("\n"):
                box.label(text=line)

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


def get_foot_bones(armature):
    """Get foot bones matching 'foot.l' in the armature."""
    return [bone for bone in armature.pose.bones if "foot.l" in bone.name.lower()]


def analyze_walk(armature, bones, action, action_name, z_max, facing_direction):
    """Analyze walk action or timeline and calculate metrics."""
    deltas = []
    frames_above_threshold = 0
    frames_with_y_delta = 0
    frames_below_threshold = 0  # Count frames where Z is below threshold
    total_frames = 0
    min_y = float('inf')
    max_y = float('-inf')
    min_z = float('inf')
    max_z = float('-inf')

    bpy.context.view_layer.objects.active = armature
    frame_range = range(
        int(action.frame_range[0]), int(action.frame_range[1]) + 1
    ) if action else range(bpy.context.scene.frame_start, bpy.context.scene.frame_end + 1)

    for bone in bones:
        prev_y = None
        for frame in frame_range:
            bpy.context.scene.frame_set(frame)
            tail_pos = armature.matrix_world @ bone.tail
            this_y, this_z = tail_pos.y, tail_pos.z
            total_frames += 1

            # Track min and max Y, Z values
            min_y = min(min_y, this_y)
            max_y = max(max_y, this_y)
            min_z = min(min_z, this_z)
            max_z = max(max_z, this_z)

            if this_z <= z_max:  # Detect frames with Z below or equal to the threshold
                frames_below_threshold += 1

            if prev_y is not None:
                delta = abs(this_y - prev_y)
                if delta > 0:  # Only consider positive delta
                    frames_with_y_delta += 1
                if delta > 0 and this_z <= z_max:  # Only include deltas where Z is below threshold
                    deltas.append(delta * facing_direction)  # Multiply by facing direction

            prev_y = this_y

    avg_delta = sum(deltas) / len(deltas) if deltas else 0
    return {
        "average_delta": avg_delta,
        "foot_bone_count": len(bones),
        "frames_below_threshold": frames_below_threshold,
        "frames_with_y_delta": frames_with_y_delta,
        "total_frames_analyzed": total_frames,
        "min_y": min_y,
        "max_y": max_y,
        "min_z": min_z,
        "max_z": max_z,
        "z_max": z_max,
        "foot_bone_names": [bone.name for bone in bones],
        "facing_direction": facing_direction,
        "action_name": action_name  # Add action name for later display
    }


def register():
    bpy.utils.register_class(LandSpeedAnalysisSettings)
    bpy.utils.register_class(LandSpeedAnalysisPanel)
    bpy.utils.register_class(LandSpeedAnalysisOperator)
    bpy.utils.register_class(DialogOperator)
    bpy.types.Scene.land_speed_analysis_settings = bpy.props.PointerProperty(type=LandSpeedAnalysisSettings)


def unregister():
    bpy.utils.unregister_class(LandSpeedAnalysisSettings)
    bpy.utils.unregister_class(LandSpeedAnalysisPanel)
    bpy.utils.unregister_class(LandSpeedAnalysisOperator)
    bpy.utils.unregister_class(DialogOperator)
    del bpy.types.Scene.land_speed_analysis_settings


if __name__ == "__main__":
    register()
