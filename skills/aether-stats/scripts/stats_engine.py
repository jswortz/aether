import numpy as np
from scipy import stats
from typing import List, Tuple, Optional

def bootstrap_ci(data: List[float], n_bootstrap: int = 10000, ci: float = 0.95) -> Tuple[float, float]:
    """
    Calculate confidence interval using bootstrapping.
    Ideal for non-normal distributions or small samples where 
    traditional t-tests might fail.
    """
    boot_means = []
    for _ in range(n_bootstrap):
        sample = np.random.choice(data, size=len(data), replace=True)
        boot_means.append(np.mean(sample))
    
    lower_bound = np.percentile(boot_means, (1 - ci) / 2 * 100)
    upper_bound = np.percentile(boot_means, (1 + ci) / 2 * 100)
    
    return lower_bound, upper_bound

def bayesian_posterior_ci(data: List[float], ci: float = 0.95) -> Tuple[float, float]:
    """
    Calculate the Bayesian Credible Interval (Posterior) assuming a normal likelihood
    and a non-informative prior. Efficient for very small N when 
    underlying variance is approximately stable.
    """
    n = len(data)
    mean = np.mean(data)
    std_err = stats.sem(data)
    
    # Using t-distribution for the posterior mean (Normal-Inverse-Gamma conjugate prior equivalent)
    h = std_err * stats.t.ppf((1 + ci) / 2, n - 1)
    
    return mean - h, mean + h

def compare_improvement(baseline: List[float], treatment: List[float]) -> dict:
    """
    Compare two sets of experiments (e.g., Aether v1 vs v2).
    """
    b_mean = np.mean(baseline)
    t_mean = np.mean(treatment)
    improvement = (t_mean - b_mean) / b_mean * 100
    
    # Bootstrap difference
    diff_means = []
    n_boot = 10000
    for _ in range(n_boot):
        b_sample = np.random.choice(baseline, size=len(baseline), replace=True)
        t_sample = np.random.choice(treatment, size=len(treatment), replace=True)
        diff_means.append(np.mean(t_sample) - np.mean(b_sample))
    
    lower = np.percentile(diff_means, 2.5)
    upper = np.percentile(diff_means, 97.5)
    
    significant = not (lower <= 0 <= upper)
    
    return {
        "improvement_pct": improvement,
        "ci_95_lower": lower,
        "ci_95_upper": upper,
        "is_significant": significant
    }

if __name__ == "__main__":
    # Example usage
    baseline_runs = [12.5, 13.1, 12.8, 14.2, 11.9]
    aether_v2_runs = [15.2, 14.8, 16.1, 15.5, 14.9]
    
    results = compare_improvement(baseline_runs, aether_v2_runs)
    print(f"Improvement: {results['improvement_pct']:.2f}%")
    print(f"Significant: {results['is_significant']}")
