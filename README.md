# Dagster Data Workflows Project

This repository contains various data processing workflows implemented using Dagster, designed to run in a Kubernetes environment.

## Project Structure
```
my_dagster_project/
├── Dockerfile
├── pyproject.toml
└── my_dagster_project/
    ├── __init__.py
    ├── assets/
    │   ├── __init__.py
    │   ├── pandas_workflow.py
    │   ├── polars_workflow.py
    │   ├── duckdb_workflow.py
    │   ├── postgres_workflow.py
    │   └── sales_workflow.py
    └── resources/
        ├── __init__.py
        └── database.py
```

## Current Workflows
1. **Pandas Workflow**: Stock market data analysis
2. **Polars Workflow**: Weather data analysis
3. **DuckDB Workflow**: Analytics using DuckDB
4. **Postgres Workflow**: Database operations
5. **Sales Workflow**: Synthetic data analysis

## Adding New Workflows

### 1. Create New Asset File
```python
# my_dagster_project/assets/new_workflow.py

from dagster import asset, Output, MetadataValue

@asset
def my_new_asset():
    """
    Description of what this asset does
    """
    # Your asset logic here
    return Output(
        result,
        metadata={
            "rows": len(result),
            "preview": MetadataValue.md(result.head().to_markdown())
        }
    )
```

### 2. Adding Resources (if needed)
```python
# my_dagster_project/resources/new_resource.py

from dagster import resource

@resource(config_schema={"param": str})
def my_new_resource(context):
    return MyResourceClass(context.resource_config["param"])
```

### 3. Register Resource (if added)
Update `my_dagster_project/__init__.py`:
```python
from dagster import Definitions
from .resources.new_resource import my_new_resource

defs = Definitions(
    assets=[],  # Assets are auto-discovered
    resources={
        "my_new_resource": my_new_resource,
        # ... other resources
    }
)
```

## Docker Image Generation

The CI/CD pipeline automatically builds and pushes Docker images based on git actions:

1. **Branch Builds**:
   - Format: `your-username/my-dagster-project:branch-name`
   - Example: `your-username/my-dagster-project:feature-new-workflow`

2. **Pull Request Builds**:
   - Format: `your-username/my-dagster-project:pr-{number}`
   - Example: `your-username/my-dagster-project:pr-123`

3. **Release Tags**:
   - Format: `your-username/my-dagster-project:{version}`
   - Example: `your-username/my-dagster-project:1.0.0`

4. **Main Branch**:
   - Tag: `your-username/my-dagster-project:latest`

5. **Commit SHA**:
   - Format: `your-username/my-dagster-project:sha-{hash}`
   - Example: `your-username/my-dagster-project:sha-a1b2c3d`

## Deploying to Kubernetes

### 1. Create Deployment File
```yaml
# kubernetes/my-workflow-deployment.yaml
apiVersion: dagster.io/v1alpha1
kind: UserDeployment
metadata:
  name: my-new-workflow
spec:
  deployment:
    image:
      repository: your-username/my-dagster-project
      tag: latest  # or specific version
    dagsterApiGrpcArgs:
      - "--module-name"
      - "my_dagster_project"
```

### 2. Deploy to Kubernetes
```bash
# Deploy new version
kubectl apply -f kubernetes/my-workflow-deployment.yaml

# Check deployment status
kubectl get userdeployments
```

### 3. Update Existing Deployment
```bash
# Update image version
kubectl patch userdeployment my-new-workflow --type=json \
  -p='[{"op": "replace", "path": "/spec/deployment/image/tag", "value": "1.0.1"}]'
```

## Development Guidelines

### 1. Code Style
- Use Black for code formatting
- Add type hints where possible
- Include docstrings for all assets and resources

### 2. Testing
```bash
# Run tests
pytest tests/

# Format code
black .
isort .
```

### 3. Version Control
- Create feature branches from main
- Use conventional commits:
  - feat: New feature
  - fix: Bug fix
  - docs: Documentation
  - chore: Maintenance

### 4. Creating Releases
```bash
# Tag new version
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

## Troubleshooting

### Common Issues
1. **Asset Not Found**:
   - Check asset file naming
   - Verify module is in correct directory

2. **Resource Configuration**:
   - Verify resource config in deployment
   - Check Kubernetes secrets if needed

3. **Docker Build Fails**:
   - Check dependency versions
   - Verify system requirements

### Logs
```bash
# Get dagster logs
kubectl logs -l app=dagster-user-deployments

# Check deployment status
kubectl describe userdeployment my-workflow
```

## Contributing
[Contributions Welcome](CONTRIBUTION.md)

## License
MIT License - See LICENSE file for details