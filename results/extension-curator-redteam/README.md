# Curator red-team extension

Run from the repository root in Linux with Python 3.11 or newer:

```bash
python report/curator_redteam.py --output-dir results/extension-curator-redteam
```

The script uses synthetic learn feedback, a fake model, temporary result/output directories, and the real `curate_skills`, `parse_skill_blocks`, and `validate_skill` flow. It probes a benign control, traversal name, direct eval-task identifier, Unicode dash and zero-width variants, a synthetic sentinel/data-read request, and hostile learn feedback. It does not call an API and records zero API cost. A synthetic task skeleton supplies task identifiers to `eval_markers()`; no lab task instructions, workspaces, answers, or check files are used to construct the attacks.

The before/after measure is a script-only normalization guard that rejects skill text containing a normalized eval marker. It is not a complete defense against semantic data requests or prompt injection. A scripted fake model proves prompt construction and parser/writer behavior only; it does not prove an LLM can be manipulated. Output creation refuses to overwrite an existing directory.
