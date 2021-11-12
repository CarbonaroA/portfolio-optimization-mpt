from data_scraping import scrape_data_from_morningstar
from optimization_utils import compute_random_portfolios_and_ef

# JPM_D: LU0404220724
# JPM_CHI: LU0522352607
# JPM_USTech: LU0159053015
# JPM_JAP: LU1438161686
# ARCA_GLB: IT0005365090
# MS_US: LU0225737302
# ARCA_US: IT0001033502
# ARCA_EU: IT0001033486

idDict = {
    "JPM_D": "F000003WKM]2]0]FOITA$$ALL",
    "JPM_CHI": "F00000J5HX]2]0]FOITA$$ALL",
    "JPM_USTech": "F000005MPD]2]0]FOITA$$ALL",
    "JPM_JAP": "F00000XR4E]2]0]FOITA$$ALL",
    "ARCA_GLB": "F000013B0A]2]0]FOITA$$ALL",
    "MS_US": "F0GBR0645X]2]0]FOITA$$ALL",
    "ARCA_US": "F0GBR04W9M]2]0]FOITA$$ALL",
    "ARCA_EU": "F0GBR04W86]2]0]FOITA$$ALL",
}  # For the API id, inspect source code of Morningstar interactive graph and search for '$$ALL'

print("When choosing target metric, pick Daily returns to perform portfolio optimization, "
      "Price and Cumulative returns are mainly for reporting purposes")
df, requested_metric = scrape_data_from_morningstar(funds_dict=idDict)
# Scraping seems fine, but cumulative returns can be shown not from the very first day, effectively starting > 0
# Most likely because not all funds were sold on that date
# It is because of how data are scraped, INNER join to keep returns of common days
# (This should not affect the optimization part, which relies on daily returns happened on the same day)
# TODO: fix this? May want to scrape separately the cumulative returns for reporting, change join type

# Returns here are percentage change

if requested_metric == "return":
    returns = df.loc[:, df.columns != "date"].copy()
    mean_returns = returns.mean()
    cov_matrix = returns.cov()
    num_portfolios = 25000
    risk_free_rate = 0.0011  # 1y Treasury bill

    compute_random_portfolios_and_ef(returns_df=returns, num_portfolios=num_portfolios, risk_free_rate=risk_free_rate,
                                     target_return=15)
