---
name: aether-stats
description: Statistical analysis and experimental design skill for Aether. Use to calculate confidence intervals, perform bootstrapping, or Bayesian posterior estimation for performance metrics. Critical for validating high-variance experiments like Mixture of Experts (MoE) tuning.
---

# Aether Stats: Experimental Integrity

This skill provides robust statistical methods for validating performance improvements in the Aether swarm, especially when dealing with high-temperature stochastic processes or small sample sizes.

## 🛠 Core Capabilities

### 1. Bootstrapping CIs
Used when the underlying distribution is unknown or non-normal (common in LLM latency/token-per-second distributions).
- **Tool**: `scripts/stats_engine.py -> bootstrap_ci`
- **When to use**: Sample size N > 10, high variance, non-Gaussian behavior.

### 2. Bayesian Posterior Estimation
Provides a "credible interval" for the mean, assuming a Normal-Inverse-Gamma conjugate prior.
- **Tool**: `scripts/stats_engine.py -> bayesian_posterior_ci`
- **When to use**: Extremely small sample sizes (N < 10) where prior knowledge of variance stability is available.

## 🎯 Use Cases

### Use Case 1: Validating Swarm Handoff Efficiency
Compare latency of SCION handoffs before and after a router optimization.
```python
results = compare_improvement(v1_latencies, v2_latencies)
if results['is_significant']:
    # Proceed with deployment
```

### Use Case 2: Multi-Model Token Efficiency
Calculate the 95% CI for token costs across different model configurations to ensure cost-savings are not due to noise.

### Use Case 3: Evaluating "Gemma 4" Offline MoE Recipes
**Scenario**: Testing a high-temperature (T=1.5) 8-expert sparse MoE configuration for a speculative "Gemma 4" model in an air-gapped environment.

**The "High-Temp MoE" Recipe**:
- **Architecture**: 8x7B Sparse MoE.
- **Expert Selection**: Top-2 Gating.
- **Sampling**: Temperature-scaled Softmax (T=1.5) to maximize expert diversity.
- **Quantization**: 4-bit Offline KV-Cache for context extension.
- **Validation Requirement**: Since T=1.5 introduces high variance, use **Bootstrapping** to ensure that "Instruction Following" scores remain within acceptable 95% CI bounds compared to the T=1.0 baseline.

## 🚀 Execution Pattern

To run a statistical validation within a worker:
1. Collect metrics into a list.
2. Call the `aether-stats` tools to verify significance.
3. Only commit "Self-Evolutions" if `is_significant` is True.

---
**Data-driven evolution. Statistically sound swarms.**
