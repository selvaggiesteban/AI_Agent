---
name: Terraform Edge Provider
description: Manages Cloudflare and Edge infrastructure as code (IaC) for reproducible and versioned environments.
---

# Terraform Edge Provider

This skill uses HashiCorp Terraform to manage Cloudflare DNS, Workers, Pages, and Zero Trust configurations, ensuring environment parity.

## Workflow

### 1. Perceive (Diagnosis)
- **Infrastructure Audit**: Identify manually created resources in the Cloudflare dashboard.
- **State Analysis**: Check for existing `terraform.tfstate` files and their current synchronization.
- **Provider Versioning**: Verify the `cloudflare` provider version and its compatibility with current API features.
- **Dependency Mapping**: Map the relationship between DNS records, Workers, and KV namespaces.

### 2. Plan (Analysis)
- **Module Design**: Create reusable modules for common patterns (e.g., "Edge Site" module containing DNS + Worker + Pages).
- **Variable Strategy**: Define environment-specific variables (e.g., `prod_zone_id` vs `dev_zone_id`).
- **Backend Selection**: Choose a remote state backend (e.g., Terraform Cloud, S3, or Cloudflare R2) for team collaboration.
- **Resource Ordering**: Plan the creation sequence to avoid dependency errors (e.g., create KV before the Worker that binds to it).

### 3. Act (Programming)
- **Provider Configuration**: Setup the `cloudflare` provider with an API token (using least privilege).
- **Resource Definition**: Write `.tf` files for `cloudflare_record`, `cloudflare_worker_script`, and `cloudflare_worker_namespace`.
- **State Import**: Use `terraform import` to bring existing manual resources under IaC management.
- **Execution**: Run `terraform plan` followed by `terraform apply` to synchronize the state.
- **CI/CD Integration**: Integrate Terraform into GitHub Actions for automated infrastructure updates.

### 4. Evaluate (Verification)
- **State Drift Check**: Run `terraform plan` to ensure no manual changes have drifted from the code.
- **Resource Validation**: Verify that the deployed resources in the dashboard match the Terraform configuration.
- **Dependency Test**: Ensure that updating a shared resource (e.g., a KV namespace) propagates correctly to dependent Workers.
- **Destruction Test**: (In dev) Run `terraform destroy` to verify a clean teardown.
