# airsim-python-monitor
Monitoring the airsim vehicle status and notifying the client by using websocket.

# demo-airsim-python-client
The python client of Airsim for the demonstration in the demo room.
Following python files are based on the orginal code from AirSim, please update code accordingly.
- setup_path.py

# Install Guidelines
## Install dependencies
You need to install following dependencies, please refer to the official documents. 

[Build on Windows](https://microsoft.github.io/AirSim/build_windows/)

[Python API](https://microsoft.github.io/AirSim/api_docs/html/#)

- Epic Unreal Engine 4.27
- Microsoft Visual Studio
- Python 3.9.9
- Git
- Install AirSim from Github

## Install python packages
- pip install airsim
- pip install numpy
- pip install msgpack-rpc-python
- pip install opencv-contrib-python
- pip install tornado

# ws-tornado.py
Monitoring the AirSim and serveing the websocket to push message to frontend.

# settings.json
The settings.json is the default config from AirSim repository, and AirSim will load this file from the default directory. The directory in windows is: "C:\Users\cccis\Documents\AirSim\settings.json"
