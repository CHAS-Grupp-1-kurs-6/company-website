# Säkerhetsmanifest

Appliceras manuellt av admin på team1-primary. Pipelinen saknar behörighet att ändra dessa.

    sudo k3s kubectl apply -f k8s/security/

| Fil | Innehåll |
| --- | --- |
| rbac-github-deployer.yaml | Minsta behörighet för deploy via GitHub OIDC |
| sbom-cronjob.yaml | Daglig Trivy-scan av SBOM, larm till Discord (webhook i secret `sbom-vulnerability-scanner-secrets`) |
| networkpolicy-deny-metadata.yaml | Blockerar poddar mot GCP metadata-server 169.254.169.254 |
