import pandas
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize

def portfolio_annualised_performance(weights, mean_returns, cov_matrix):
    returns = np.sum(mean_returns * weights) * 252
    std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)
    return std, returns

def generate_random_portfolios(num_portfolios, mean_returns, cov_matrix, risk_free_rate):
    std_ = []
    return_ = []
    sharpe_ratio = []
    weights_record = []
    for portfolio in range(num_portfolios):
        weights = np.random.random(len(mean_returns))
        weights /= np.sum(weights)
        weights_record.append(weights)
        portfolio_std_dev, portfolio_return = portfolio_annualised_performance(weights, mean_returns, cov_matrix)
        std_.append(portfolio_std_dev)
        return_.append(portfolio_return)
        sharpe_ratio.append((portfolio_return - risk_free_rate) / portfolio_std_dev)
    return std_, return_, sharpe_ratio, weights_record

def portfolio_volatility(weights, mean_returns, cov_matrix):
    return portfolio_annualised_performance(weights, mean_returns, cov_matrix)[0]

def min_variance_portfolio(mean_returns, cov_matrix):
    num_assets = len(mean_returns)
    args = (mean_returns, cov_matrix)
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bound = (0.0,1.0)
    bounds = tuple(bound for _ in range(num_assets))

    result = scipy.optimize.minimize(portfolio_volatility, num_assets*[1./num_assets], args=args,
                        method='SLSQP', bounds=bounds, constraints=constraints)

    return result

def efficient_frontier_volatilities(mean_returns, cov_matrix, target):
    num_assets = len(mean_returns)
    args = (mean_returns, cov_matrix)

    def portfolio_return(weights):
        return portfolio_annualised_performance(weights, mean_returns, cov_matrix)[1]

    constraints = ({'type': 'eq', 'fun': lambda x: portfolio_return(x) - target},
                   {'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple((0,1) for _ in range(num_assets))
    result = scipy.optimize.minimize(portfolio_volatility, num_assets*[1./num_assets], args=args, method='SLSQP', bounds=bounds, constraints=constraints)
    return result  # result.x is the array of weights

def efficient_frontier(mean_returns, cov_matrix, returns_range):
    efficients = []
    # In order to retain only the upper branch of the EF, I would need to restrict to returns higher than that with minimum volatility
    for ret in returns_range:
        efficients.append(efficient_frontier_volatilities(mean_returns, cov_matrix, ret))
        # This gives the volatility for the target returns
    return efficients

def compute_random_portfolios_and_ef(returns_df, num_portfolios, risk_free_rate, target_return):
    mean_returns = returns_df.mean()
    cov_matrix = returns_df.cov()
    std, return_, sharpe_ratio, _ = generate_random_portfolios(num_portfolios, mean_returns, cov_matrix, risk_free_rate)

    min_vol = min_variance_portfolio(mean_returns, cov_matrix)
    sdt_min, ret_min = portfolio_annualised_performance(min_vol['x'], mean_returns, cov_matrix)
    min_vol_allocation = pandas.DataFrame(min_vol.x, index=returns_df.columns, columns=['allocation'])
    min_vol_allocation.allocation = [round(value * 100, 2) for value in min_vol_allocation.allocation]
    min_vol_allocation = min_vol_allocation.T

    desired_return_efficient_portfolio = optimize_desired_return(returns_df=returns_df, target_return=target_return)
    sdt_desired_return, desired_return = portfolio_annualised_performance(desired_return_efficient_portfolio['x'],
                                                                          mean_returns, cov_matrix)
    desired_return_efficient_allocation = pandas.DataFrame(desired_return_efficient_portfolio.x, index=returns_df.columns,
                                                 columns=['allocation'])
    desired_return_efficient_allocation.allocation = [round(value * 100, 2) for value in desired_return_efficient_allocation.allocation]
    #desired_return_efficient_allocation = desired_return_efficient_allocation.T  # For readability

    annual_volatility = np.std(returns_df) * np.sqrt(252)
    annual_return = mean_returns * 252

    fig, ax = plt.subplots(figsize=(10, 7))
    ax.scatter(annual_volatility, annual_return, marker='o', s=200)
    for i, txt in enumerate(returns_df.columns):
        ax.annotate(txt, (annual_volatility[i], annual_return[i]), xytext=(10, 0), textcoords='offset points')

    plt.scatter(std, return_, c=sharpe_ratio, cmap='YlGnBu', marker='o', s=10, alpha=0.3)
    plt.colorbar()
    plt.scatter(sdt_min, ret_min, marker='*', color='g', s=500, label='Minimum volatility')
    plt.scatter(sdt_desired_return, desired_return, marker='*', color='r', s=500, label='Desired return efficient portfolio')

    target = np.linspace(min(annual_return), 24, 100)
    efficient_portfolios = efficient_frontier(mean_returns, cov_matrix, target)

    plt.plot([p['fun'] for p in efficient_portfolios], target, linestyle='-.', color='black',
             label='efficient frontier')
    plt.title('Calculated Portfolio Optimization based on Efficient Frontier')
    plt.xlabel('annualised volatility')
    plt.ylabel('annualised returns')
    plt.legend(labelspacing=0.8)
    plt.show()

    print("-" * 80)
    print("Desired return Portfolio Allocation\n")
    print("Annualised Return:", round(desired_return, 2))
    print("Annualised Volatility:", round(sdt_desired_return, 2))
    print("\n")
    print(desired_return_efficient_allocation)
    print("-" * 80)
    print("Minimum Volatility Portfolio Allocation\n")
    print("Annualised Return:", round(ret_min, 2))
    print("Annualised Volatility:", round(sdt_min, 2))
    print("\n")
    print(min_vol_allocation)
    print("-" * 80)
    print("Individual Funds Returns and Volatility\n")

    for i, txt in enumerate(returns_df.columns):
        print(txt, ":", "annualised return", round(annual_return[i], 2), ", annualised volatility:", round(annual_volatility[i], 2))
    print("-" * 80)

def optimize_desired_return(returns_df, target_return = 10):  # TODO: Refactor this
    mean_returns = returns_df.mean()
    cov_matrix = returns_df.cov()
    efficient_portfolio = efficient_frontier_volatilities(mean_returns, cov_matrix, target_return)

    return efficient_portfolio