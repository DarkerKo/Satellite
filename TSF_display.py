import numpy as np
import networkx as nx
from scipy.stats import gamma
import itertools
import matplotlib.pyplot as plt  # 导入绘图库


# 定义Car类
class Car:
    def __init__(self, speed, communication_range):
        self.speed = speed  # 单位：米/秒
        self.communication_range = communication_range  # 单位：米


# 创建城市地图类
class CityMap:
    def __init__(self):
        self.graph = nx.Graph()  # 创建一个空的无向图对象，后续将添加节点和边。

    def add_edge(self, node1, node2, length, arrival_rate, average_travel_time, var):
        # 在图中添加边，带有长度和车辆到达率λ属性
        self.graph.add_edge(node1, node2, length=length, arrival_rate=arrival_rate, Average_travel_time=average_travel_time, Var=var)

    def get_edges(self):
        return self.graph.edges(data=True)  # 返回图中所有边及其相关数据

    def get_nodes(self):
        return self.graph.nodes()  # 返回图中所有节点

    def plot_graph(self):
        pos = nx.spring_layout(self.graph)  # 使用spring布局算法为图生成布局
        labels = nx.get_edge_attributes(self.graph, 'length')  # 获取每条边的长度信息

        # 绘制图形
        nx.draw(self.graph, pos, with_labels=True, node_size=700, node_color='skyblue', font_size=10,
                font_weight='bold')
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=labels)  # 绘制边的长度标签

        plt.title("City Map")
        plt.show()  # 显示图形


# 计算链路延迟的Gamma分布参数
def compute_link_packet_delay(car, length, arrival_rate):
    v = car.speed
    R = car.communication_range
    l = length  # 提取 本链路的长度
    λ = arrival_rate  # 提取 本链路的车辆到达率

    E_lf = l / 2

    # 计算两种情况的 发生概率
    β = 1 - np.exp(-λ * R / v)  # 情况1：立即转发的概率β

    # 计算两种情况的 链路延迟的期望和方差
    E_d_forward = (l - E_lf - R) / v  # 情况1： 立即转发的链路延迟期望
    E_d_wait = (1 / λ) + (l - R) / v  # 情况2： 等待与携带的链路延迟期望

    # 链路延迟的总体期望
    E_d = E_d_forward * β + E_d_wait * (1 - β)

    # 链路延迟的总体方差
    Elf2 = E_lf ** 2 / 3
    Ed2_forward = ((l - R) ** 2 - 2 * (l - R) * E_lf + Elf2) / v ** 2
    Ed2_wait = ((1 / λ) + (l - R)) ** 2

    Ed2 = Ed2_forward * β + Ed2_wait * (1 - β)

    Var_d = Ed2 + E_d ** 2

    # # 计算Gamma分布的参数θ和κ
    # if Var_d > 0:
    #     θ = Var_d / E_d
    #     κ = E_d / θ
    # else:
    #     κ = E_d
    #     θ = 1.0

    return E_d, Var_d  # 返回该链路延迟的期望和方差（结合了两种情况）

def compute_path_travel_delay(city_map, car, path):
    total_Exp = 0
    total_Var = 0
    for i in range(len(path) - 1):
        node1 = path[i]
        node2 = path[i + 1]
        edge_data = city_map.graph.get_edge_data(node1, node2)
        exp = edge_data['Average_travel_time']
        var = edge_data['Var']

        total_Exp += exp
        total_Var += var
    return total_Exp, total_Var


# 计算路径的Gamma分布参数
def compute_path_packet_delay(city_map, car, path):
    total_Exp = 0
    total_Var = 0
    for i in range(len(path) - 1):
        node1 = path[i]
        node2 = path[i + 1]
        edge_data = city_map.graph.get_edge_data(node1, node2)
        length = edge_data['length']
        arrival_rate = edge_data['arrival_rate']

        temp_Exp, temp_Var = compute_link_packet_delay(car, length, arrival_rate)
        total_Exp += temp_Exp
        total_Var += temp_Var
    return total_Exp, total_Var


