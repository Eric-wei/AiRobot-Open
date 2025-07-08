# import os

# # 设置为树莓派5的配置
# os.environ['BLINKA_FORCEBOARD'] = 'RASPBERRY_PI_5'
# os.environ['BLINKA_FORCECHIP'] = 'BCM2XXX'

from adafruit_servokit import ServoKit
import time  # 添加时间模块用于动画效果


class Arm_Left:
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, debug=False):
        """
        初始化手臂控制器（单例模式）
        """
        # 确保 __init__ 只执行一次
        if Arm_Left._initialized:
            return
       
        # 初始化左手四个关节
        self.kit = ServoKit(channels=16)
        self.left_arm1 = self.kit.servo[12]
        self.left_arm2 = self.kit.servo[13]
        self.left_arm3 = self.kit.servo[14]
        self.left_arm4 = self.kit.servo[15]
       
        # 设置脉冲宽度范围(500-2500微秒)，对应0.5ms-2.5ms
        self.left_arm1.set_pulse_width_range(500, 2580)
        self.left_arm2.set_pulse_width_range(500, 2680)
        self.left_arm3.set_pulse_width_range(500, 2780)
        self.left_arm4.set_pulse_width_range(450, 2600)

        # 设置舵机的可动角度范围(0-180度)
        self.left_arm1.actuation_range = 180
        self.left_arm2.actuation_range = 180
        self.left_arm3.actuation_range = 180
        self.left_arm4.actuation_range = 180
       
         # 四个手关节的初始化角度信息
        self.initialize_angle = [90, 0, 90, 180]




