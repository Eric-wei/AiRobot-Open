# import os

# # 设置为树莓派5的配置
# os.environ['BLINKA_FORCEBOARD'] = 'RASPBERRY_PI_5'
# os.environ['BLINKA_FORCECHIP'] = 'BCM2XXX'

from adafruit_servokit import ServoKit
import time  # 添加时间模块用于动画效果


class Arm_Right:
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
        if Arm_Right._initialized:
            return
       
        # 初始化左手四个关节
        self.kit = ServoKit(channels=16)
        self.right_arm1 = self.kit.servo[8]
        self.right_arm2 = self.kit.servo[9]
        self.right_arm3 = self.kit.servo[10]
        self.right_arm4 = self.kit.servo[11]
       
        # 设置脉冲宽度范围(500-2500微秒)，对应0.5ms-2.5ms
        self.right_arm1.set_pulse_width_range(500, 2650)
        self.right_arm2.set_pulse_width_range(500, 2580)
        self.right_arm3.set_pulse_width_range(500, 2650)
        self.right_arm4.set_pulse_width_range(450, 2750)

        # 设置舵机的可动角度范围(0-180度)
        self.right_arm1.actuation_range = 180
        self.right_arm2.actuation_range = 180
        self.right_arm3.actuation_range = 180
        self.right_arm4.actuation_range = 180
       
         # 四个手关节的初始化角度信息
        self.initialize_angle = [90, 180, 90, 0]