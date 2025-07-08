import string
from .action_smooth import Action_Smooth

class Expression_Inf():
    def __init__(self, ) -> None:
        
        self.expression_now = "初始化"
        self.transition_time = 1 #动作转换时每180度运动的时间
        self.generate_anction = Action_Smooth()
        self.initialize = [[[0, 0, 90], [1, 0, 0], [2, 0, 90], [3, 0, 180], [4, 0, 90], [5, 0, 180], [6, 0, 90], [7, 0, 0], [8, 0, 90], [9, 0, 70], [10, 0, 60], 
                            [11, 0, 110], 0.6, "human"]]    
        self.test_arm = [[[0, 90, 20], [1, 0, 20 ], [2, 90, 30], [3, 180, 100], [9, 70, 150], 0.6, "human"],
                         [[2, 30, 120], 0.3, "human"],
                         [[2, 120, 30], 0.3, "human"],
                         [[2, 30, 120], 0.3, "human"]]
        self.hellow = [[[0, 90, 20], [1, 0, 20 ], [2, 90, 30], [3, 180, 100], [9, 70, 180], [10, 60, 90], [11, 110, 90], 0.6, "human"],
                         [[2, 30, 120], 0.3, "human"],
                         [[2, 120, 30], 0.3, "human"],
                         [[2, 30, 120], 0.3, "human"]]                      
        self.proud = [[[1, 0, 40], [2 , 90, 160], [3, 180, 110], [5, 180, 140], [6, 90, 30], [7, 0, 70], [8, 90, 100], [9, 70, 180], [10, 60, 110], [11, 110, 60], 0.3, "human"],
                      [[1, 40, 10], [2, 160, 180], [3, 110, 90], [5, 140, 170], [6, 30, 20], [7, 70, 90], 0.1, "human"]]   


 
    def get_expression_animation(self, label: str) -> list[list[list[list[float]]]]:
        match label:
            case "测试手臂":
                return self.generate_anction.generate_smooth_animation_list(self.test_arm)
            case "骄傲":
                return self.generate_anction.generate_smooth_animation_list(self.proud)
            case "结束":
                return self.generate_anction.generate_smooth_animation_list(self.initialize)
            case "打招呼":
                return self.generate_anction.generate_smooth_animation_list(self.hellow)
            case _:
                raise ValueError("没有这个表情叫：%s" % (label))
    
    def get_expression_animation_O(self, label: str) -> list[list[list[float]]]:
        match label:
            case "测试手臂":
                return self.test_arm
            case "骄傲":
                return self.proud
            case "结束":
                return self.initialize
            case "打招呼":
                return self.hellow
            case _:
                raise ValueError("没有这个表情叫：%s" % (label))
            

    def get_transition_animation(self, label: str, servo_angle_now: list, config = "human") ->list[list[list[list[float]]]]:#得到当前表情到下一个表情的过渡动作
        animation_starts = self.get_expression_animation_O(label)[0][:-2]
        transition_animation = []
        start_servo_index = []
        max_angle = 0
        for animation in animation_starts: #获得第一运动帧的所以运动舵机下标
                start_servo_index.append(animation[0])
        for i in range(len(servo_angle_now)): #遍历所有运行的舵机
            if abs(servo_angle_now[i] - self.initialize[0][i][2]) > 1 and not i in start_servo_index: #将没有初始化且不在初始舵机内的舵机初始化
                transition_animation.append([i, servo_angle_now[i], self.initialize[0][i][2]])
        for animation_start in animation_starts: #把下一个表情的的第一个动作与当前的角度结合成一个过渡动作
            if abs(servo_angle_now[animation_start[0]] - animation_start[2]) > 1:
                transition_animation.append([animation_start[0], servo_angle_now[animation_start[0]], animation_start[2]])
                if abs(servo_angle_now[animation_start[0]] - animation_start[2]) > max_angle:
                    max_angle = abs(servo_angle_now[animation_start[0]] - animation_start[2])
        transition_animation.append(max_angle/180*self.transition_time) #用最大的相差角度计算出时间
        transition_animation.append(config)
        print(transition_animation)
        return self.generate_anction.generate_smooth_animation_list([transition_animation])

        

            

