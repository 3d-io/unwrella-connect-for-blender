import bpy
import queue
import subprocess
import threading
import time
from .app_params import unwrellaParams
from .data_exchange import DataExchange
from .map_handler import MapHandler
from .message_params import (QueueMessage, QueueMsgSeverity)
from .util import Util

class Processing:

  def __init__(self, doQuickPack=False):
    self.quickPack = doQuickPack

  def execute(self, operator, context):
    if len(context.selected_objects) == 0:
      self.update_status(operator, "No objects are selected!", "ERROR")
      return {"FINISHED"}

    unique_objects = Util.get_unique_objects(context.selected_objects)
    meshes = Util.get_meshes(unique_objects)
    if len(meshes) == 0:
      self.update_status(operator, "None of the selected objects can be processed.", "ERROR")
      return {"FINISHED"}

    # The active object must be one of those we process
    activeObj = context.view_layer.objects.active
    if activeObj not in meshes:
      context.view_layer.objects.active = meshes[0]

    self.timer = time.time()
    self.coverage = 0.0
    self.density = 0.0
    self.sceneScale = context.scene.unit_settings.scale_length
    self.dispUnit = Util.get_scale_display_unit()
    unwrella_props = context.scene.UnwrellaProps

    if unwrella_props.uio_create_channel:
      MapHandler.set_map_name(unwrella_props.uio_channel_name)
      MapHandler.add_map_to_objects(unique_objects)

    options = {
      "Width": unwrella_props.uio_width,
      "Height": unwrella_props.uio_height,
      "PackMode": int(unwrella_props.uio_engine),
      "Padding": unwrella_props.uio_padding,
      "UseDensity": unwrella_props.uio_use_density,
      "Density": unwrella_props.uio_density * self.sceneScale,
      "Combine": unwrella_props.uio_combine,
      "Rescale": unwrella_props.uio_rescale,
      "PreRotate": unwrella_props.uio_prerotate,
      "FullRotation": unwrella_props.uio_fullRotate,
      "Rotation": int(unwrella_props.uio_rotate),
      "DynamicTiling": unwrella_props.uio_dynamicTiling,
      "TilesX": unwrella_props.uio_tilesX,
      "TilesY": unwrella_props.uio_tilesY,
    }

    if (self.quickPack):
      options = {
        "Width": unwrella_props.bl_rna.properties['uio_width'].default,
        "Height": unwrella_props.bl_rna.properties['uio_height'].default,
        "PackMode": int(unwrella_props.bl_rna.properties['uio_engine'].default),
        "Padding": unwrella_props.bl_rna.properties['uio_padding'].default,
        "UseDensity": unwrella_props.bl_rna.properties['uio_use_density'].default,
        "Density": unwrella_props.bl_rna.properties['uio_density'].default * self.sceneScale,
        "Combine": unwrella_props.bl_rna.properties['uio_combine'].default,
        "Rescale": unwrella_props.bl_rna.properties['uio_rescale'].default,
        "PreRotate": unwrella_props.bl_rna.properties['uio_prerotate'].default,
        "FullRotation": unwrella_props.bl_rna.properties['uio_fullRotate'].default,
        "Rotation": int(unwrella_props.bl_rna.properties['uio_rotate'].default),
        "DynamicTiling": unwrella_props.bl_rna.properties['uio_dynamicTiling'].default,
        "TilesX": unwrella_props.bl_rna.properties['uio_tilesX'].default,
        "TilesY": unwrella_props.bl_rna.properties['uio_tilesY'].default,
      }

    localOptions = {
      "QuickPack": self.quickPack,
      "Selection": unwrella_props.uio_selection_only,
    }

    try:
      operator.process = subprocess.Popen([unwrellaParams["appPath"], 'connect'], stdin=subprocess.PIPE,
        stdout=subprocess.PIPE, shell=False)
    except:
      msgStr = 'Unwrella-IO executable not found. Please refer to the Documentation for installation instructions.'
      self.update_status(operator, msgStr, "ERROR")
      return {"FINISHED"}

    bpy.ops.object.mode_set(mode = "EDIT")
    operator.msg_queue = queue.SimpleQueue()
    context.window_manager.modal_handler_add(operator)
    operator.unwrella_thread = threading.Thread(target=DataExchange.data_exchange_thread, args=(operator.process,
      options, localOptions, meshes, operator.msg_queue))
    operator.unwrella_thread.daemon = True
    operator.unwrella_thread.start()
    return {"RUNNING_MODAL"}

  def modal(self, operator, context, event):
    self.check_user_cancel(operator, event)
    if self.check_messages(operator):
      dispDensity = float(self.density) / self.sceneScale
      dispTime = round(time.time() - self.timer, 2)
      context.scene.UnwrellaProps.uio_stats = f"{self.coverage}%  ¦  {dispDensity}px/{self.dispUnit}  ¦  {dispTime}s"
      bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
      return {"FINISHED"}
    if not operator.unwrella_thread.is_alive() and operator.process.poll() is not None:
      operator.msg_queue.put((QueueMessage.COMPLETE, 1))
    return {"RUNNING_MODAL"}

  def update_status(self, operator, msg, severity="INFO"):
    operator.report({severity}, msg)

  def check_user_cancel(self, operator, event):
    if event.type == "ESC":
      operator.process.terminate()
      operator.update_status("Unwrella-IO process cancelled.")

  def check_messages(self, operator):
    while True:
      try:
        item = operator.msg_queue.get_nowait()
      except queue.Empty as ex:
        break

      if item[0] == QueueMessage.PROGRESS:
        progress_str = "Progress: %d %%" % (int(item[1] * 100.0))
        self.update_status(operator, progress_str)
      elif item[0] == QueueMessage.MESSAGE:
        if (len(item) > 2):
          if (item[2] == QueueMsgSeverity.WARNING):
            self.update_status(operator, item[1], "WARNING")
          elif (item[2] == QueueMsgSeverity.ERROR):
            self.update_status(operator, item[1], "ERROR")
            Util.show_message_box(item[1], "Error", "ERROR")
          else:
            self.update_status(operator, item[1], "INFO")
        else:
          self.update_status(operator, item[1], "INFO")
      elif item[0] == QueueMessage.STATS:
        self.coverage = item[1]
        self.density = item[2]
      elif item[0] == QueueMessage.COMPLETE:
        return True
    return False