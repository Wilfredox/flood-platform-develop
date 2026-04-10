import numpy as np
from scipy.optimize import differential_evolution

def get_muskingum_coeffs(K, x, dt):
    """计算单段马斯京根系数 C0, C1, C2"""
    denom = K - K * x + 0.5 * dt
    c0 = (-K * x + 0.5 * dt) / denom
    c1 = (K * x + 0.5 * dt) / denom
    c2 = (K - K * x - 0.5 * dt) / denom
    return c0, c1, c2

def route_segmented_muskingum(I, params, dt):
    """
    执行分段马斯京根演进计算
    :param I: 上游入流序列 (numpy array)
    :param params: [K1, K2, K3, x1, x2, x3] 对应 低、中、高水位的参数
    :param dt: 计算步长 (应与 K 单位一致)
    """
    K1, K2, K3, x1, x2, x3 = params
    
    # 按 33% 和 66% 分位数划分高中低流量段
    p33 = np.percentile(I, 33.33)
    p66 = np.percentile(I, 66.67)

    n = len(I)
    O = np.zeros(n)
    O[0] = I[0]  # 假定初始时刻出流等于入流

    for t in range(n - 1):
        # 根据当前流量判断属于哪一段
        q_current = I[t]
        if q_current <= p33:
            K, x = K1, x1
        elif q_current <= p66:
            K, x = K2, x2
        else:
            K, x = K3, x3

        # 计算系数并演进
        c0, c1, c2 = get_muskingum_coeffs(K, x, dt)
        O[t+1] = c0 * I[t+1] + c1 * I[t] + c2 * O[t]

    return O

def simulate_system(qa, qb, params_vector, dt):
    """
    模拟整个系统的下游流量 (A + B + baseflow + bias)
    :param params_vector: 长度为 14 的参数向量
    """
    # 解析 14 个参数
    params_a = params_vector[0:6]   # A 站的 [K1, K2, K3, x1, x2, x3]
    params_b = params_vector[6:12]  # B 站的 [K1, K2, K3, x1, x2, x3]
    baseflow = params_vector[12]    # 基流
    bias = params_vector[13]        # 线性偏置系数

    # 分别演进两支流
    out_a = route_segmented_muskingum(qa, params_a, dt)
    out_b = route_segmented_muskingum(qb, params_b, dt)

    # 叠加计算，加入随时间变化的偏置项
    n = len(qa)
    t_arr = np.arange(n)
    q_sim = out_a + out_b + baseflow + bias * (t_arr / max(1, n - 1))
    
    return q_sim

def calc_nse(obs, sim):
    """计算纳什效率系数 (NSE)"""
    numerator = np.sum((obs - sim) ** 2)
    denominator = np.sum((obs - np.mean(obs)) ** 2)
    if denominator == 0:
        return 0
    return 1 - (numerator / denominator)

def objective_function(params_vector, qa, qb, qc, dt):
    """DE 算法的目标函数：最小化 1 - NSE"""
    q_sim = simulate_system(qa, qb, params_vector, dt)
    
    # 惩罚项：防止产生负流量或数值发散
    if np.any(q_sim < 0) or np.any(np.isnan(q_sim)):
        return 1e6

    nse_val = calc_nse(qc, q_sim)
    return 1 - nse_val  # DE 算法寻找最小值，因此返回 1 - NSE

def calibrate(qa, qb, qc, dt):
    """执行差分进化算法率定参数"""
    print("开始执行差分进化(DE)参数率定...")
    
    # 定义 14 个参数的搜索边界 (Bounds)
    # 结构: A(K1,K2,K3,x1,x2,x3), B(K1,K2,K3,x1,x2,x3), baseflow, bias
    # 注意：这里的界限(0.1 ~ 150 等)需根据你的流域实际传播时间调整
    bounds = [
        (0.1, 150), (0.1, 150), (0.1, 150), # A的 K1, K2, K3
        (0.0, 0.5), (0.0, 0.5), (0.0, 0.5), # A的 x1, x2, x3
        (0.1, 150), (0.1, 150), (0.1, 150), # B的 K1, K2, K3
        (0.0, 0.5), (0.0, 0.5), (0.0, 0.5), # B的 x1, x2, x3
        (0.0, 500),                         # baseflow 基流
        (-500, 500)                         # bias 线性偏差
    ]

    # 调用 scipy 的差分进化算法
    result = differential_evolution(
        objective_function, 
        bounds, 
        args=(qa, qb, qc, dt),
        strategy='best1bin',
        maxiter=100,      # 相当于 JS 代码中的 generations
        popsize=15,       # 种群规模 (相对 bounds 数量)
        tol=0.01,
        mutation=(0.5, 1),
        recombination=0.7,
        disp=True         # 打印每代进度
    )

    best_params = result.x
    best_nse = 1 - result.fun
    
    print(f"\n率定完成! 最佳 NSE: {best_nse:.4f}")
    return best_params, best_nse

# ==========================================
# 测试与使用示例
# ==========================================
if __name__ == "__main__":
    # 1. 模拟生成一些伪数据（真实使用时请用 pandas 读取 Excel）
    np.random.seed(42)
    time_steps = 100
    dt_minutes = 60  # 步长 60 分钟 (1小时)
    
    q_a = np.sin(np.linspace(0, 3.14, time_steps)) * 100 + 20
    q_b = np.sin(np.linspace(0, 3.14, time_steps) - 0.5) * 80 + 10
    
    # 假设下游测站 C 的真实流量是 A 和 B 的某种延迟叠加
    q_c_obs = np.roll(q_a, 2) * 0.9 + np.roll(q_b, 3) * 0.85 + 15
    q_c_obs[0:3] = q_c_obs[3] # 修复平移造成的端点

    # 2. 运行率定
    best_p, final_nse = calibrate(q_a, qb=q_b, qc=q_c_obs, dt=dt_minutes)

    # 3. 使用率定好的参数进行预报演算
    q_simulated = simulate_system(q_a, q_b, best_p, dt_minutes)

    # 打印前 5 个时刻的比对结果
    print("\n预报计算验证 (前 5 个时刻):")
    print("实测值(Qc):", np.round(q_c_obs[:5], 2))
    print("模拟值(Sim):", np.round(q_simulated[:5], 2))