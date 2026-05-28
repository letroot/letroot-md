---
tags: [podcast, pragmatic-engineer, ai, dev-tools, open-source, startups, engineering-culture, product-building]
date: 2026-05-27
episode: "Building OpenCode with Dax Raad"
guests: [[Dax Raad]]
url: https://www.youtube.com/watch?v=1VqKUrxR2C8
type: interview
---

# Building OpenCode with Dax Raad

## Summary

Dax Raad, co-founder of [[OpenCode]], joins [[Gergely Orosz]] on [[The Pragmatic Engineer Podcast]] to discuss building the most popular open source coding harness -- which surged from 650K to nearly 8M monthly active users in under a year. Despite building one of the fastest-growing AI developer tools, Dax is strikingly skeptical about AI's actual productivity impact on engineering teams. He shipped a memo to his own team admitting they were shipping too many features, absorbing too many hacks, and not actually moving faster. The conversation covers open source strategy, the Anthropic blocking incident that became a growth lever, inference profitability, GPU bottlenecks, the "muted prickle" of AI-assisted shortcuts, why taste and quality still matter, and the enduring importance of product judgment over raw output speed.

## Key Insights

*   **[[Open Source as Moat]]**: Dax saw that no coding agent had claimed the open source position. Just as [[Linux]] became the default through neutral ground where vendors compete, [[OpenCode]] positioned itself as the model-agnostic harness -- and the world kept handing them wins they didn't predict.

*   **[[The Muted Prickle]]**: Pre-AI, when you wrote a hack, you felt it. You remembered it next time. That feeling kept your judgment sharp. With AI agents doing the hacky work, that visceral feedback loop is muted. The landmines are still there -- they just won't blow up on you today. This is the core danger of AI-assisted development.

*   **[[Bottom-Up Dev Tool Adoption]]**: Dev tools are [[B2C Products]] in disguise. The massively adopted ones all grew bottom-up -- individual developers start using them, they creep into companies. Most programmers are terrible at thinking like consumer companies, which is why they build tools nobody loves to use.

*   **[[Inference Profitability]]**: The floor cost of delivering a token is the electricity to power the GPU. Dax has seen 80% margins on some models at sticker price. Prices have actually gone up (people switched from Sonnet to more expensive Opus), while compute costs haven't changed. He estimates [[Anthropic]] and [[OpenAI]] may be looking at 90% margins at current pricing.

*   **[[GPU Supply Crunch]]**: GPU demand for inference is growing exponentially while production grows linearly. Even at OpenCode's scale, GPU availability is a bottleneck. Big tech is vacuuming up the supply chain -- if you're a startup trying to get GPU capacity, the suppliers would rather talk to [[Amazon]] or [[Microsoft]].

*   **[[Shipping Restraint Over Velocity]]**: Dax's memo to his team identified three turbocharged problems: (1) shipping features not worth shipping, (2) absorbing hacks instead of redesigning systems, and (3) not spending enough time cleaning up. The worst part? They weren't even moving faster -- they just felt like they were.

*   **[[Quality as Differentiator]]**: When OpenCode launched, the key differentiator against [[Claude Code]] was that the terminal experience just felt better. They built their own rendering framework -- the "irrational" thing no engineering team should do -- and it gave them a quality edge against a much larger, better-funded competitor.

*   **[[Domain-Driven Design for AI Agents]]**: Old enterprise patterns like [[DDD]] are coming back because coding agents are "a bunch of idiots working 24/7." The verbose patterns humans hated writing? Agents don't care about verbosity. You get modular, safe code without the human cost of typing boilerplate.

*   **[[Regulatory Arbitrage as Strategy]]**: When [[Anthropic]] blocked Claude subscriptions in OpenCode, Dax immediately messaged [[OpenAI]] to take the opposite stance. The strategy: pick one temporary bad guy, galvanize all their competitors, push forward. They got [[GitHub Copilot]], [[Microsoft]], [[Google]], and others to rally around OpenCode as the neutral alternative.

