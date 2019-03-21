import os
import numpy as np
import pandas as pd
import warnings
pd.core.common.is_list_like = pd.api.types.is_list_like
import pandas_datareader.data as web
import scipy.stats as st
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

np.random.seed(seed=233423)

sns.set_style('whitegrid')
sns.set_context('talk')
sns.set_palette('dark')

os.environ['TIINGO_API_KEY'] = 'ba62a0fba810f937382b5e772f8f152b58c4ebfc'

N_DAYS = 15

# Create models from data
def best_fit_distribution(df, bins=200, ax=None, n_days_projection=N_DAYS):
    """Model data by finding best fit distribution to data"""
    real_projections = create_real_days_projection(df, n_days=n_days_projection)
    data = real_projections[1]

    std_real = np.array([real_projections[i].std() for i in real_projections])
    mean_real = np.array([real_projections[i].mean() for i in real_projections])

    # Get histogram of original data
    y, x = np.histogram(data, bins=bins, density=True)
    x = (x + np.roll(x, -1))[:-1] / 2.0

    # Distributions to check
    DISTRIBUTIONS = [
        st.alpha,st.anglit,st.arcsine,st.beta,st.betaprime,st.bradford,st.burr,st.cauchy,st.chi,st.chi2,#st.cosine,
        st.dgamma,st.dweibull,st.erlang,st.expon,st.exponnorm,st.exponweib,st.exponpow,st.f,st.fatiguelife,st.fisk,
        st.foldcauchy,st.foldnorm,st.frechet_r,st.frechet_l,st.genlogistic,st.genpareto,st.gennorm,st.genexpon,
        st.genextreme,st.gausshyper,st.gamma,st.gengamma,st.genhalflogistic,st.gilbrat,st.gompertz,st.gumbel_r,
        st.gumbel_l,st.halfcauchy,st.halflogistic,st.halfnorm,st.halfgennorm,st.hypsecant,st.invgamma,st.invgauss,
        st.invweibull,st.johnsonsb,st.johnsonsu,st.ksone,st.kstwobign,st.laplace,st.levy,st.levy_l,st.levy_stable,
        st.logistic,st.loggamma,st.loglaplace,st.lognorm,st.lomax,st.maxwell,st.mielke,st.nakagami,st.ncx2,st.ncf,
        st.nct,st.norm,st.pareto,st.pearson3,
        st.powerlaw,st.powerlognorm,st.powernorm,
        #st.rdist,
        st.reciprocal,st.rayleigh,st.rice,st.recipinvgauss,#st.semicircular,
        st.t,st.triang,st.truncexpon,st.truncnorm,st.tukeylambda,
        st.uniform,st.vonmises,st.vonmises_line,st.wald,st.weibull_min,st.weibull_max,st.wrapcauchy
    ]

    # Best holders
    best_distribution = st.norm
    best_params = (0.0, 1.0)
    best_sse = np.inf

    # Estimate distribution parameters from data
    for distribution in DISTRIBUTIONS:

        # Try to fit the distribution
        try:
            # Ignore warnings from data that can't be fit
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore')

                # fit dist to data
                params = distribution.fit(data, floc=data.mean())

                # Separate parts of parameters
                arg = params[:-2]
                loc = params[-2]
                scale = params[-1]

                # Calculate fitted PDF and error with fit in distribution
                pdf = distribution.pdf(x, loc=loc, scale=scale, *arg)
                sse = np.sum(np.power(y - pdf, 2.0))
                dist_mean = distribution.mean(*params)


                # validate that the distribution mean corresponds to the loc parameter
                if abs((loc-dist_mean)/loc)>0.01:
                    continue

                # if axis pass in add to plot
                try:
                    if ax:
                        pd.Series(pdf, x).plot(ax=ax)
                    end
                except Exception:
                    pass

                # create the projection dict for each day:
                print('DOING: '+distribution.name)
                projection = create_projected_sample(distribution, params, sample_size=100000, n_days=n_days_projection)
                std_projected = np.array([projection[i].std() for i in projection])
                mean_projected = np.array([projection[i].mean() for i in projection])

                sse_std = np.sum(np.power(std_real - std_projected, 2.0))
                sse_mean = np.sum(np.power(mean_real - mean_projected, 2.0))
                sse = sse_std  # (sse_std/std_real[-1]+sse_mean/std_real[-1])

                # identify if this distribution is better
                if best_sse > sse > 0:
                    best_distribution = distribution
                    best_params = params
                    best_sse = sse
                    means = mean_projected
                    stds = std_projected

        except Exception:
            pass

    return (best_distribution.name, best_params, mean_real, means, std_real, stds)


