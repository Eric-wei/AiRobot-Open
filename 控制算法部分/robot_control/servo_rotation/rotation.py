from adafruit_servokit import ServoKit
from .rotation_inf import Rotation_Inf
from math import pi
import time #控制舵机的速度时需要


class Rotation:
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, sleep_time: float = 0.01):
        """
        初始化手臂控制器（单例模式）
        """
        # 确保 __init__ 只执行一次
        if Rotation._initialized:
            return
        self.sleep_time = sleep_time #舵机旋转的最小间隔时间
        self.is_tuch_number = 1 #在旋转中判断舵机是否到给定值的最小误差范围
       
    def rotaion_normal(self, rotation_inf_list: list[Rotation_Inf]):
        # TODO: 实现舵机在给定的起点给，终点和速度进行控制
        while True:
            all_done = True
            direction = 1
            for servo_inf in rotation_inf_list:
                if not servo_inf.is_done:
                    if abs(servo_inf.inf[servo_inf.inf_index][1] - servo_inf.inf[servo_inf.inf_index][0]) > 1:
                        # 更新角度（非阻塞）,此时还没有转动到目标位置
                        direction = 1 if  servo_inf.inf[servo_inf.inf_index][1] - servo_inf.inf[servo_inf.inf_index][0]> 0 else -1
                        step = servo_inf.inf[servo_inf.inf_index][2] * self.sleep_time * direction 
                        servo_inf.inf[servo_inf.inf_index][0] += direction*min(abs(step), abs(servo_inf.inf[servo_inf.inf_index][1] - servo_inf.inf[servo_inf.inf_index][0]))
                        servo_inf.servo.angle = servo_inf.inf[servo_inf.inf_index][0]
                        all_done = False
                    else:
                        servo_inf.servo.angle = servo_inf.inf[servo_inf.inf_index][1]
                        if  servo_inf.inf_index+1 < len(servo_inf.inf) :
                            servo_inf.inf_index += 1
                            all_done = False
                        else:
                            servo_inf.is_done = True
            if all_done:
                break
            time.sleep(self.sleep_time)
    
    

    
    def rotaion_initialize(self, rotation_inf_list: list[Rotation_Inf], initialize_time: int = 2):
        # 用来对起始角度不知道的舵机设置初始化角度
        for servo_inf in rotation_inf_list:
            servo_inf.servo.angle = servo_inf.inf[0][1]
        time.sleep(initialize_time)

    def close_servo(self, rotation_inf_list: list[Rotation_Inf]):
        for servo_inf in rotation_inf_list:
            servo_inf.servo.angle = None