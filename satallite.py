import numpy as np
import random
import math
import time
# 顺行轨道（与地球自转同方向）： 假设一颗 LEO 卫星的速度为 7.8 公里/秒，而地面在赤道的自转速度为 0.465 公里/秒，那么顺行轨道上卫星相对于地面的速度约为 7.8 公里/秒 - 0.465 公里/秒 = 7.335 公里/秒。
# 逆行轨道（与地球自转方向相反）：举例：如果卫星的速度为 7.8 公里/秒，地面自转速度为 0.465 公里/秒，那么逆行轨道上卫星相对于地面的速度约为 7.8 公里/秒 + 0.465 公里/秒 = 8.265 公里/秒。
# 这里是顺行轨道，不过用的是卫星相对于地面的速度。所以没关系
# 这里只有一个轨道高度， 2000Km,所以卫星旋转的角速度和对地覆盖半径都是固定的

# Prograde orbit (same direction as the Earth's rotation): Assuming a LEO satellite's speed is 7.8 km/s, and the Earth's rotation speed at the equator is 0.465 km/s, then the satellite's speed relative to the Earth in the prograde orbit is about 7.8 km/s - 0.465 km/s = 7.335 km/s.
# Retrograde orbit (opposite to the Earth's rotation): For example: If the satellite's speed is 7.8 km/s and the Earth's rotation speed is 0.465 km/s, then the satellite's speed relative to the Earth in the retrograde orbit is about 7.8 km/s + 0.465 km/s = 8.265 km/s.
# This is a prograde orbit, but the speed of the satellite relative to the Earth is used. So it doesn't matter
# There is only one orbital altitude here, 2000Km, so the angular velocity of the satellite's rotation and the radius of coverage of the Earth are fixed

EARTH_PERIMETER = 40075
EARTH_RADIUS = 6360

G = 6.674 * 10**-11  # 万有引力常数 (m^3 kg^-1 s^-2)， gravitational constant
M = 5.972 * 10**24   # 地球的质量 (kg)，   Mass of the Earth (kg)


# 节点类(卫星类的父类)
class Node:
    def __init__(self, name, position):
        self.name = name
        self.position = np.array(position) #地面基站的位置， 或者卫星相对于地面的投影的圆心位置， The location of the ground base station, or the center of the satellite's projection relative to the ground


# 定义卫星类，继承自节点
class Satellite(Node):
    def __init__(self, name, position, speed, orbit_height, communication_radius, theta):
        super().__init__(name, position)
        self.speed = speed  # 卫星速度，单位为公里/0.01S. (这里是地面覆盖距离的变化速度)
        self.orbitHeight = orbit_height
        self.communication_radius = communication_radius  # 卫星间通讯范围
        self.theta = theta  # 目前卫星所在的旋转角度（弧度制）

        #根据轨道高度计算对地覆盖半径
        self.coverage_radius = EARTH_RADIUS * math.acos(EARTH_RADIUS / (EARTH_RADIUS + orbit_height))
        # print("卫星对地覆盖半径是：", self.coverage_radius) # 4492.0965573546355

        #根据轨道高度计算卫星的角速度
        orbital_radius = (EARTH_RADIUS + orbit_height) * 10 ** 3  # 转换为米
        self.angular_velocity = math.sqrt(G * M / orbital_radius ** 3) # 角速度 (弧度/秒)
        # print("角速度是：", self.angular_velocity) # 0.0008259306530384688 rad


    def can_communicate(self, other):
        """检查卫星之间是否能通信(使用的坐标系时以地球为圆心， 以卫星轨道为半径的圆)"""
        # 计算两个卫星的坐标
        x1 = (other.orbitHeight + EARTH_RADIUS) * math.cos(other.theta)
        y1 = (other.orbitHeight + EARTH_RADIUS) * math.sin(other.theta)

        x2 = (self.orbitHeight + EARTH_RADIUS) * math.cos(self.theta)
        y2 = (self.orbitHeight + EARTH_RADIUS) * math.sin(self.theta)

        # 计算两个卫星的直线距离
        distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        return distance <= self.communication_radius

    def is_covering(self, groundStation):
        """检查卫星是否覆盖了某个地面节点"""
        #计算卫星和基站的地面距离
        # print("The satellite's position is:", self.position[0], self.position[1], "， The ground base station locations are:", groundStation.position[0], groundStation.position[1])

        if self.position[0] - groundStation.position[0] > EARTH_PERIMETER / 2:
            distance = math.sqrt((EARTH_PERIMETER - (self.position[0] - groundStation.position[0]) - groundStation.position[0]) ** 2  + (self.position[1] - groundStation.position[1]) ** 2)
        else:
            distance = math.sqrt((self.position[0] - groundStation.position[0]) ** 2 + (self.position[1] - groundStation.position[1]) ** 2)
        print(f"The distance between {self.name} and the ground base station is: {distance}") # 4527.69,  9013.87, …………
        return distance <= self.coverage_radius

    def move(self, timeUnit): #单位时间是0.01S
        """模拟卫星按速度移动"""
        #更新卫星所处圆心的位置(假设Y轴不变，也就是维度不变， 只更新x轴的位置)
        self.position[0] = (self.position[0] + self.speed * timeUnit) % EARTH_PERIMETER # 简化模型，只在x轴上移动

        #更新卫星的所处角度
        self.theta = (self.theta + self.angular_velocity * timeUnit) % (2 * math.pi)




