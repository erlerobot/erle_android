# -*- encoding: utf-8 -*-
'''
                                          
 _____     _        _____     _       _   
|   __|___| |___   | __  |___| |_ ___| |_ 
|   __|  _| | -_|  |    -| . | . | . |  _|
|_____|_| |_|___|  |__|__|___|___|___|_|  
                                          
@author: Víctor Mayoral Vilches <victor@erlerobot.com>
@description: A server written in python for the android client of the robot Erle.
'''
from bluetooth import *
import binascii

while True:
  server_sock=BluetoothSocket( RFCOMM )
  server_sock.bind(("",PORT_ANY))
  server_sock.listen(2)

  port = server_sock.getsockname()[1]

  uuid = "00001101-0000-1000-8000-00805F9B34FB"

  advertise_service( server_sock, "SampleServer",
                     service_id = uuid,
                     service_classes = [ uuid, SERIAL_PORT_CLASS ],
                     profiles = [ SERIAL_PORT_PROFILE ],
#                     protocols = [ OBEX_UUID ]
                      )

  print("Waiting for connection on RFCOMM channel %d" % port)

  client_sock, client_info = server_sock.accept()
  print("Accepted connection from ", client_info)

  try:
      while True:
          data = client_sock.recv(1024)
          if len(data) == 0: break              
          firstByte = data[0]
          firstByte_hexlify = binascii.hexlify(data[0])

          if firstByte == "U":
            print "U received"
          elif firstByte == "T":
            print "T received"
          elif firstByte == "A":
            print "A received"
          elif firstByte == "B":
            print "B received"
          elif firstByte == "C":
            print "C received"
          elif firstByte == "D":
            print "D received"
          else:
            pass

          # # print data
          # print "-----"
          # for d in data:
          #   print binascii.hexlify(d)

  except IOError:
      #pass
      print("disconnected")
      client_sock.close()
      server_sock.close()

print("all done")