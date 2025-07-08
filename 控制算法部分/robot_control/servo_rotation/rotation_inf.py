from unittest.mock import Base
from adafruit_motor.servo import Servo
from pydantic import BaseModel
from typing import Optional, Type

class Rotation_Inf():
    def __init__(self, servo:Servo, inf: list[list[int]], inf_index = 0, is_done: bool = True):
        if any(len(inf) != 3 for inf in inf):
            raise ValueError("每行必须有3个元素")
        self.inf = inf
        self.servo = servo
        self.is_done = is_done
        self.inf_index = inf_index
        #验证速度参数是否有问题

class Control_Inf(BaseModel):
    servo_index: int
    servo_angle_speed: list[list[int]]



       
    
