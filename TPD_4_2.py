import numpy as np
from scipy.stats import gamma, norm
from scipy.integrate import quad


# 1. 计算在一个路段上车辆 Va 和 Vb 相遇的概率。它使用Gamma分布的概率密度函数 (PDF) 来进行积分计算。  t1_2 和 t2_1 是链接旅行延迟的期望值。
# 1. Computes the probability that vehicles Va and Vb meet on a road segment. It uses the probability density function (PDF) of the Gamma distribution for the integral calculation. t1_2 and t2_1 are the expected values ​​of the link travel delays.
def encounter_probability_segment(mean_a, variance_a, mean_b, variance_b, t1_2, t2_1):
    """
    Calculate the probability of meeting on a road segment.
    :param mean_a: mean of vehicle Va
    :param variance_a: variance of vehicle Va
    :param mean_b: mean of vehicle Vb
    :param variance_b: variance of vehicle Vb
    :param t1_2: expected link travel delay for L1,2
    :param t2_1: expected link travel delay for L2,1
    :return: meeting probability
    """

    # 计算 Gamma 分布的形状和尺度参数
    shape_a = (mean_a ** 2) / variance_a
    scale_a = variance_a / mean_a

    shape_b = (mean_b ** 2) / variance_b
    scale_b = variance_b / mean_b

    # 定义Gamma分布的PDF。 Defining the PDF of the Gamma distribution
    def f(x):  # 车辆Va到达某个位置的 Gamma 分布 PDF。 Gamma distribution PDF of vehicle Va arriving at a certain location.
        return gamma.pdf(x, a=shape_a, scale=scale_a)

    def g(y):  # 车辆Vb到达某个位置的 Gamma 分布 PDF。   Gamma distribution PDF of vehicle Vb arriving at a certain location.
        return gamma.pdf(y, a=shape_b, scale=scale_b)

    # 计算相遇概率
    prob = 0 # 用于累计相遇概率
    total_integral = 0  # 总积分
    for x in np.arange(0, 100, 0.01):  # x的积分范围是：0~100秒，也就是说从0秒时刻到第100秒时刻Va都有可能到达点1。积分步长是0.01
        prob += quad(lambda y: f(x) * g(y), x, x + t1_2 + t2_1)[0] #计算二重积分， 对于每一个 x，通过 quad 函数计算 f(x)和g(x)的乘积在区间[x, x + t1_2 + t2_1]上的积分，这样就得到了在此区间内Va和Vb同时到达的概率
        # quad 是 SciPy 库中的一个数值积分函数，它返回的第一个元素是积分的结果，因此通过 [0] 取出结果并加到 prob 上。 返回值是(积分的结果, 估计的误差)
        # quad is a numerical integration function in the SciPy library. The first element it returns is the result of the integration, so the result is taken out through [0] and added to prob. The return value is (the result of the integration, the estimated error)
        total_integral += 1  # 记录积分次数

    # 归一化 Normalization
    prob /= total_integral  # 除以积分次数  Divide by the number of integrations

    return prob


# 示例数据
mean_a = 10  # 车辆 Va从其他点 到点1的延迟均值(期望）， 其他点可能是固定的点， 也可能是不同的点。The mean (expected) delay of vehicle Va from other points to point 1. Other points may be fixed points or different points.
variance_a = 2  # 车辆 Va从其他点 到点1的延迟方差。 The delay variance of vehicle Va from other points to point 1
mean_b = 15  # 车辆Vb从点2到点1的延迟均值(期望)。 Mean (expected) delay of vehicle Vb from point 2 to point 1
variance_b = 3  # 车辆Vb从点2到点1的延迟方差。 The delay variance of vehicle Vb from point 2 to point 1

t1_2 = 5  # n1 ~ n2路段的延迟期望(相对于所有车辆计算的) Expected delay of segment n1 to n2 (calculated relative to all vehicles)
t2_1 = 6  # n2 ~ n1路段的延迟期望 Expected delay of the n2 ~ n1 segment

# 计算相遇概率
prob_segment = encounter_probability_segment(mean_a, variance_a, mean_b, variance_b, t1_2, t2_1)
print(f"Probability of meeting on a road segment: {prob_segment}")


# 2. 计算算车辆 Va 和 Vb 在交叉口的相遇概率。它考虑了两种情况： Calculate the probability of vehicles Va and Vb meeting at the intersection. It considers two cases:
# 情况1：Va 早于 Vb 到达交叉口。    情况2：Vb 早于 Va 到达交叉口。      该函数同样使用 Gamma 分布的 PDF 来进行积分计算。
# Case 1: Va reaches the intersection earlier than Vb. Case 2: Vb reaches the intersection earlier than Va. This function also uses the PDF of the Gamma distribution for integral calculation.
def encounter_probability_intersection(mean_a, variance_a, mean_b, variance_b, ti_5, R, Sb):
    """
    Calculate the probability of encounter at an intersection.
    :param mean_a: mean of vehicle Va
    :param variance_a: variance of vehicle Va
    :param mean_b: mean of vehicle Vb
    :param variance_b: variance of vehicle Vb
    :param ti_5: link travel delay at the intersection
    :param R: communication range
    :Sb: expected speed of Vb
    :return: encounter probability
    """

    def f(x):
        return gamma.pdf(x, a=mean_a ** 2 / variance_a, scale=variance_a / mean_a)

    def g(y):
        return gamma.pdf(y, a=mean_b ** 2 / variance_b, scale=variance_b / mean_b)

    # 计算相遇概率 Case 1
    #外层积分：quad(lambda x: ..., 0, np.inf) 表示对 x 从 0 到正无穷进行积分。
    #内层积分：表示对 y 从 x + ti_5 到 x + ti_5 + R/Sb 进行积分，f(x) 和 g(y) 是两个函数，分别与 x 和 y 有关。
    prob_case_1 = quad(lambda x: quad(lambda y: f(x) * g(y), x + ti_5, x + ti_5 + R/Sb)[0], 0, 100)[0] #100

    # 计算相遇概率 Case 2
    prob_case_2 = quad(lambda x: quad(lambda y: f(x) * g(y), x + ti_5 - R/Sb, x + ti_5)[0], 0, 100)[0]

    # 总相遇概率
    total_prob = prob_case_1 + prob_case_2
    return total_prob


# 示例数据
mean_a_intersection = 10  # 车辆Va的均值   The mean value of vehicle Va
variance_a_intersection = 2  # 车辆Va的方差  The variance of vehicle Va
mean_b_intersection = 15  # 车辆Vb的均值   The mean value of vehicle Vb
variance_b_intersection = 3  # 车辆Vb的方差  The variance of vehicle Vb
ti_5 = 5  # 交叉口的链接旅行延迟。（Va从点i到点5的时间间隔） Link travel delay at the intersection. (The time interval between Va from point i to point 5)
R = 10  # 通信范围   Communication range
Sb = 0.5 #Vb的预期速度  Expected speed of Vb

# 计算交叉口的相遇概率
prob_intersection = encounter_probability_intersection(mean_a_intersection, variance_a_intersection,
                                                       mean_b_intersection, variance_b_intersection,
                                                       ti_5, R, Sb)
print(f"Meeting probability at intersection: {prob_intersection}")
