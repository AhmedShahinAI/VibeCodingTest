Read and follow `subskills/ui-plan/SKILL.md` completely before acting.

Run the executable planning wrapper from the project root:

```bash
python scripts/ui_plan_workflow.py --root . --brand-policy=strict
```

If strict mode blocks on missing approval, use proposal mode only for review:

```bash
python scripts/ui_plan_workflow.py --root . --brand-policy=proposal --draft --proposal A
```

After the user approves a direction, write approval with:

```bash
python scripts/approve_brand.py --root . --proposal A
```

Then rerun strict mode so Phase 0, the design system, and the token-backed page plan are updated together.