# 计算在给定时间内成功传输的概率
def calculate_success_probability(kappa, theta, time_limit):
    return gamma.cdf(time_limit, a=kappa, scale=theta)


# 主函数：模拟并找到最优路径
def find_optimal_path(city_map, car, source, destination):
    # 这是使用NetworkX库中的all_simple_paths函数，该函数用于在给定的图（city_map.graph）中找到从source节点到destination节点的所有简单路径。简单路径是指路径中没有重复节点。
    # itertools.islice是Python的itertools库中的一个函数，用于对可迭代对象（如生成器）进行切片操作。这里它的作用是从nx.all_simple_paths的生成器中，最多获取前100条路径。
    all_paths = list(itertools.islice(nx.all_simple_paths(city_map.graph, source=source, target=destination), 100))
    # print(all_paths)
    path_probabilities = {}

    for path in all_paths:
        Exp_packet_delat, Var_packet_delat = compute_path_packet_delay(city_map, car, path)
        packet_delat_kappa = Exp_packet_delat ** 2 / Var_packet_delat
        packet_delat_theta = Var_packet_delat / Exp_packet_delat

        Exp_travel_delat, Var_travel_delat = compute_path_travel_delay(city_map, car, path)
        # travel_delat_kappa = Exp_travel_delat ** 2 / Var_travel_delat
        # travel_delat_theta =  Var_travel_delat / Exp_travel_delat

        success_prob = calculate_success_probability(packet_delat_kappa, packet_delat_theta, Exp_travel_delat)
        path_probabilities[tuple(path)] = success_prob
        print(f"Path: {path},  The predicted probability that the data packet arrives at the destination before the vehicle is: {success_prob:.4f}")

    optimal_path = max(path_probabilities, key=path_probabilities.get)
    print(f"\nOptimal Path: {optimal_path} with probability {path_probabilities[optimal_path]:.4f}")
    return optimal_path





# 示例数据构建城市地图
def build_city_map():
    city_map = CityMap()
    nodes = range(1, 7)
    city_map.graph.add_nodes_from(nodes)

    city_map.add_edge(1, 2, length=500, arrival_rate=0.05, average_travel_time=22.5, var=3)# 80Km/h
    city_map.add_edge(2, 3, length=300, arrival_rate=0.08, average_travel_time=21.4, var=2)# 50km/h
    city_map.add_edge(3, 4, length=400, arrival_rate=0.06, average_travel_time=19.2, var=3) # 75Km/h
    city_map.add_edge(4, 5, length=600, arrival_rate=0.04, average_travel_time=27, var=3) # 80Km/h
    city_map.add_edge(5, 6, length=350, arrival_rate=0.07, average_travel_time=31.5, var=3) # 40Km/h
    city_map.add_edge(1, 3, length=800, arrival_rate=0.03, average_travel_time=48, var=3) # 60Km/h
    city_map.add_edge(2, 4, length=700, arrival_rate=0.02, average_travel_time=50.4, var=3) # 50Km/h
    city_map.add_edge(3, 5, length=500, arrival_rate=0.05, average_travel_time=30, var=3) # 60Km/h
    city_map.add_edge(4, 6, length=450, arrival_rate=0.06, average_travel_time=27, var=3) # 60Km/h

    return city_map


# 主程序
if __name__ == "__main__":
    city_map = build_city_map()
    car = Car(speed=15, communication_range=100)
    source_node = 1
    destination_node = 6
    pro_threshold = 0.8 # # 给定的时间限制，单位：秒

    # 显示地图
    city_map.plot_graph()
    print("The predicted probability threshold for a packet to arrive at its destination before the vehicle does is:", pro_threshold)
    # 寻找延迟最优路径
    optimal_path = find_optimal_path(city_map, car, source_node, destination_node)
