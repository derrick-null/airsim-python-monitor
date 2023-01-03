import tornado.ioloop    
import tornado.web
import tornado.websocket
import tornado.httpserver
import setup_path 
import airsim

import cv2 #conda install opencv
import time
import logging
import os
import json
from threading import Thread
import uuid

import urllib.parse
import urllib.request

os.chdir("./")
logging.basicConfig(filename='as-py-client.log', level=logging.INFO) 
logger = logging.getLogger('logger')

formatter = logging.Formatter('%(threadName)s - %(thread)d - %(asctime)s - %(funcName)s - %(levelname)s - %(message)s')

flogHandler = logging.FileHandler('as-py-client.log')
flogHandler.setLevel(logging.INFO)

consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.INFO)

flogHandler.setFormatter(formatter)
consoleHandler.setFormatter(formatter)

logger.addHandler(flogHandler)
logger.addHandler(consoleHandler)

connections = {}
class ConnStatus():
    def add_conn(self, user):
        #if user not in self.connections:
        connections['asClient'] = user
        logger.info("Front end connected")
    def remove_conn(self, user):
        if connections:
            del connections['asClient']
            logger.info("Front end disconnected")
    def sendMsg(self, message):
        if connections:
            conn = connections['asClient']
            conn.write_message(message)
            logger.info("Send msg to front end: " + message)
class FinishProcessHandler(tornado.web.RequestHandler):
    def get(self):
        p=self.get_argument("p", None, True)
        self.write("The param is: " + p)
        logger.info("Receive msg through Get method: " + p)
    def post(self):
        try:
            paramBody = self.request.body.decode('utf-8')
            param = json.loads(paramBody)
            logger.info("Finishing process request from AI:" + paramBody)
            result = {}
            result['result'] = 'success'
            param['msgType'] = 'finish'
            ConnStatus().sendMsg(json.dumps(param))
            self.write(json.dumps(result))
        except Exception as e:
            logger.critical(e, exc_info=True)
    def set_default_headers(self):
        self.set_header("Content-Type", 'application/json')

class WSHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self,request):
        return True
    def open(self):
        ConnStatus().add_conn(self)
        self.write_message('OK')
    def on_close(self):
        ConnStatus().remove_conn(self)
    def on_message(self, message):
        self.write_message('OK')

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("This is index handler")


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/index', IndexHandler),
            (r'/airsim', WSHandler),
            (r'/finishProcess', FinishProcessHandler)
        ]
        tornado.web.Application.__init__(self, handlers)
        
class AIClient():
    def notify(self, uuid):
        try:
            url = "http://localhost:8088/mockServer"
            param = {}
            param['id'] = uuid
            req_json = json.dumps(param)
            req_post = req_json.encode('utf-8')
            logger.info("Params for request AI:" + req_json)
            headers = {'Content-Type': 'application/json'}
            req = urllib.request.Request(url=url, headers=headers, data=req_post)
            res = urllib.request.urlopen(req)
            if res:
                res = res.read().decode('utf-8')
                logger.info("Response from AI:", res)
        except Exception as e:
            logger.critical(e, exc_info=True)

def monitorCarState():
    client = airsim.CarClient()
    client.confirmConnection()
    start = time.time()
    # monitor car state while you drive it manually.
    while True:
        collisionInfo = client.simGetCollisionInfo()
        carState = client.getCarState()
        #print("monitoring the vehicle state")
        result = {}
        result['id'] = str(uuid.uuid4())
        if collisionInfo.has_collided: 
            AIClient().notify(result['id'])
            logger.info("Collision detected and notifying AI:" + result['id'])
        collisionResult = getCollisionInfo(collisionInfo, carState, result)
        #print(collisionResult)
        ConnStatus().sendMsg(collisionResult)
        time.sleep(1)

def getCollisionInfo(collisionInfo, carState, result):
    #position = collision_info.position
    #normal = collision_info.normal
    #position = collision_info.position
    #impact_point = collision_info.impact_point
    #penetration_depth = collision_info.penetration_depth
    result['hasCollided'] = collisionInfo.has_collided
    result['speed'] = carState.speed
    result['rpm'] = carState.rpm
    return json.dumps(result, indent=3)

if __name__ == "__main__":
    
    app = Application()
    app.listen(9001)
    loop = tornado.ioloop.IOLoop.current()
    thread = Thread(target=monitorCarState)
    thread.start()
    loop.start()
    
