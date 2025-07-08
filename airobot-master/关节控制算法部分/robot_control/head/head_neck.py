from adafruit_servokit import ServoKit
import time  # 添加时间模块用于动画效果


class Head_Neck():
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
        if Head_Neck._initialized:
            return
       
        # 初始化脖子和两个耳朵关节
        self.kit = ServoKit(channels=16)
        self.head_rotation = self.kit.servo[6]
        self.head_pitch = self.kit.servo[7]
        self.head_left_ear = self.kit.servo[5]
        self.head_right_ear = self.kit.servo[4]
        
        #设置脉冲范围
        self.head_rotation.set_pulse_width_range(550, 2650)
        self.head_pitch.set_pulse_width_range(500, 2500)
        self.head_left_ear.set_pulse_width_range(550, 2650)
        self.head_left_ear.set_pulse_width_range(550, 2650)

        #设置旋转范围
        self.head_rotation.actuation_range = 180
        self.head_pitch.actuation_range = 180
        self.head_left_ear.actuation_range = 180
        self.head_right_ear.actuation_range = 180
        

        #设置初始角度
        self.initialize_angel = [90, 70, 60, 110]