*   **[[Emergent Systems Over Top-Down Design]]**: Dax is deeply influenced by [[Nassim Taleb]]'s ideas on [[Skin in the Game]] and emergent properties. Almost everything great comes not from top-down design but from smaller entities operating together, producing something unexpectedly great -- whether that's robust software, great neighborhoods, or open source ecosystems.

## Coach's Corner

**On Slowing Down to Speed Up:**

Dax's team memo is the most honest thing a founder building an AI-native tool could say: "We're shipping more, but we're not moving faster." As a founder building a SaaS product, this is the trap to watch for. AI lets you execute faster, but execution was never your bottleneck -- **thinking** was. Before AI, you spent 95% of your energy thinking and 5% doing. Now it's 96/4. The ratio barely moved. The danger is that faster execution creates an *illusion* of productivity while accumulating technical and product debt.

**On Product Judgment Over Output:**

The job of product isn't to receive a problem and ship the immediate solution. It's to absorb all the problems and find **one** solution that fixes fifty of them. AI doesn't help with this at all. Your competitive advantage as a founder isn't how fast you can prompt an agent -- it's how well you can see the pattern across user complaints and ship the elegant abstraction. Invest in your ability to think, not your ability to type.

**On Quality as a Startup Weapon:**

Big company products are rotting faster than ever because agents make it easy to ship mediocre code. This is an opportunity. Doing "irrational" things -- building your own terminal framework, polishing the first-time experience, refusing to brand GitHub commits -- these aren't luxuries. They're the things that make people feel competence before they even evaluate features. Quality compounds; shortcuts compound faster, but in the wrong direction.

**On Picking Your Industry:**

Software engineering is the only skill that lets you parachute into *any* industry and become a unicorn within a year. Don't just add UI components -- learn the domain. An engineer who understands farming *and* code is in the top 10 people worldwide for that intersection. In a world where AI can write code, your domain expertise is your moat.

**On Building in Public and Feedback Loops:**

OpenCode ships a demo first, then lets users tell them what to build next. No product managers summarizing feedback -- engineers get it directly. This tight loop is how small teams punch above their weight. If you're building a SaaS, keep the feedback loop direct. Don't let reports tell you what hurts -- feel it yourself.

## Action Items

*   [ ] **Audit your last sprint**: Were the features you shipped worth shipping, or did you just respond to the loudest request?
*   [ ] **Map your feedback loops**: Where are you insulated from customer pain? Are there "muted prickles" you're not feeling because an agent or a process stands between you and the consequence?
*   [ ] **Review your first-time experience**: Set up a clean Docker container and experience your product from scratch every two weeks, like Dax does.
*   [ ] **Evaluate your quality investments**: What's one "irrational" thing you could do that would make your product feel distinctly better?
*   [ ] **Schedule cleanup time**: Block time each sprint for paying down tech debt and cleaning up patterns. As Dax notes, cleaning is easier than ever with agents -- but you have to decide to do it.

## Resources

*   [Building OpenCode with Dax Raad (YouTube)](https://www.youtube.com/watch?v=1VqKUrxR2C8) - Full episode
*   [How Claude Code is Built](https://newsletter.pragmaticengineer.com/p/how-claude-code-is-built) - Pragmatic Engineer deep dive referenced in the episode
*   [How Codex is Built](https://newsletter.pragmaticengineer.com/p/how-codex-is-built) - Pragmatic Engineer deep dive referenced in the episode
*   [Skin in the Game](https://en.wikipedia.org/wiki/Skin_in_the_Game) by [[Nassim Taleb]] - Book recommended by Dax on emergent properties and bottom-up systems
*   [[OpenCode]] - Open source coding harness (https://opencode.ai)
*   [[SST]] - Dax's previous open source project for building full-stack serverless applications
*   [[OpenNext]] - Open source adapter for deploying Next.js on AWS, originally built by Dax's team