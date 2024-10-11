import numpy as np
import random
import math
import time

EARTH_PERIMETER = 40075.0
EARTH_RADIUS = 6360.0

G = 6.674 * 10 ** -11  # 万有引力常数 (m^3 kg^-1 s^-2)
M = 5.972 * 10 ** 24  # 地球的质量 (kg)


# 基站类
class Station:
    def __init__(self, name, lat_lon):
        self.name = name
        self.lat_lon = np.array(lat_lon)  # 地面基站的经纬度


# 定义卫星类
class Satellite():
    def __init__(self, name, speed, orbit_height, communication_radius, theta, inclination, coverage_radius, angular_velocity):
        self.name = name
        self.speed = speed  # 卫星的线速度，单位为Km/s. (这里是地面覆盖距离的变化速度)
        self.orbitHeight = orbit_height # 卫星轨道高度
        self.communication_radius = communication_radius  # 卫星间通讯范围
        self.theta = theta  # 卫星在轨道中的初始角度（弧度制）
        self.inclination = inclination  # 卫星所在轨道的倾角
        self.coverage_radius = coverage_radius  # 对地覆盖信号的半径
        self.angular_velocity = angular_velocity  # 卫星围绕地球旋转的角速度
        self.position_3d = self.compute_3d_position() #卫星的三维位置
        self.lat_lon = self.compute_lat_lon() # 卫星投影到地面的经纬度

    def compute_3d_position(self):
        """计算卫星在三维空间中的位置 (x, y, z)"""
        x = (self.orbitHeight + EARTH_RADIUS) * math.cos(self.theta)
        y = (self.orbitHeight + EARTH_RADIUS) * math.sin(self.theta) * math.cos(self.inclination)
        z = (self.orbitHeight + EARTH_RADIUS) * math.sin(self.inclination)
        return np.array([x, y, z])

    def compute_lat_lon(self):
        """根据卫星的三维位置计算其在地球表面的经纬度投影 (lat, lon)"""
        x, y, z = self.position_3d
        r = np.linalg.norm(self.position_3d)  # 距离地心的距离
        # 纬度 φ (latitude)
        lat = math.degrees(math.asin(z / r))
        # 经度 λ (longitude)
        lon = math.degrees(math.atan2(y, x))

        # 确保经纬度在有效范围内
        if lat > 90:
            lat = 180 - lat
        elif lat < -90:
            lat = -180 - lat

        if lon > 180:
            lon -= 360
        elif lon < -180:
            lon += 360

        return np.array([lat, lon])


    def can_communicate(self, other):
        """检查两个卫星之间是否可以通信 (三维距离)"""
        distance = np.linalg.norm(self.position_3d - other.position_3d)
        return distance <= self.communication_radius * 10 ** 3  # 转换为米

    def is_covering(self, groundStation):
        """检查卫星是否覆盖了某个地面节点"""
        """使用 Haversine 公式计算两个经纬度之间的距离"""
        lat1, lon1 = self.lat_lon
        lat2, lon2 =  groundStation.lat_lon

        # 将角度转换为弧度
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance_to_ground_station =  EARTH_RADIUS * c  # 地球的半径，单位为公里
        return distance_to_ground_station <= self.coverage_radius

    def move(self, timeUnit):  # 单位时间是0.5S, 0.5s检测一次
        # 更新卫星的所处角度
        self.theta = (self.theta + self.angular_velocity * timeUnit) % (2 * math.pi)
        print(f"{self.name}'s new theta is {self.theta}")

        # 更新卫星的三维空间位置
        self.position_3d = self.compute_3d_position()  # 调用 compute_3d_position() 更新三维位置
        print(f"{self.name}'s new 3D position is {self.position_3d}")

        # 更新卫星的经纬度投影
        self.lat_lon = self.compute_lat_lon()  # 调用 compute_lat_lon() 更新经纬度投影
        print(f"{self.name}'s new lat/lon projection is {self.lat_lon}")

# 定义数据包类
class Packet:
    def __init__(self, size):
        self.size = size  # 数据包大小，单位为MB


