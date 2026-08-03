# Licenses

This release derives from two upstream datasets with **different** license terms.
They are shipped as separate files so each can be used under its own terms.

| Source | Files | License | Status |
|---|---|---|---|
| MuSiQue | `data/*/musique/*.jsonl` | permissive (verify) | **TODO: confirm + add text** |
| HotpotQA | `data/two_hop/hotpotqa/*.jsonl` | copyleft (verify) | **TODO: confirm + add text** |

TODO before release:
  1. Confirm the exact license and version for each upstream dataset from its
     official repository -- do not rely on secondhand claims.
  2. Save the full license text here as MuSiQue.txt and HotpotQA.txt.
  3. State the license of THIS derivative work, including the translations,
     which are a new contribution requiring their own terms.
  4. Note that scripts/make_combined.py output mixes both sources and so
     inherits the more restrictive terms.
