"""Auto-generated organism wrapping 58 functions from scipy.stats."""

import numpy as np
from organisms.base import MathematicalOrganism


class ScipyStatsOrganism(MathematicalOrganism):
    name = "scipy_stats"
    operations = {
        "anderson": {
            "code": "def anderson(x):\n    import scipy.stats\n    result = scipy.stats.anderson(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "bayes_mvs": {
            "code": "def bayes_mvs(x):\n    import scipy.stats\n    result = scipy.stats.bayes_mvs(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "boxcox": {
            "code": "def boxcox(x):\n    import scipy.stats\n    result = scipy.stats.boxcox(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "boxcox_normmax": {
            "code": "def boxcox_normmax(x):\n    import scipy.stats\n    result = scipy.stats.boxcox_normmax(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "chi2_contingency": {
            "code": "def chi2_contingency(x):\n    import scipy.stats\n    result = scipy.stats.chi2_contingency(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "chisquare": {
            "code": "def chisquare(x):\n    import scipy.stats\n    result = scipy.stats.chisquare(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "circmean": {
            "code": "def circmean(x):\n    import scipy.stats\n    result = scipy.stats.circmean(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "circstd": {
            "code": "def circstd(x):\n    import scipy.stats\n    result = scipy.stats.circstd(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "circvar": {
            "code": "def circvar(x):\n    import scipy.stats\n    result = scipy.stats.circvar(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "combine_pvalues": {
            "code": "def combine_pvalues(x):\n    import scipy.stats\n    result = scipy.stats.combine_pvalues(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "array",
        },
        "cumfreq": {
            "code": "def cumfreq(x):\n    import scipy.stats\n    result = scipy.stats.cumfreq(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "describe": {
            "code": "def describe(x):\n    import scipy.stats\n    result = scipy.stats.describe(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "integer",
        },
        "differential_entropy": {
            "code": "def differential_entropy(x):\n    import scipy.stats\n    result = scipy.stats.differential_entropy(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "ecdf": {
            "code": "def ecdf(x):\n    import scipy.stats\n    result = scipy.stats.ecdf(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "entropy": {
            "code": "def entropy(x):\n    import scipy.stats\n    result = scipy.stats.entropy(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "expectile": {
            "code": "def expectile(x):\n    import scipy.stats\n    result = scipy.stats.expectile(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "find_repeats": {
            "code": "def find_repeats(x):\n    import scipy.stats\n    result = scipy.stats.find_repeats(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "gmean": {
            "code": "def gmean(x):\n    import scipy.stats\n    result = scipy.stats.gmean(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "gstd": {
            "code": "def gstd(x):\n    import scipy.stats\n    result = scipy.stats.gstd(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "gzscore": {
            "code": "def gzscore(x):\n    import scipy.stats\n    result = scipy.stats.gzscore(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "hmean": {
            "code": "def hmean(x):\n    import scipy.stats\n    result = scipy.stats.hmean(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "iqr": {
            "code": "def iqr(x):\n    import scipy.stats\n    result = scipy.stats.iqr(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "matrix",
            "output_type": "scalar",
        },
        "jarque_bera": {
            "code": "def jarque_bera(x):\n    import scipy.stats\n    result = scipy.stats.jarque_bera(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "kstat": {
            "code": "def kstat(x):\n    import scipy.stats\n    result = scipy.stats.kstat(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "kstatvar": {
            "code": "def kstatvar(x):\n    import scipy.stats\n    result = scipy.stats.kstatvar(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "kurtosis": {
            "code": "def kurtosis(x):\n    import scipy.stats\n    result = scipy.stats.kurtosis(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "kurtosistest": {
            "code": "def kurtosistest(x):\n    import scipy.stats\n    result = scipy.stats.kurtosistest(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "lmoment": {
            "code": "def lmoment(x):\n    import scipy.stats\n    result = scipy.stats.lmoment(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "median_abs_deviation": {
            "code": "def median_abs_deviation(x):\n    import scipy.stats\n    result = scipy.stats.median_abs_deviation(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "mode": {
            "code": "def mode(x):\n    import scipy.stats\n    result = scipy.stats.mode(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "moment": {
            "code": "def moment(x):\n    import scipy.stats\n    result = scipy.stats.moment(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "mvsdist": {
            "code": "def mvsdist(x):\n    import scipy.stats\n    result = scipy.stats.mvsdist(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "normaltest": {
            "code": "def normaltest(x):\n    import scipy.stats\n    result = scipy.stats.normaltest(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "power_divergence": {
            "code": "def power_divergence(x):\n    import scipy.stats\n    result = scipy.stats.power_divergence(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "ppcc_max": {
            "code": "def ppcc_max(x):\n    import scipy.stats\n    result = scipy.stats.ppcc_max(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "probplot": {
            "code": "def probplot(x):\n    import scipy.stats\n    result = scipy.stats.probplot(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "quantile_test": {
            "code": "def quantile_test(x):\n    import scipy.stats\n    result = scipy.stats.quantile_test(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "rankdata": {
            "code": "def rankdata(x):\n    import scipy.stats\n    result = scipy.stats.rankdata(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "relfreq": {
            "code": "def relfreq(x):\n    import scipy.stats\n    result = scipy.stats.relfreq(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "sem": {
            "code": "def sem(x):\n    import scipy.stats\n    result = scipy.stats.sem(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "shapiro": {
            "code": "def shapiro(x):\n    import scipy.stats\n    result = scipy.stats.shapiro(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "siegelslopes": {
            "code": "def siegelslopes(x):\n    import scipy.stats\n    result = scipy.stats.siegelslopes(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "sigmaclip": {
            "code": "def sigmaclip(x):\n    import scipy.stats\n    result = scipy.stats.sigmaclip(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "skew": {
            "code": "def skew(x):\n    import scipy.stats\n    result = scipy.stats.skew(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "skewtest": {
            "code": "def skewtest(x):\n    import scipy.stats\n    result = scipy.stats.skewtest(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "theilslopes": {
            "code": "def theilslopes(x):\n    import scipy.stats\n    result = scipy.stats.theilslopes(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "tiecorrect": {
            "code": "def tiecorrect(x):\n    import scipy.stats\n    result = scipy.stats.tiecorrect(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "tmax": {
            "code": "def tmax(x):\n    import scipy.stats\n    result = scipy.stats.tmax(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "tmean": {
            "code": "def tmean(x):\n    import scipy.stats\n    result = scipy.stats.tmean(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "tmin": {
            "code": "def tmin(x):\n    import scipy.stats\n    result = scipy.stats.tmin(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "tsem": {
            "code": "def tsem(x):\n    import scipy.stats\n    result = scipy.stats.tsem(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "tstd": {
            "code": "def tstd(x):\n    import scipy.stats\n    result = scipy.stats.tstd(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "tvar": {
            "code": "def tvar(x):\n    import scipy.stats\n    result = scipy.stats.tvar(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "variation": {
            "code": "def variation(x):\n    import scipy.stats\n    result = scipy.stats.variation(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "wilcoxon": {
            "code": "def wilcoxon(x):\n    import scipy.stats\n    result = scipy.stats.wilcoxon(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "yeojohnson": {
            "code": "def yeojohnson(x):\n    import scipy.stats\n    result = scipy.stats.yeojohnson(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
        "yeojohnson_normmax": {
            "code": "def yeojohnson_normmax(x):\n    import scipy.stats\n    result = scipy.stats.yeojohnson_normmax(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "scalar",
        },
        "zscore": {
            "code": "def zscore(x):\n    import scipy.stats\n    result = scipy.stats.zscore(x)\n    if isinstance(result, tuple):\n        result = result[0]\n    return result\n",
            "input_type": "array",
            "output_type": "array",
        },
    }
