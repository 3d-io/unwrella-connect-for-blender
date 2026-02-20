from bpy.types import PropertyGroup
from bpy.props import (StringProperty, BoolProperty, IntProperty, FloatProperty, EnumProperty)

class UnwrellaProperties(PropertyGroup):
  uio_combine: BoolProperty(name="Combine", description="Pack all selected objects in one UV Sheet", default = True)
  uio_selection_only: BoolProperty(name="Selection", description="Pack only selected faces", default = False)
  uio_width: IntProperty(name="w:", description="UV Sheet Width", default = 1024, min = 1)
  uio_height: IntProperty(name="h:", description="UV Sheet Height", default = 1024, min = 1)
  uio_padding: FloatProperty(name="Padding", description="Specifies the distance between UV charts within the texture.", default = 2.0, min = 0.0)
  uio_engine: EnumProperty(
    name="Dropdown:",
    description="Choose Packing method",
    items=[
      ("0", "Efficient", "Best compromise for speed and space usage"),
      ("1", "High Quality", "Slowest but maximal space usage"),
      ("2", "Turbo", "Fastest but leaves gaps and can't fill holes"),
    ],
    default="0"
  )
  uio_rescale: BoolProperty(name="Rescale UV-Charts", description="Enable to rescale UV charts based on their mesh surface area for uniform pixel distribution. Disable to keep original chart sizes after packing.", default=True)
  uio_prerotate: BoolProperty(name="Pre-Rotate", description="Optimizes the initial orientation of UV charts before packing, working independently of other rotation options.", default=True)
  uio_rotate: EnumProperty(
    name="Rotation:",
    description="Apply additional rotation angles to UV charts for better fit.",
    items=[
      ("0", "0°", "None"),
      ("1", "90°", "90 degrees"),
      ("2", "45°", "45 degrees"),
      ("3", "23°", "23 degrees")
    ],
    default="1"
  )
  uio_fullRotate: BoolProperty(name="Ø", description="Allow full 360° UV rotation; slower but can improve packing.", default=False)
  uio_dynamicTiling: BoolProperty(name="Dynamic Tiling", description="Determine the number of tiles dynamically based on density.", default=False)
  uio_tilesX: IntProperty(name="Tiles X:", description="UV Tile Columns", default=1, min=1)
  uio_tilesY: IntProperty(name="Tiles Y:", description="UV Tile Rows", default=1, min=1)
  uio_create_channel: BoolProperty(name="Create new map channel", description="Store UV results in a new map channel.", default=False)
  uio_channel_name: StringProperty(name="UV Map", description="Name the created UV channel.", default="Unwrella")
  uio_stats: StringProperty(name="Stats", description="View UV coverage, density, and calculation time.", default="Waiting for action...")
  uio_use_density: BoolProperty(name="Use Density", description="Toggle texel density control. When enabled, UVs are scaled to match the target density; when disabled, UVs maximize texture space usage with optional uniform scaling.", default=False)
  uio_density: FloatProperty(name="Density", description="Define the desired texel density (pixels per unit) to control UV island scaling.", default=100.0, min=0.0001)