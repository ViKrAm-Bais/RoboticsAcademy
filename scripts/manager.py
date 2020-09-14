#!/usr/bin/env python3
import sys
print(sys.path)

import asyncio
import websockets
import os
import threading
import time

async def kill_simulation():
    cmd_gzweb = "pkill -9 -f host.py"
    os.popen(cmd_gzweb)
    cmd_host = "pkill -9 -f node"
    os.popen(cmd_host)
    cmd_host = "pkill -9 -f gzserver"
    os.popen(cmd_host)
    cmd_ros = "pkill -9 -f roslaunch"
    os.popen(cmd_ros)
    cmd_rosout = "pkill -9 -f rosout"
    os.popen(cmd_rosout)
    cmd_mel = "pkill -9 -f melodroot"
    os.popen(cmd_mel)
    cmd_rosout = "pkill -9 -f rosout"
    os.popen(cmd_rosout)
    """cmd_py = "pkill -9 -f python"
    os.popen(cmd_py)"""

class DockerThread(threading.Thread):
    def __init__(self, cmd):
        threading.Thread.__init__(self)
        self.cmd = cmd

    def run(self):
        stream = os.popen(self.cmd)
        out = stream.read()
        print(out)

async def hello(websocket, path):
    #name = await websocket.recv()
    print(websocket)
    async for name in websocket:
        print(name)
        if name == "open":
            print("> Starting simulation")
            xvfb_cmd = "/usr/bin/Xvfb :0 -screen 0 1024x768x16"
            xvfb_thread = DockerThread(xvfb_cmd)
            xvfb_thread.start()

            roslaunch_cmd = '/bin/sh -c "export PWD="/";chmod +rwx /;export DISPLAY=:0;export OLDPWD=/etc/ros/rosdep;cd /;export LD_LIBRARY_PATH=/opt/ros/melodic/lib:/usr/lib/x86_64-linux-gnu/gazebo-9/plugins;export GAZEBO_MODEL_PATH=/usr/share/gazebo-9/models:$GAZEBO_MODEL_PATH;export GAZEBO_MODEL_DATABASE_URI=http://gazebosim.org/models;export ROS_DISTRO=melodic;export PKG_CONFIG_PATH=/opt/ros/melodic/lib/pkgconfig;export OGRE_RESOURCE_PATH=/usr/lib/x86_64-linux-gnu/OGRE-1.9.0;export SHLVL=1;export GAZEBO_PLUGIN_PATH=/usr/lib/x86_64-linux-gnu/gazebo-9/plugins:;export TERM=xterm;export ROS_VERSION=1;export GAZEBO_MASTER_URI=http://localhost:11345;ROS_ETC_DIR=/opt/ros/melodic/etc/ros;export CMAKE_PREFIX_PATH=/opt/ros/melodic;export ROS_PACKAGE_PATH=/opt/ros/melodic/share; chmod +x /opt/ros/melodic/bin/rosmaster;export ' \
                  'PYTHONPATH=/opt/ros/melodic/lib/python2.7/dist-packages; chmod +x /opt/ros/melodic/bin/roslaunch ; cd ' \
                  '/; export ROS_ROOT=/opt/ros/melodic/share/ros;export GAZEBO_RESOURCE_PATH=/usr/share/gazebo9:$GAZEBO_RESOURCE_PATH; export ' \
                  'ROS_MASTER_URI=http://localhost:11311; export PATH=/opt/ros/melodic/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin; /opt/ros/melodic/bin/roslaunch ' \
                  './RoboticsAcademy/exercises/follow_line/web-template/launch/simple_line_follower_ros_headless.launch" '
           #roslaunch_cmd = 'roslaunch ./RoboticsAcademy/exercises/car_junction/launch/car.launch'
            roslaunch_thread = DockerThread(roslaunch_cmd)
            roslaunch_thread.start()
            time.sleep(5)
            #stream = os.popen(gzweb_cmd)

            gzweb_cmd = 'cd /gzweb; npm start -p 8080'
            gzweb_thread = DockerThread(gzweb_cmd)
            gzweb_thread.start()

            host_cmd = "python /RoboticsAcademy/exercises/follow_line/web-template/host.py 0.0.0.0"
            host_thread = DockerThread(host_cmd)
            host_thread.start()
        elif name == "resume":
            print("RESUME SIMULATIOn")
            cmd = "/opt/ros/melodic/bin/rosservice call gazebo/unpause_physics"
            rosservice_thread = DockerThread(cmd)
            rosservice_thread.start()
        elif name == "stop":
            print("STOP SIMULATIOn")
            cmd = "/opt/ros/melodic/bin/rosservice call gazebo/pause_physics"
            rosservice_thread = DockerThread(cmd)
            rosservice_thread.start()
        elif name == "start":
            cmd = "/opt/ros/melodic/bin/rosservice call gazebo/unpause_physics"
            rosservice_thread = DockerThread(cmd)
            rosservice_thread.start()
        elif name == "reset":
            cmd = "/opt/ros/melodic/bin/rosservice call gazebo/reset_simulation"
            rosservice_thread = DockerThread(cmd)
            rosservice_thread.start()
        else:
            print("ALL KILED")
            await kill_simulation()

        greeting = f"Hello {name}!"

        await websocket.send("Done")
        #print(f"> {greeting}")

start_server = websockets.serve(hello, "0.0.0.0", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()