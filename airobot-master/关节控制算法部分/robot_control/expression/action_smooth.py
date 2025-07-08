import numpy as np

class Smooth_Generate(): #五次多项式生成离散的顺滑运动轨迹
    def __init__(self) -> None:
        self.cdtime = 100
    #通过起始位置，终止位置，起始速度，终止速度，起始加速度，终止加速度，运动时间和离散采样时间计算出运动轨迹
    def calulate_trace(self, theta_start: float, theta_end: float, time : float, v_start: float = 0, v_end: float = 0, 
                       a_start: float = 0, a_end: float = 0, segment : int = 10) -> list[list[float]]: 
        theta0 = theta_start    # 起始角度 (°)
        thetaT = theta_end    # 终止角度 (°)
        v0 = v_start        # 起始速度 (°/s)
        vT = v_end         # 终止速度 (°/s)
        a0 = a_start        # 起始加速度 (°/s²)
        aT = a_end       # 终止加速度 (°/s²)
        T = time          # 总时间 (s)
        S = segment

        a0_coeff = theta0
        a1_coeff = v0
        a2_coeff = a0 / 2
        a3_coeff = (20*(thetaT - theta0) - (8*vT + 12*v0)*T - (3*a0 - aT)*T**2) / (2*T**3)
        a4_coeff = (30*(theta0 - thetaT) + (14*vT + 16*v0)*T + (3*a0 - 2*aT)*T**2) / (2*T**4)
        a5_coeff = (12*(thetaT - theta0) - 6*(vT + v0)*T - (aT - a0)*T**2) / (2*T**5)

        # 生成轨迹
        t = np.linspace(0, T, self.cdtime)
        theta_t = a0_coeff + a1_coeff*t + a2_coeff*t**2 + a3_coeff*t**3 + a4_coeff*t**4 + a5_coeff*t**5
        velocity_t = abs(a1_coeff + 2*a2_coeff*t + 3*a3_coeff*t**2 + 4*a4_coeff*t**3 + 5*a5_coeff*t**4)
        acceleration_t = 2*a2_coeff + 6*a3_coeff*t + 12*a4_coeff*t**2 + 20*a5_coeff*t**3
        # 生成运动段
        theta_segments = np.linspace(theta0, thetaT, S)  # 将一个角度范围划分为S段
        animation_segment = [] #动作序列
        for i in range(len(theta_segments)-1):
            if theta0 < thetaT:
                theta_min = float(theta_segments[i])
                theta_max = float(theta_segments[i+1])
            else:
                theta_max = float(theta_segments[i])
                theta_min = float(theta_segments[i+1])
            # 找到该角度范围内所有速度点
            mask = (theta_t >= theta_min) & (theta_t < theta_max)
            if np.any(mask):
                avg_speed = float(np.mean(velocity_t[mask]))
            else:
                # 若无数据点（罕见），插值或继承前一段速度
               if i > 0:
                    avg_speed = animation_segment[i-1][2]
               else:
                    avg_speed = 100
            if theta0 < thetaT:
              animation_segment.append([theta_min, theta_max, avg_speed])
            else:
              animation_segment.append([theta_max, theta_min, avg_speed])
        return list(animation_segment)
            

class Action_Smooth():
    def __init__(self):
        self.smooth = Smooth_Generate()
        self.preset_v = {
                         "fast_speed2": 200.0,
                         "fast_speed1": 150.0,
                         "medium_speed": 100.0,
                         "slow_speed1": 50.0,
                         "slow_speed2": 20.0
                        }
        self.preset_animation = {
            "normal": [0, 0, 0, 0],#预设的动作参数，依次是起始速度，终止速度，起始加速度，终止加速度
            "human": [200, 100, 200, 80]

        }
    
    def genarate_smooth_animation_one(self,angle: list[float], time : float, config : str) -> list[list[float]]: 
        if not(len(angle) == 2):
            raise ValueError("必须只包含角度的起点两个个值！")
        if (angle[0] > 180 or angle[0] < 0) or (angle[1] > 180 or angle[1] < 0):
            raise ValueError("角度值必须在0~180度之间")
        if abs(angle[0] - angle[1]) < 5:
            raise ValueError("角度值的起点和终点范围不能小于5")
        if not(time > 0):
            raise ValueError("时间必须大于0")
        if abs(angle[0] - angle[1])/time > 3000:
            raise ValueError("平均速度的值不能超过每秒3000°")
        if isinstance(config, str):
            if config in self.preset_animation:
                set_config = self.preset_animation[config]
            else:
                raise ValueError("没有一个叫%d的动作设置" % (config))
        animation_segment = self.smooth.calulate_trace(angle[0], angle[1], time, set_config[0], set_config[1], set_config[2], set_config[3])
        return animation_segment
    
    def generate_smooth_animation_list(self, animation_lists: list[list[list]]) -> list[list[list]]:
        animation_segment_lists = []
        for animation_list in animation_lists:
            animation_segment_list = []
            time = animation_list[-2]
            config = animation_list[-1]
            for animation in animation_list[:-2]:
                animations = self.genarate_smooth_animation_one([animation[1], animation[2]], time, config)
                if animation[0] < 0 or animation[0] > 15:
                    raise ValueError("舵机标号必须在0~15之间！")
                animations.insert(0,animation[0])
                animation_segment_list.append(animations)
            animation_segment_lists.append(animation_segment_list)
        return animation_segment_lists
    
            
            


            