# 查找当前覆盖到起始基站的卫星
def find_covering_satellite(station, orbits):
    for orbit in orbits: #遍历出轨道
        for satellite in orbit: # 遍历出此轨道的卫星
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
def simulate_data_transfer(start_station, orbits, target_station, packet_size):
    print("开始检测卫星.......\n")
    packet = Packet(packet_size)
    print(f"数据包大小: {packet.size} MB，来自: {start_station.name}\n")

    # --------------------------------------------检查有无覆盖卫星-------------------------------------------
    covering_satellite = find_covering_satellite(start_station, orbits)  # 找到的卫星类对象，没找到返回None
    # 如果没有
    if not covering_satellite:
        print(f"检测完成, 当前没有卫星覆盖 {start_station.name}, 等待卫星覆盖...")

        while not covering_satellite:
            time.sleep(0.5)  # 模拟时间流逝，每0.5S检查一次
            print("开始移动..................")
            # 卫星移动
            for orbit in orbits:  # 遍历输出轨道
                for satellite in orbit:  # 遍历出卫星
                    satellite.move(0.5)  # 更新0.5秒后卫星的位置和角度
            # 再次检查有无覆盖卫星
            covering_satellite = find_covering_satellite(start_station, orbits)

        print(f"{covering_satellite.name} 现在覆盖 {start_station.name}, 开始发送数据包")
    print(f"\n找到覆盖卫星。卫星名称: {covering_satellite.name}\n")
    # --------------------------------------------卫星间转发数据包--------------------------------------------
    for i in range(len(satellites) - 1):  # 只是检查了卫星列表中相连的两颗卫星是否可以通讯
        current_satellite = satellites[i]
        next_satellite = satellites[i + 1]

        # 移动卫星并预测转发时间后的卫星位置
        time_hours = 0.01  # 假设转发时间为0.01小时, 36s
        for orbit in orbits:  # 遍历出轨道
            for satellite in orbit:  # 遍历出卫星
                satellite.move(time_hours)

        if current_satellite.can_communicate(next_satellite):
            print(f"{current_satellite.name} -> {next_satellite.name} 成功转发数据包")
        else:
            print(f"{current_satellite.name} -> {next_satellite.name} 转发失败, 距离过远")
            return

    # -----------------------------------------------预测最终的卫星是否覆盖目标基站--------------------------------
    final_satellite = satellites[-1]
    print(f"预测 {final_satellite.name} 将覆盖目标基站 {target_station.name}")

    if final_satellite.is_covering(target_station):
        print(f"{final_satellite.name} 已覆盖到 {target_station.name}，成功发送数据包")
    else:
        print(f"{final_satellite.name} 尚未覆盖 {target_station.name}，等待卫星移动...")
        # 等待此卫星覆盖到目标基站
        while not final_satellite.is_covering(target_station):
            time.sleep(0.5)
            final_satellite.move(0.5)
        print(f"{final_satellite.name} 现在覆盖到了 {target_station.name}，成功发送数据包")


def create_orbiting_satellites(num_satellites, orbit_heights, speeds, communication_radius, inclinations, coverage_radius, angular_velocities):
    satellites = []
    for i in range(0, len(orbit_heights)): #轨道数量
        temp_orbit = []
        for j in range(num_satellites[i]): #此轨道的卫星数量
            speed = speeds[i]
            theta = (2 * math.pi / num_satellites[i]) * j  # 将卫星均匀分布在轨道上
            temp_orbit.append(Satellite(f"Satellite_{orbit_heights[i]}_{j}", speed, orbit_heights[i], communication_radius, theta, inclinations[i], coverage_radius[i], angular_velocities[i]))
        satellites.append(temp_orbit)
    return satellites #得到一个2维数组， 长度为5， 每个小数组里是每个轨道的卫星


# 示例用法
if __name__ == "__main__":
    # 创建地面基站 (位置用纬度和经度表示)
    start_station = Station("StartStation", [37.7749, -122.4194])  # 示例：旧金山的经纬度
    target_station = Station("TargetStation", [35.0148, 114.4222])  # 目标基站的经纬度

    # 创建卫星
    num_satellites = [18, 10, 16, 20, 15]
    orbit_heights = [2000.0, 2200.0, 2500.0, 2300.0, 2100.0]  # 轨道高度（单位：公里）
    communication_radius = 1000.0  # 卫星之间的通信半径（单位：公里）
    view_angle = 30  # 卫星的视场角（单位：度）
    inclinations = [math.radians(30), math.radians(60), math.radians(90), math.radians(120), math.radians(150)]  # 每个轨道的倾角（单位：弧度）

    #根据轨道高度计算卫星的移动速度(线速度)
    radii_m = [(EARTH_RADIUS + height) * 10 ** 3 for height in orbit_heights]
    speeds = [math.sqrt(G * M / r) / 1000.0 for r in radii_m]  # 各个轨道上卫星的速度（单位：公里/0.01S）
    print("每个轨道的卫星的线速度是：", speeds) # [6.9047802594015995, 6.823640188386309, 6.707120975746278, 6.784128332264759, 6.863850555223682]

    #通过线速度 计算卫星围绕地球旋转的角速度.(也可以通过G和M计算出来)
    radii_km = [EARTH_RADIUS + height for height in orbit_heights]
    angular_velocities = [speed / radius for speed, radius in zip(speeds, radii_km)]
    print("每个轨道的卫星的角速度(弧度/S)是：", angular_velocities) # [0.0008259306530384688, 0.000797154227615223, 0.0007570113968110924, 0.0007833866434485865, 0.0008113298528633194]

    #通过视场角计算卫星覆盖地面信号面积的半径
    theta_rad = math.radians(view_angle)  # 将视场角从度数转换为弧度
    D = [2 * height * math.tan(theta_rad / 2) for height in orbit_heights]  # 覆盖直径，单位：km
    coverage_radius = [d / 2 for d in D]  # 覆盖半径，单位：km
    print("每个轨道的卫星的 覆盖地面信号面积半径是：", coverage_radius) # [535.8983848622454, 589.4882233484699, 669.8729810778067, 616.2831425915822, 562.6933041053577]

    orbits = create_orbiting_satellites(num_satellites, orbit_heights, speeds, communication_radius, inclinations, coverage_radius, angular_velocities)
    print("satellites的形状是：", len(orbits)) # 5

    # 开始模拟数据传输
    simulate_data_transfer(start_station, orbits, target_station, packet_size=50)  # 传输一个大小为50MB的数据包

