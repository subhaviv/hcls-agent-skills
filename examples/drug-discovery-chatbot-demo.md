# Drug Discovery Chatbot Demo: Skills + Code Exploration on MolPipeline

## Purpose

Demonstrates the chatbot frontend running against a cheminformatics/ML codebase ([MolPipeline](https://github.com/basf/MolPipeline)), showing how multiple HCLS skills activate across domain specialists to handle a complex drug repurposing workflow.

## Setup

### Prerequisites

- Node.js 18+
- `kiro-cli` installed and authenticated
- MolPipeline repo cloned to `~/Repositories/MolPipeline/`

### Install Skills

```bash
cd ~/Repositories/awesome-kiro-agent-skills-for-hcls
./install.sh --target kiro --mode multiagent --path ~/Repositories/MolPipeline/
```

This installs 38 HCLS skills + 9 multiagent configs into `~/Repositories/MolPipeline/.kiro/`.

### Start the Demo

```bash
# Terminal 1 — frontend
cd demo && npm run dev

# Terminal 2 — backend (pointed at MolPipeline)
cd demo && DEMO_CWD=~/Repositories/MolPipeline npm run server
```

Open http://localhost:5173 and select `hcls-multiagent` in the agent dropdown.

---

## Prompt: Multi-Domain Drug Repurposing Campaign

```
I'm running a drug repurposing campaign against a novel neuroinflammation target. First, review MolPipeline's similarity search capabilities and build a Tanimoto pipeline to find structural analogs of approved TNF-alpha inhibitors in my library. Second, for the top hits, design an ML experiment using MolPipeline's scaffold splitting and conformal prediction to predict BBB permeability — what model architecture, evaluation metrics, and reporting standards should I follow for a regulatory submission? Third, explain how I should validate these computational hits in a translational research framework — what's the path from in-silico to IND-enabling studies?
```

### What Happens

1. **Task list created** — coordinator breaks the multi-domain request into sequential/parallel tasks
2. **Subagent delegation** — routes to multiple specialists:
   - `hcls-drug-discovery` for repurposing strategy and cheminformatics pipeline
   - `hcls-ai-infra` for ML experiment design and regulatory reporting
   - `hcls-drug-discovery` again for translational validation framework
3. **Code exploration** — specialists read MolPipeline source:
   - `molpipeline/mol2any/` for fingerprint implementations
   - `molpipeline/estimators/` for nearest-neighbor and clustering
   - `notebooks/` for scaffold split examples
4. **Skill activation** — multiple skills load across specialists

### Skills Triggered

| Skill | Specialist | Why |
|-------|-----------|-----|
| `drug-repurposing` | hcls-drug-discovery | Target-based repurposing strategy, evidence hierarchy, translatability |
| `cheminformatics` | hcls-drug-discovery | Morgan fingerprints, Tanimoto similarity, PAINS filtering |
| `ml-researcher` | hcls-ai-infra | Scaffold split CV, evaluation metrics, TRIPOD+AI reporting, conformal prediction |
| `translational-research` | hcls-drug-discovery | T0→T1 validation path, proof of mechanism, IND-enabling study design |

### What to Observe in the UI

- **Sticky task list** tracking 3+ tasks at the top while response streams
- **Multiple subagent tabs** — each specialist working independently with its own skill badges
- **Inline tool chips** — compact file reads and searches as the agents explore MolPipeline source
- **Cross-domain synthesis** — coordinator combines specialist outputs into a coherent plan
- **Skill badges inside subagent tabs** — showing which domain knowledge each specialist loaded

---

## Simpler Single-Domain Prompts

For quicker demos that trigger individual skills:

### Cheminformatics (triggers `cheminformatics` skill)

```
I have a CSV of 5000 SMILES from a HTS campaign. Help me build a MolPipeline that calculates Morgan fingerprints (radius 3, 2048 bits), filters out PAINS compounds, computes Lipinski descriptors, and flags molecules violating Rule-of-5.
```

### ML Experiment Design (triggers `ml-researcher` skill)

```
Design a binary classification pipeline using MolPipeline + RandomForest for hERG toxicity prediction. I need proper scaffold-based train/test splitting, hyperparameter optimization, and conformal prediction for uncertainty quantification. What evaluation metrics should I use?
```

### Structure-Based Drug Design (triggers `structure-based-drug-design` skill)

```
After virtual screening with AutoDock Vina, I have 200 hit SMILES. Build a MolPipeline post-processing workflow that standardizes structures, removes salts, calculates physicochemical properties, clusters by Murcko scaffold, and ranks by predicted binding affinity vs drug-likeness.
```

---

## Key Takeaways

1. **Multi-specialist routing.** A single complex prompt activates 3+ domain specialists, each with their own skill set — keeping context efficient while covering broad ground.
2. **Code-grounded answers.** Specialists don't just recite theory — they read MolPipeline's actual implementations and reference specific modules/classes.
3. **Skill composition.** Drug repurposing + cheminformatics + ML design + translational research combine into a coherent end-to-end plan that no single skill could produce alone.
4. **Task tracking.** The sticky task list shows progress across the multi-step workflow, with checkmarks as each domain is addressed.