def create_real_days_projection(df, n_days=10):
    """
    It assumes that the df has a column 'logP'.

    Returns: dict with the values of the real cummulative returns for each day spacing in ndays
    """
    real_rets_dict = {0: np.array([0])}
    for n in range(1, n_days):
        real_rets_dict[n] = df.iloc[::n].rolling(2).apply(lambda x: x[-1]-x[0], raw=True)['logP'].dropna().values
    return real_rets_dict

def create_projected_sample(distribution, dist_params, sample_size=10, n_days=10):
    """
    Creates a dict containing a sample with size "sample_size"
        of the projection of the distribution for each day in n_days.n_days

    returns: dict with a sample of projected rets for each day in n_days
    """
    projections_dict={}
    projected_sample = np.zeros(sample_size)
    projections_dict[0] = projected_sample
    for n in range(1, n_days):
        projections_dict[n] = projections_dict[n-1] + distribution.rvs(*dist_params, size=sample_size)
    return projections_dict


def make_pdf(dist, params, size=10000):
    """Generate distributions's Probability Distribution Function """

    # Separate parts of parameters
    arg = params[:-2]
    loc = params[-2]
    scale = params[-1]

    # Get sane start and end points of distribution
    start = dist.ppf(0.01, *arg, loc=loc, scale=scale) if arg else dist.ppf(0.01, loc=loc, scale=scale)
    end = dist.ppf(0.99, *arg, loc=loc, scale=scale) if arg else dist.ppf(0.99, loc=loc, scale=scale)

    # Build PDF and turn into pandas Series
    x = np.linspace(start, end, size)
    y = dist.pdf(x, loc=loc, scale=scale, *arg)
    pdf = pd.Series(y, x)

    return pdf

# Load data from statsmodels datasets
start = datetime(2005, 9, 1)
end = datetime(2019, 9, 1)
df = web.DataReader(['AMZN'], 'tiingo', start, end)
df['logP'] = np.log(df['close'])
df['cum_rets'] = df['logP'].rolling(2).apply(lambda x: x[-1]-x[0], raw=True).dropna()
data = df['cum_rets'].dropna()


print('hello')

# Plot for comparison
plt.figure(figsize=(12,8))
ax = data.plot(kind='hist', bins=50, density=True, alpha=0.5)
# Save plot limits
dataYLim = ax.get_ylim()

# Find best fit distribution
best_fit_name, best_fit_params, mean_real, means, std_real, stds = best_fit_distribution(df, 200, ax)
best_dist = getattr(st, best_fit_name)

# Update plots
ax.set_ylim(dataYLim)
ax.set_title(u'El Niño sea temp.\n All Fitted Distributions')
ax.set_xlabel(u'Temp (°C)')
ax.set_ylabel('Frequency')

# Make PDF with best params 
pdf = make_pdf(best_dist, best_fit_params)

# Display
plt.figure(figsize=(12,8))
ax = pdf.plot(lw=2, label='PDF', legend=True)
data.plot(kind='hist', bins=50, density=True, alpha=0.5, label='Data', legend=True, ax=ax)

param_names = (best_dist.shapes + ', loc, scale').split(', ') if best_dist.shapes else ['loc', 'scale']
param_str = ', '.join(['{}={:0.5f}'.format(k,v) for k,v in zip(param_names, best_fit_params)])
dist_str = '{}({})'.format(best_fit_name, param_str)

ax.set_title(u'El Niño sea temp. with best fit distribution \n' + dist_str)
ax.set_xlabel(u'Temp. (°C)')
ax.set_ylabel('Frequency')


plt.figure(figsize=(12,8))
plt.plot(range(N_DAYS), means, '-o', label='projection')
plt.plot(range(N_DAYS), mean_real, '-o', label='real')
plt.legend()

plt.figure(figsize=(12,8))
plt.plot(range(N_DAYS), stds, '-o', label='projection')
plt.plot(range(N_DAYS), std_real, '-o', label='real')
plt.legend()

plt.show()