# 定义数据包类
class Packet:
    def __init__(self, size):
        self.size = size  # 数据包大小，单位为MB


# 查找当前覆盖到起始基站的卫星
def find_covering_satellite(station, satellites):
    for satellite in satellites:
        if satellite.is_covering(station):
            return satellite
    return None


# 查找能与目标基站通讯的卫星
def find_closest_covering_satellite(target_station, satellites):
    covering_satellites = [sat for sat in satellites if sat.is_covering(target_station)]
    if covering_satellites:
        return covering_satellites[0]  # 简化：假设找到的第一个卫星为最近的
    return None


# 模拟数据传输过程
def simulate_data_transfer(ground_station, satellites, target_station, packet_size):
    print("Start detecting satellites.......\n")
    packet = Packet(packet_size)
    print(f"Packet size: {packet.size} MB， Send from: {ground_station.name}\n")

    #--------------------------------------------检查有无覆盖卫星-------------------------------------------
    covering_satellite = find_covering_satellite(ground_station, satellites) #找的的话返回卫星类对象， 没有找到返回None
    # 如果没有
    if not covering_satellite:
        print(f"There is currently no satellite coverage {ground_station.name}, waiting for satellite coverage...")

        while not covering_satellite:
            time.sleep(0.01)  # 模拟时间流逝， 每0.01S检查一次
            #卫星移动
            for satellite in satellites:
                satellite.move(10)  # 卫星每小时移动
            #再次检查有无覆盖卫星
            covering_satellite = find_covering_satellite(ground_station, satellites)

        print(f"{covering_satellite.name} now covers {ground_station.name},  and starts sending data packets")
    print(f"\nThe covered satellite is found. The satellite name is: {covering_satellite.name}\n")
    # --------------------------------------------卫星间转发数据包--------------------------------------------
    for i in range(len(satellites) - 1): # 只是检查了卫星列表中 相连的两颗卫星是否可以通讯
        current_satellite = satellites[i]
        next_satellite = satellites[i + 1]

        # 移动卫星并预测转发时间后的卫星位置
        time_hours = 0.1  # 假设转发时间为0.1小时
        for sat in satellites:
            sat.move(time_hours)

        if current_satellite.can_communicate(next_satellite):
            print(f"{current_satellite.name} -> {next_satellite.name} Successfully forwarded packet")
        else:
            print(f"{current_satellite.name} -> {next_satellite.name} Forwarding failed, distance is too far")
            return

    # 预测最终的卫星是否覆盖目标基站
    final_satellite = satellites[-1]
    print(f"预测 {final_satellite.name} 将覆盖目标基站 {target_station.name}")

    if final_satellite.is_covering(target_station):
        print(f"{final_satellite.name} 已覆盖到 {target_station.name}，成功发送数据包")
    else:
        print(f"{final_satellite.name} 尚未覆盖 {target_station.name}，等待卫星移动...")
        # 等待此为姓覆盖到 目标基站
        while not final_satellite.is_covering(target_station):
            time.sleep(1)
            final_satellite.move(0.1)
        print(f"{final_satellite.name} 现在覆盖到了 {target_station.name}，成功发送数据包")


# 定义节点
ground_station = Node("StartGroundStation", [0, 0])
print("The location of the ground station is:", ground_station.position[0], ",", ground_station.position[1])

target_station = Node("TargetGroundStation", [1000, 0]) #Km
print("The location of the target station is:", target_station.position[0], ",",  target_station.position[1])
print(f"The satellite's orbital altitude is:2000, so the angular velocity is:0.000825 rad, The satellite coverage radius of the earth is:{EARTH_RADIUS * math.acos(EARTH_RADIUS / (EARTH_RADIUS + 2000))}\n")


satellites = [Satellite(f"Satellite{i}", [i * 4500, 500], speed=0.07, orbit_height=2000, communication_radius=1500, theta=(2 * math.pi / 30) * i) for i in range(1, 10)] # 9颗卫星，每颗卫星 每0.01S移动70m，轨道高度2000Km，自身通信半径为1500Km,覆盖地面信号范围半径是2000km
for satellite in satellites:
    print(f"{satellite.name},  Satellite's starting position: {satellite.position}") #






# 模拟数据传输
simulate_data_transfer(ground_station, satellites, target_station, packet_size=10)

# 更新卫星位置（每小时移动一次）
time_hours = 1
for satellite in satellites:
    satellite.move(time_hours)
    print(f"{satellite.name} 新位置: {satellite.position}")
