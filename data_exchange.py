import struct
from .geometry_io import GeometryIO
from .message_params import (QueueMessage, QueueMsgSeverity)

class DataExchange:

  def data_exchange_thread(process, options, localOptions, meshes, msg_queue):
    msg_queue.put((QueueMessage.MESSAGE, "Preparing geometry"))

    geometryData, usedFaces = GeometryIO.gather_geometry_data(meshes, localOptions)
    binaryData = bytearray()
    interfaceVersion = (1, 1, 0)
    binaryData += (interfaceVersion[0]).to_bytes(4, byteorder="little")
    binaryData += (interfaceVersion[1]).to_bytes(4, byteorder="little")
    binaryData += (interfaceVersion[2]).to_bytes(4, byteorder="little")
    binaryData += DataExchange.encode_options(options)
    binaryData += geometryData
    sumBytes = len(binaryData)
    binaryData = sumBytes.to_bytes(4, byteorder="little") + binaryData

    msg_queue.put((QueueMessage.MESSAGE, "Processing"))

    try:
      out_stream = process.stdin
      out_stream.write(binaryData)
      out_stream.flush()

      message = ""
      while True:
        messageSize = struct.unpack("<I", process.stdout.read(4))[0]
        message = process.stdout.read(messageSize)
        readPtr = 0
        messageType = struct.unpack_from("<I", message, readPtr)[0]
        readPtr += 4
        if messageType == 0: # success
          break
        elif messageType == 1: # progress
          msg_queue.put((QueueMessage.PROGRESS, struct.unpack_from("<d", message, readPtr)[0]))
        elif messageType == 2: # error
          msgSize = struct.unpack_from("<I", message, readPtr)[0]
          readPtr += 4
          msg = message[readPtr:readPtr+msgSize].decode()
          msg_queue.put((QueueMessage.MESSAGE, msg, QueueMsgSeverity.ERROR))
          return
        else:
          print("Error: unsupported message " + str(messageType))

      numObjects = struct.unpack_from("<I", message, readPtr)[0]
      readPtr += 4
      for obj in range(0, numObjects):
        objId = struct.unpack_from("<I", message, readPtr)[0]
        readPtr += 4
        readPtr = GeometryIO.update_object_data(meshes[objId], message, readPtr, localOptions["Selection"], usedFaces[objId])

      coverage = struct.unpack_from("<d", message, readPtr)[0]
      readPtr += 8
      density = struct.unpack_from("<d", message, readPtr)[0]
      msg_queue.put((QueueMessage.STATS, str(round(coverage, 2)), str(round(density, 2))))
      msg_queue.put((QueueMessage.MESSAGE, "Packing complete", QueueMsgSeverity.WARNING))
    except:
      return

  def encode_options(options):
    data = bytearray()
    data += (options["Width"]).to_bytes(4, byteorder="little")
    data += (options["Height"]).to_bytes(4, byteorder="little")
    data += (options["PackMode"]).to_bytes(4, byteorder="little")
    data += bytearray(struct.pack("<d", options["Padding"]))
    data += bytearray(struct.pack("<?", options["UseDensity"]))
    data += bytearray(struct.pack("<d", options["Density"]))
    data += bytearray(struct.pack("<?", options["Combine"]))
    data += bytearray(struct.pack("<?", options["Rescale"]))
    data += bytearray(struct.pack("<?", options["PreRotate"]))
    data += bytearray(struct.pack("<?", options["FullRotation"]))
    data += (options["Rotation"]).to_bytes(4, byteorder="little")
    data += bytearray(struct.pack("<?", options["DynamicTiling"]))
    data += (options["TilesX"]).to_bytes(4, byteorder="little")
    data += (options["TilesY"]).to_bytes(4, byteorder="little")
    return data