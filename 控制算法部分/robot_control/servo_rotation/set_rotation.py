from sqlalchemy import PoolResetState
from ..arms.arm_left import Arm_Left
from ..arms.arm_right import Arm_Right
from ..head.head_neck import Head_Neck
from .rotation_inf import Control_Inf, Rotation_Inf
from .rotation import Rotation
from ..expression.expression_inf import Expression_Inf
import time

class Set_Rotation():
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Set_Rotation, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # 防止重复初始化
        if not hasattr(self, 'initialized'):
            self.initialized = True
        self.arm_left = Arm_Left()
        self.arm_right = Arm_Right()
        self.head_neck = Head_Neck()
        self.rotation = Rotation()
        self.expression = Expression_Inf()
        self.servo_angle_now = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] #目前的角度值信息，初始化时为0
        self.expression_now = self.expression.expression_now
        self.initialize_angle = self.arm_left.initialize_angle + self.arm_right.initialize_angle + self.head_neck.initialize_angel
        # 初始化舵机控制信息
        initial_inf = [[0, 90, 30]]  # 初始化信息，没有作用
        self.rotation_inf_arm_left = [
            Rotation_Inf(servo=self.arm_left.left_arm1, inf=initial_inf),
            Rotation_Inf(servo=self.arm_left.left_arm2, inf=initial_inf),
            Rotation_Inf(servo=self.arm_left.left_arm3, inf=initial_inf),
            Rotation_Inf(servo=self.arm_left.left_arm4, inf=initial_inf)
        ]
        self.rotation_inf_all = [
            Rotation_Inf(servo=self.arm_left.left_arm1, inf=initial_inf),#四个左手信息
            Rotation_Inf(servo=self.arm_left.left_arm2, inf=initial_inf),
            Rotation_Inf(servo=self.arm_left.left_arm3, inf=initial_inf),
            Rotation_Inf(servo=self.arm_left.left_arm4, inf=initial_inf),
            Rotation_Inf(servo=self.arm_right.right_arm1, inf=initial_inf),#四个右手信息
            Rotation_Inf(servo=self.arm_right.right_arm2, inf=initial_inf),
            Rotation_Inf(servo=self.arm_right.right_arm3, inf=initial_inf),
            Rotation_Inf(servo=self.arm_right.right_arm4, inf=initial_inf),
            Rotation_Inf(servo=self.head_neck.head_rotation, inf=initial_inf),#头部信息
            Rotation_Inf(servo=self.head_neck.head_pitch, inf=initial_inf),
            Rotation_Inf(servo=self.head_neck.head_left_ear, inf=initial_inf),
            Rotation_Inf(servo=self.head_neck.head_right_ear, inf=initial_inf)

        ]

    def set_rotation_inf(self, control_inf_list: list[Control_Inf]) -> list[Rotation_Inf]: #检查control_inf控制参数并转化为控制舵机序列
        drive_servo_inf = []
        for control_inf in control_inf_list:
            if control_inf.servo_index < 0 or control_inf.servo_index > 15:
                raise ValueError("舵机引脚必须在0~15号")
            i = 0
            for angle_speed in control_inf.servo_angle_speed:
                if (angle_speed[0] < 0 or angle_speed[0] > 180) or (angle_speed[1] < 0 or angle_speed[1] > 180):
                    raise ValueError("舵机的控制角度必须在0~180°之间")
                if angle_speed[2] > 300:
                    raise ValueError("舵机的速度不能超过300°每秒")
                if not(len(angle_speed) == 3):
                    raise ValueError("舵机的控制参数必须是3个，初始角度，终止角度，速度")
                if i + 1 < len(control_inf.servo_angle_speed):
                    if not(angle_speed[1] == control_inf.servo_angle_speed[i+1][0]):
                       raise ValueError("舵机的控制角度之间间隔必须是连续的")
                i += 1
            self.rotation_inf_all[control_inf.servo_index].inf = control_inf.servo_angle_speed
            self.rotation_inf_all[control_inf.servo_index].is_done = False
            self.rotation_inf_all[control_inf.servo_index].inf_index = 0
            drive_servo_inf.append(self.rotation_inf_all[control_inf.servo_index])
        return drive_servo_inf
    
    def set_rotation_inf_by_list(self, control_inf_list: list[list[list[float]]]) -> list[Rotation_Inf]: #检查列表控制参数参数并转化为控制舵机序列
        drive_servo_inf = []
        for control_inf in control_inf_list:
            i = 0
            for index_or_speed in control_inf:
                if i == 0:
                    if index_or_speed < 0 or index_or_speed > 15:
                        raise ValueError("舵机引脚必须在0~15号")  
                else:
                    if (index_or_speed[0] < 0 or index_or_speed[0] > 180) or (index_or_speed[1] < 0 or index_or_speed[1] > 180):
                        raise ValueError("舵机的控制角度必须在0~180°之间")
                    if index_or_speed[2] > 3000:
                        raise ValueError("舵机的速度不能超过3000°每秒")
                    if not(len(index_or_speed) == 3):
                        raise ValueError("舵机的控制参数必须是3个，初始角度，终止角度，速度")
                    if i + 1 < len(control_inf) :
                        if not(index_or_speed[1] == control_inf[i+1][0]):
                            raise ValueError("舵机的控制角度之间间隔必须是连续的")
                i += 1
            self.rotation_inf_all[control_inf[0]].inf = control_inf[1:]
            self.rotation_inf_all[control_inf[0]].is_done = False
            self.rotation_inf_all[control_inf[0]].inf_index = 0
            drive_servo_inf.append(self.rotation_inf_all[control_inf[0]])
            print (control_inf)
        return drive_servo_inf

    def drive_normal_rotation(self, control_inf_list: list[Control_Inf]):# 驱动普通旋转
        drive_servo_inf = self.set_rotation_inf(control_inf_list)
        self.rotation.rotaion_normal(drive_servo_inf)

    def drive_normal_rotation_by_list(self, control_inf_list: list[list[list[float]]]):# 驱动普通旋转通过列表
        drive_servo_inf = self.set_rotation_inf_by_list(control_inf_list)
        self.rotation.rotaion_normal(drive_servo_inf)


    def drive_initalize_servo(self, initialize_time: int = 2): # 驱动舵机初始化
        for i in range(len(self.rotation_inf_all)):
            self.rotation_inf_all[i].servo.angle = self.initialize_angle[i]
        self.get_servo_angle_now()
        time.sleep(initialize_time)

    def drive_close_servo(self, control_inf_list: list[Control_Inf]):
        drive_servo_inf = self.set_rotation_inf(control_inf_list)
        self.rotation.close_servo(drive_servo_inf)

    def drive_animation(self,animation_list: list[list[list[list[float]]]]): #执行一个完整的动作序列
        for control_inf_list in animation_list:
            self.drive_normal_rotation_by_list(control_inf_list)
        
    def drive_expression(self, expression: str): #执行一个给定的表情
        animation = self.expression.get_expression_animation(expression)
        self.expression_now = str
        self.drive_animation(animation)

    def get_servo_angle_now(self): #获得当前所有舵机的角度
        for i in range(len(self.servo_angle_now)):
            self.servo_angle_now[i] = round(self.rotation_inf_all[i].servo.angle)

    def drive_expression_list(self,expression_list : list): #执行一个表情列表
        self.drive_expression(expression_list[0])
        self.get_servo_angle_now()
        for expression in expression_list[1:]:
            if not (isinstance(expression, str) or isinstance(expression, float)):
                raise ValueError("表情列表中表情标签必须是字符串类型与间隔时间！")
            if isinstance(expression, float):# 进行暂停间隔
                time.sleep(expression)
            else :
                if expression == "结束":
                    animation = self.expression.get_transition_animation(label=expression, servo_angle_now=self.servo_angle_now)
                    self.expression_now = str
                    self.drive_animation(animation)
                else:
                    animation = self.expression.get_expression_animation(expression)
                    animation[0] = self.expression.get_transition_animation(label=expression, servo_angle_now=self.servo_angle_now)[0] #将第一个动作改为过渡动作
                    self.expression_now = str
                    self.drive_animation(animation)
            self.get_servo_angle_now()

                
           