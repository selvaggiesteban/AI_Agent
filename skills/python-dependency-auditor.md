---
name: Python Dependency Auditor
description: Secures Python projects by auditing third-party packages for vulnerabilities, license compliance, and bloat.
---

# Python Dependency Auditor

This skill ensures that the Python ecosystem used in the project is secure, lean, and legally compliant, preventing "supply chain" attacks.

## Workflow

### 1. Perceive (Diagnosis)
- **Dependency Mapping**: Generate a full list of installed packages using `pip freeze` or `poetry lock`.
- **Vulnerability Scan**: Use `safety` or `pip-audit` to find known CVEs in current versions.
- **License Audit**: Identify packages with restrictive licenses (e.g., GPL) that may conflict with project goals.
- **Bloat Analysis**: Identify unused dependencies that are still listed in `requirements.txt`.

### 2. Plan (Analysis)
- **Update Strategy**: Decide which packages need immediate updates vs. those that require careful migration (breaking changes).
- **Alternative Search**: Identify vulnerable packages that have no fix and find secure alternatives.
- **Pinning Policy**: Define a versioning strategy (e.g., pinning to exact versions for production, ranges for dev).
- **Audit Cadence**: Determine how often the audit should run (e.g., on every PR).

### 3. Act (Programming)
- **Version Update**: Update `requirements.txt` or `pyproject.toml` to the secure versions.
- **Dependency Pruning**: Remove unused packages to reduce the attack surface.
- **Lockfile Implementation**: Use `poetry.lock` or `pip-compile` (pip-tools) to ensure deterministic builds.
- **CI Integration**: Add `pip-audit` as a mandatory check in the GitHub Actions workflow.
- **License Filtering**: Implement a check to block the addition of packages with forbidden licenses.

### 4. Evaluate (Verification)
- **CVE-Free Report**: Run `pip-audit` and verify a "No known vulnerabilities found" result.
- **Regression Testing**: Run the full test suite to ensure that updating dependencies didn't break the app.
- **Build Reproducibility**: Verify that the app installs identically on different machines using the lockfile.
- **Size Check**: Compare the size of the virtual environment before and after pruning.
