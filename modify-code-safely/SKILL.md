---
name: modify-code-safely
description: Use before any task that may modify source code, tests, executable scripts, runtime configs, dependencies, data processing, training or inference behavior, public APIs, or checkpoint contracts. Run a read-only preflight, obtain user confirmation of preserved, allowed, and unknown behavior plus the planned scope, then enforce one production path and evidence-backed validation. Do not use for read-only explanation, review, diagnosis, planning, or documentation-only edits.
---

# Modify Code Safely

## Purpose

Act as a mandatory pre-change gate. Establish the behavioral contract and obtain user confirmation before making changes or executing validation. Keep the implementation minimal, single-path, and separated from test-only instrumentation.

## 1. Start With Read-Only Evidence

Announce that this skill is active and that it requires a pre-change confirmation gate.

Before proposing a change:

- Read all applicable `AGENTS.md` files and repository instructions.
- Confirm the exact repository, worktree, branch, entrypoint, active config, and relevant checkpoint or runtime mode.
- Run `git status` and inspect relevant diffs before touching a dirty worktree.
- Trace the current implementation, neighboring code, tests, configs, and documentation with read-only commands.
- Identify the real execution path and existing validation signals.

Before user confirmation, only perform read-only inspection such as file reads, search, `git status`, `git diff`, and `git log`. Do not edit files, create or switch branches, fetch or pull, install dependencies, run code or tests, start training or evaluation, operate remote jobs, or commit and push.

## 2. Freeze the Change Contract

For changes involving training semantics, inference semantics, data contracts, checkpoint ABI, public interfaces, dependencies, or production execution paths, explicitly classify:

- **Preserve:** behavior and contracts that must remain unchanged.
- **Allowed to change:** the exact behavior and files authorized to change.
- **Unknown:** unclear assumptions, risks, or choices that require a user decision.

Also report:

- the proposed implementation approach;
- the expected file and interface scope;
- the minimum validation plan;
- every uncertainty or issue that could materially affect correctness, compatibility, performance, or scope.

For every task that may modify code, ask at least one concrete confirmation question after read-only inspection, even if the request appears fully specified or no material **Unknown** is initially identified. Do not treat the original task request as satisfying this pre-change question requirement.

If the modification is so simple that no questions shuold be asked and only a few lines of codes or configs are being changed, do not do it yourself. Instead, ask the user to modify the code himself and give clear instructions on the way to change. And you don't need to ask for confirmation in this case because you did not change the code yourself.

Select the unresolved questions that are most important and most likely to change the plan. In each round, ask only a small number of those questions, then stop and wait for explicit user answers. After receiving the answers, re-evaluate the remaining unknowns and repeat the necessary read-only inspection. Continue this cycle until every issue that could materially affect the approach, training methods, behavioral contract, or validation conclusion is resolved and the user explicitly approves the final contract. Do not begin execution while any material item remains under **Unknown**.

Do not make a consequential technical choice, fill in an ambiguous requirement, or expand the scope on the user's behalf. Do not use default assumptions, configuration switches, fallback paths, parallel implementations, or an "implement first, decide later" approach to bypass unresolved decisions.

After confirmation, execute continuously within the approved contract without asking for every command. Pause and reconfirm if new uncertainty, risk, scope expansion, or a required change to the approved approach appears.

## 3. Verify Baselines Before Reuse

Before adapting an external repository, paper implementation, branch, or prior experiment, verify:

- exact version, commit, and configuration;
- training versus inference mode;
- input, output, mask, state, and checkpoint contracts;
- whether apparently similar modules have the same data dependencies and semantics.

Treat structural similarity as a lead, not proof of behavioral equivalence. Reuse only the contract-compatible portion.

## 4. Keep One Production Path

- Implement only the behavior required by the confirmed contract.
- Do not add configuration switches, fallback paths, compatibility wrappers, parallel implementations, legacy paths, unused abstractions, or speculative future interfaces unless explicitly required.
- Prefer the smallest change to existing functions, call sites, and tests.
- Do not perform unrelated refactors, formatting, renames, cleanup, or dependency changes.
- Preserve existing training, inference, checkpoint, data, and public-interface behavior unless the contract explicitly authorizes a change.

## 5. Isolate Validation From Production

- Make small-model, smoke, and benchmark configurations exercise the same production code path as the formal model. Reduce only official configuration values, data volume, or run length; do not create a toy implementation.
- Keep minimal reference computations for parity, shapes, masks, dependencies, gradients, or call counts under `tests/` only.
- Do not expose a test reference through production modules, public interfaces, evaluators, runtime fallbacks, or alternate execution paths.
- Put newly introduced fail-fast logic, checking branches, debug gates, additional shape checks, and smoke harnesses under `tests/`, not production code.
- If temporary production instrumentation is necessary for an experiment, isolate it on a dedicated experimental branch. Do not merge instrumentation or smoke-only changes into the production branch.
- Do not delete or refactor existing production checks unless the confirmed task explicitly requires it.

## 6. Require Real Validation Evidence

For correctness changes, run the smallest approved test that exercises the real path and report the exact command, result, and unverified scope.

For numerical or performance changes, compare under the same:

- checkpoint and code baseline;
- input and preprocessing;
- seed and noise where applicable;
- precision, hardware, runtime, and configuration.

Report numerical equivalence or bounded error, stage-level latency, end-to-end latency, and the relevant real-task or rollout result. Treat reduced calls, tokens, memory estimates, or theoretical FLOPs as hypotheses, not proof of success.

## 7. Finish Cleanly

- Inspect the final diff for unnecessary files, interfaces, branches, checks, or assumptions.
- Confirm test-only logic did not leak into production code.
- Update the required project documentation and experiment record after substantive changes or runs.
- Follow repository-specific commit, push, remote-validation, and documentation rules.
- State what was changed, what was validated, what remains unverified, and whether the approved contract was preserved.
