import heapq
from collections import defaultdict


# 定义车辆节点。   Define vehicle node
class VehicleNode:
    def __init__(self, vehicle_id, expected_encounter_time):
        self.vehicle_id = vehicle_id
        self.expected_encounter_time = expected_encounter_time
        self.children = []  # Record child nodes

    def __lt__(self, other):
        # 比较相遇时间，用于优先队列排序。     Compare encounter times for priority queue sorting
        return self.expected_encounter_time < other.expected_encounter_time


# 构建图的类
class PredictedEncounterGraph:
    def __init__(self, threshold=0.6, ttl=10.0):
        self.threshold = threshold  # 相遇概率阈值   Encounter probability threshold
        self.ttl = ttl
        self.graph = {}  # 存储节点信息    Storage node information
        self.bitmap = defaultdict(int)  # 位图标记车辆是否被访问(创建了一个 默认字典，其默认值是整数 0)。  Bitmap marks whether the vehicle has been visited

    def add_node(self, parent_id, vehicle_id, expected_encounter_time):
        if vehicle_id not in self.graph:
            self.graph[vehicle_id] = VehicleNode(vehicle_id, expected_encounter_time)

        #向自己的子节点列表中加入子节点。   Add a child node to its own child node list
        if parent_id is not None:
            self.graph[parent_id].children.append(self.graph[vehicle_id]) # 将新节点添加到父节点的子节点列表中。  Add the new node to the parent node's list of children

    def predict_encounter(self, source_vehicle, destination_vehicle, vehicles, encounter_times, encounter_probs):
        # 使用最小优先队列（堆）实现扩展   Scaling with minimum priority queue (heap)
        queue = []
        heapq.heappush(queue, (0, source_vehicle))  # 插入源车辆作为根节点。    Insert the source vehicle as the root node
        self.bitmap[source_vehicle] = 1  # 标记源车辆已访问。    Mark source vehicle visited

        # 构建图
        while queue:
            # 弹出优先队列中的节点，队列中时间最小的节点会被优先扩展。 Pop the node in the priority queue, the node with the shortest time in the queue will be expanded first
            current_time, current_vehicle = heapq.heappop(queue) # 数字， 车名
            # print("current_time:", current_time, "current_vehicle:", current_vehicle) # 0, a

            # 如果已经到达目标车辆，结束扩展。 If the target vehicle has been reached, end the expansion
            if current_vehicle == destination_vehicle:
                break

            # 遍历当前车辆的相遇时间。 Traverse the encounter time of the current vehicle
            for next_vehicle, encounter_time in encounter_times[current_vehicle]: # encounter_times通过车名键访问到 对应值
                #如果车没有被标记， 而且这两辆车相遇的概率大于 阈值。 If the car is not marked, and the probability of the two cars meeting is greater than the threshold
                if self.bitmap[next_vehicle] == 0 and encounter_probs[(current_vehicle, next_vehicle)] >= self.threshold:
                    #相遇时间必须小于TTL。 The encounter time must be less than TTL
                    if encounter_time <= self.ttl:
                        # 插入子节点到优先队列。 Insert child nodes into the priority queue
                        heapq.heappush(queue, (encounter_time, next_vehicle))

                        self.add_node(current_vehicle, next_vehicle, encounter_time)
                        self.bitmap[next_vehicle] = 1  # 标记该车辆已访问。 Mark the vehicle visited

        return self.graph


# 模拟车辆网络和相遇信息。 Simulating vehicle networks and encounter information
def simulate_encounter_graph():
    # 初始化车辆、相遇时间、相遇概率等信息。 Initialize vehicle, encounter time, encounter probability and other information
    vehicles = ['a', 'b', 'c', 'd', 's']
    encounter_times = {
        'a': [('b', 3), ('d', 5)],
        'b': [('c', 6)],
        'c': [('s', 8)],
        'd': [('s', 7)]
    }
    encounter_probs = {
        ('a', 'b'): 0.7, ('a', 'd'): 0.8,
        ('b', 'c'): 0.6, ('c', 's'): 0.9,
        ('d', 's'): 0.85
    }
    source_vehicle = 'a'
    destination_vehicle = 's'

    # 创建预测相遇图。 Creating a Predicted Encounter Graph
    peg = PredictedEncounterGraph(threshold=0.6, ttl=10.0)
    peg.graph['a'] = VehicleNode(source_vehicle, 0)
    graph = peg.predict_encounter(source_vehicle, destination_vehicle, vehicles, encounter_times, encounter_probs)


    # 输出图结构。 Output graph structure
    for vehicle_id, node in graph.items():
        for child in node.children:
            print(f"Vehicle {vehicle_id} will encounter vehicles: {child.vehicle_id} at time {child.expected_encounter_time}")


# 运行模拟。 Run the simulation
simulate_encounter_graph()
