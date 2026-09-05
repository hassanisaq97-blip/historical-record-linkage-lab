# LLM-assisteret linkage (eksperimentelt tillæg) - IKKE kørt

Fandt 685 'gråzone'-par (ML predicted_proba mellem 0.35 og 0.65), men ingen lokal Ollama-server blev fundet paa http://localhost:11434/api/generate (forsoegt via GET /api/tags).

Dette er forventet i dette udviklingsmiljoe, hvor netvaerksadgang til ollama.com/registry.ollama.ai er blokeret (verificeret empirisk - se docs/limitations.md), saa Ollama og en model kan ikke installeres her. Trinnet indgaar bevidst ikke i hovedpipelinen eller i README's rapporterede precision/recall/F1-tal. Kør selv med:

```bash
ollama serve &
ollama pull llama3.2
snakemake --snakefile workflow/Snakefile --cores 1 llm_supplement
```
