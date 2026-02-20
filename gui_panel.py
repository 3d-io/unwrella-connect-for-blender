import bpy
from .app_params import (AppAccess, unwrellaParams)

class UnwrellaPanel(bpy.types.Panel):
  bl_label = "Unwrella"
  bl_idname = "UNWRELLAIO_PT_layout"
  bl_category = "Unwrella"
  bl_space_type = "IMAGE_EDITOR"
  bl_region_type = "UI"

  @classmethod
  def poll(self, context):
    return context.object is not None

  def draw(self, context):
    layout = self.layout
    unwrellaProps = context.scene.UnwrellaProps
    unwrellaObjProps = context.object.UnwrellaObjProps

    if (unwrellaParams["AppAccess"] != AppAccess.NONE):
      row = layout.row()
      row.scale_y = 3.0
      if (unwrellaParams["AppAccess"] == AppAccess.UNWRELLA_IO):
        row.operator("unwrellaoperator.unwrapbtn", text="Unwrap")
      else:
        row.operator("unwrellaoperator.unwrapbtn", text="Pack")
      row = layout.row()
      row.scale_y = 1.5
      row.operator("unwrellaoperator.quickpackbtn", text="Quick Pack")
      box = layout.box()
      box.label(text="Stats:     " + unwrellaProps.uio_stats)
      row = layout.row(align=True)
      row.prop(unwrellaProps, "uio_combine")
      row.label(text="", icon="BLANK1")
      row.prop(unwrellaProps, "uio_selection_only")

      layout.separator()
      multiFlag = ""
      numSelected = len(context.selected_objects)
      if (numSelected > 1):
        multiFlag = f" (+{numSelected-1})"
      if (unwrellaParams["AppAccess"] == AppAccess.UNWRELLA_IO):
        layout.label(text="Unwrap: " + context.object.name + multiFlag, icon="OUTLINER_OB_MESH")
        layout.prop(unwrellaObjProps, "uio_unwrap_mode", text="Mode")
      else:
        layout.label(text="Pack: " + context.object.name + multiFlag, icon="OUTLINER_OB_MESH")
        layout.prop(unwrellaObjProps, "uio_pack_mode", text="Mode")

      if (unwrellaParams["AppAccess"] == AppAccess.UNWRELLA_IO):
        row = layout.row(align=True)
        row.prop(unwrellaObjProps, "uio_keep_seams")
        row.label(text="", icon="BLANK1")
        row.prop(unwrellaObjProps, "uio_use_marks")

        row = layout.row(align=True)
        row.label(text="Stretch:")
        row.label(text="", icon="BLANK1")
        row.prop(unwrellaObjProps, "uio_stretch", text="")

        row = layout.row(align=True)
        row.label(text="Hard Angle:")
        row.label(text="", icon="BLANK1")
        row.prop(unwrellaObjProps, "uio_hard_angle", text="")

        row = layout.row(align=True)
        row.prop(unwrellaObjProps, "uio_cut_concave")
        row.label(text="", icon_value=unwrellaParams["icons"]["mark_grooves"].icon_id)
        row.prop(unwrellaObjProps, "uio_angle_concave", text="")
        row = layout.row(align=True)
        row.prop(unwrellaObjProps, "uio_cut_convex")
        row.label(text="", icon_value=unwrellaParams["icons"]["mark_ridges"].icon_id)
        row.prop(unwrellaObjProps, "uio_angle_convex", text="")
        layout.prop(unwrellaObjProps, "uio_cut_holes")

      layout.separator()
      layout.label(text="UV Map Options:", icon="TEXTURE_DATA")
      row = layout.row(align=True)
      row.scale_y = 1.5
      row.operator("unwrellaoperator.sizebtn", text="512").size = 512
      row.operator("unwrellaoperator.sizebtn", text="1k").size = 1024
      row.operator("unwrellaoperator.sizebtn", text="2k").size = 2048
      row.operator("unwrellaoperator.sizebtn", text="4k").size = 4096

      row = layout.row(align=True)
      row.alignment = "EXPAND"
      row.prop(unwrellaProps, "uio_width")
      row.prop(unwrellaProps, "uio_height")

      row = layout.row(align=True)
      row.label(text="Padding:")
      row.prop(unwrellaProps, "uio_padding", text="")

      row = layout.row(align=True)
      row.prop(unwrellaProps, "uio_use_density")
      row.prop(unwrellaProps, "uio_density", text="")
      layout.prop(unwrellaProps, "uio_dynamicTiling")
      layout.separator()

      layout.label(text="UV Packing Engine:", icon="MESH_GRID")
      layout.prop(unwrellaProps, "uio_engine", text="Method")
      layout.prop(unwrellaProps, "uio_rescale")
      layout.prop(unwrellaProps, "uio_prerotate")

      row = layout.row(align=True)
      row.scale_y = 1.5
      row.prop(unwrellaProps, "uio_rotate", expand=True)
      row.prop(unwrellaProps, "uio_fullRotate", toggle=True)

      row = layout.row(align=True)
      row.prop(unwrellaProps, "uio_tilesX")
      row.prop(unwrellaProps, "uio_tilesY")

      layout.separator()
      layout.prop(unwrellaProps, "uio_create_channel")
      row = layout.row(align=True)
      row.prop(unwrellaProps, "uio_channel_name")
      row.operator("unwrellaoperator.clearmaptoolbtn", text="" , icon="TRASH")

    else:
      layout.label(text="Unwrella-IO not found.", icon="ERROR")
      layout.label(text="This add-on requires Unwrella-IO")
      layout.label(text="or Blender-IO to be installed.")
      layout.label(text="If it is installed try setting the path")
      layout.label(text="manually in 'Preferences - Add-ons'.")
      layout.label(text="Check the documentation for details.")

    layout.separator()
    row = layout.row(align=True)
    row.scale_y = 1.5
    row.operator("wm.url_open", text="Homepage", icon="HOME").url = "https://www.unwrella.com"
    row.scale_y = 1.5
    row.operator("wm.url_open", text="Documentation" , icon="QUESTION").url = "https://docs.3d-plugin.com/unwrellaconnect-blender"