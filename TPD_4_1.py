import numpy as np
from scipy.stats import gamma

def calculate_gamma_params(mean, variance):
    """
    Compute the parameters of the Gamma distribution.
    :param mean: mean
    :param variance: variance
    :return: shape parameter (kappa) and scale parameter (theta)
    """
    theta = variance / mean
    kappa = mean / theta
    return kappa, theta

def travel_time_on_segment(mean, variance):
    """
    Calculate the travel time for a single road segment.
    :param mean: mean of the road segment travel time
    :param variance: variance of the road segment travel time
    :return: Returns the parameters of the Gamma distribution
    """
    kappa, theta = calculate_gamma_params(mean, variance)
    return kappa, theta

def end_to_end_travel_time(segment_means, segment_variances):
    """
    Calculate the travel time of the end-to-end path.
    :param segment_means: list of means for each segment
    :param segment_variances: list of variances for each segment
    :return: Gamma distribution parameters for E2E travel time
    """
    total_mean = sum(segment_means)
    total_variance = sum(segment_variances)
    kappa, theta = calculate_gamma_params(total_mean, total_variance)
    return kappa, theta

def arrival_time_prediction(current_time, e2e_travel_delay):
    """
    Calculate the arrival time of the vehicle at the target intersection.
    :param current_time: current time
    :param e2e_travel_delay: end-to-end travel delay
    :return: arrival time
    """
    return current_time + e2e_travel_delay

# Sample data (the mean and variance of each road section are provided by the service provider)
segment_means = [10, 15, 20]  # The average value of each road segment
segment_variances = [2, 3, 5]  # The variance of each road segment
current_time = 5

# Calculate the Gamma parameter for each road segment
segment_params = [travel_time_on_segment(mean, variance) for mean, variance in zip(segment_means, segment_variances)]
print("Gamma distribution parameters (kappa, theta) for each road segment:", segment_params)

# Calculate the Gamma parameter for end-to-end travel time
e2e_params = end_to_end_travel_time(segment_means, segment_variances)
print("Gamma distribution parameters (kappa, theta) for end-to-end travel time:", e2e_params)

# Calculate arrival time prediction
e2e_travel_delay = gamma.rvs(a=e2e_params[0], scale=e2e_params[1])  # 从Gamma分布中抽样
print("The sampling interval is:", e2e_travel_delay)
arrival_time = arrival_time_prediction(current_time, e2e_travel_delay)
print("The predicted arrival time of the vehicle at the target intersection:", arrival_time)
