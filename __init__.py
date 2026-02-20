import bpy
import bpy.utils.previews
import os
from .app_params import unwrellaParams
from .gui_panel import UnwrellaPanel
from .operators import (UnwrapOperator, QuickPackOperator, SizeOperator, RotationOperator, FullRotationOperator,
  ClearMapOperator)
from .object_properties import UnwrellaObjectProperties
from .properties import UnwrellaProperties
from .preferences import UnwrellaPreferences
from .util import Util

registered_classes = []
classes = (UnwrellaPreferences, UnwrellaProperties, UnwrellaObjectProperties, UnwrellaPanel, UnwrapOperator,
  QuickPackOperator, SizeOperator, RotationOperator, FullRotationOperator, ClearMapOperator)

subscriptionOwner = object()

def active_obj_callback():
  for area in bpy.context.screen.areas:
    if area.type == "IMAGE_EDITOR":
      area.tag_redraw()

def register():
  bpy.msgbus.subscribe_rna(
    key=(bpy.types.LayerObjects, 'active'),
    owner=subscriptionOwner,
    args=(),
    notify=active_obj_callback
  )

  for cls in classes:
    bpy.utils.register_class(cls)
    registered_classes.append(cls)
  bpy.types.Scene.UnwrellaProps = bpy.props.PointerProperty(type=UnwrellaProperties)
  bpy.types.Object.UnwrellaObjProps = bpy.props.PointerProperty(type=UnwrellaObjectProperties)

  unwrellaParams["appPath"], unwrellaParams["AppAccess"] = Util.get_app_path()

  iconCol = bpy.utils.previews.new()
  iconsDir = os.path.join(os.path.dirname(__file__), "icons")
  iconCol.load("unwrap_organic", os.path.join(iconsDir, "organic.svg"), 'IMAGE')
  iconCol.load("unwrap_hard", os.path.join(iconsDir, "hard.svg"), 'IMAGE')
  iconCol.load("unwrap_mosaic", os.path.join(iconsDir, "mosaic.svg"), 'IMAGE')
  iconCol.load("unwrap_pack", os.path.join(iconsDir, "pack.svg"), 'IMAGE')
  iconCol.load("unwrap_keep", os.path.join(iconsDir, "keep.svg"), 'IMAGE')
  iconCol.load("mark_grooves", os.path.join(iconsDir, "groove.svg"), 'IMAGE')
  iconCol.load("mark_ridges", os.path.join(iconsDir, "ridge.svg"), 'IMAGE')
  iconCol.load("unwrella_uv", os.path.join(iconsDir, "uv.svg"), 'IMAGE')
  unwrellaParams["icons"] = iconCol

def unregister():
  bpy.msgbus.clear_by_owner(subscriptionOwner)

  bpy.utils.previews.remove(unwrellaParams["icons"])

  for cls in registered_classes:
    bpy.utils.unregister_class(cls)
  del registered_classes[:]
  del bpy.types.Scene.UnwrellaProps
  del bpy.types.Object.UnwrellaObjProps

if __name__ == "__main__":
  register()