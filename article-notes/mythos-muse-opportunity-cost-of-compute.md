---
title: "Mythos, Muse, and the Opportunity Cost of Compute"
author: "Ben Thompson"
source: "https://stratechery.com/2026/mythos-muse-and-the-opportunity-cost-of-compute"
date: "2026-04-14"
tags:
  - article
  - ai
  - economics
  - stratechery
---

# Mythos, Muse, and the Opportunity Cost of Compute

## Summary
Ben Thompson discusses the shift in tech economics driven by AI, specifically how the era of zero marginal costs that defined [[Aggregation Theory]] is being challenged by the high opportunity costs of compute in 2025/2026. Models like [[Anthropic]]'s Mythos and [[Meta]]'s Muse highlight how hyperscalers must make difficult decisions on allocating scarce compute resources between internal workloads, enterprise customers, and consumers.

## Key Concepts

### Marginal Costs vs Opportunity Costs
- **Marginal Costs**: Tech historically operated on zero marginal costs (once infrastructure was built, adding a user cost almost nothing). AI changes this because every interaction requires compute. However, electricity and chips are still largely treated as fixed costs that *must* be utilized.
- **Opportunity Costs**: The real constraint is opportunity cost. Compute used for one customer or workload cannot be used for another. For example, [[Microsoft]] missed Azure growth expectations because it allocated GPU capacity to its own higher-margin products (like Copilot) instead of external customers.

### Anthropic and Mythos
- [[Anthropic]] announced *Mythos*, focusing on its security implications (e.g., finding software vulnerabilities via Project Glasswing).
- While security is a real concern, limiting Mythos access also solves Anthropic's opportunity cost problem: they are compute-constrained. Restricting access allows them to charge higher prices and manage their limited compute, avoiding the degradation issues seen with high consumer demand.
- Protecting against distillation (competitors training smaller models on frontier model outputs) is critical to protect both margins and compute availability.

### Meta's Unique Position with Muse
- [[Meta]] introduced *Muse Spark*, a natively multimodal reasoning model.
- Because Meta relies on an advertising business model and lacks a massive enterprise/cloud arm like Google or Microsoft, it doesn't face the same opportunity costs in serving consumers.
- This structural advantage allows Meta to dominate the consumer AI space without the tradeoff of losing lucrative enterprise deals, giving them a strong incentive to open-source models like Muse to commoditize the layer below them and pressure competitors' pricing power.

### Demand vs. Supply in AI
- The core of [[Aggregation Theory]] (owning demand/customers) remains relevant, but compute constraints mean supply cannot be taken for granted.
- [[OpenAI]] believes its massive infrastructure build-out will allow it to outpace Anthropic's product momentum by simply having more compute available to satisfy demand.
- However, Thompson wagers that owning demand will ultimately trump owning supply. If a product is good enough, it will attract the necessary capital and cash flow to secure compute (e.g., Anthropic's TPU deal with Google). 

## Notable Quotes
> "It’s opportunity costs, not marginal costs, that are the challenge facing hyperscalers. How much compute should go to customers, and which ones? How much should be reserved for internal workloads?"

> "In other words, Meta may actually face less competition in winning the consumer space than it might have seemed a few months ago, simply because that is their primary focus — and because they have their own model..."

> "My bet is that owning demand will ultimately trump owning supply, suggesting that the underlying principles of Aggregation Theory lives on."

## Related Links
- [[Aggregation Theory]]
- [[AI Economics]]
- [[Compute Constraints]]
- [[Frontier Models]]
