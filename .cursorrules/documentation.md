# Documentation Standards

## When to Document

**Do NOT create documentation** for:
- Simple utility functions
- Self-explanatory code
- Small helper scripts
- Experimental or temporary code

Documentation is only needed for:
- Public APIs
- Complex algorithms that require explanation
- When explicitly requested by the user

## Documentation Format

### Python Docstrings

All functions, classes, and modules must have docstrings following Google style:

```python
def process_data(data: dict) -> dict:
    """
    Process input data and return transformed result.
    
    Args:
        data: Input dictionary with required fields
        
    Returns:
        Transformed dictionary with processed data
        
    Raises:
        ValueError: If required fields are missing
    """
    # Implementation
```

### Markdown Conventions

- Use proper heading hierarchy (H1 for title, H2 for sections, etc.)
- Use code fences with language tags for code blocks
- Use tables for structured data
- Include links to related documentation

### README Files

Each major directory should have a README.md with:
- Purpose of the directory
- Key files and their roles
- How to use/run the code
- Dependencies and prerequisites

## Project Documentation Structure

```
docs/
├── workflow.md              # Main workflow documentation
└── diagrams/                # Mermaid diagrams
    ├── README.md            # Diagram index
    └── *.md                 # Individual diagram files

specs/
└── {feature-id}/            # Feature specifications
    ├── spec.md              # Main specification
    ├── plan.md              # Technical plan
    ├── quickstart.md        # Quick start guide
    └── README.md            # Feature overview
```

## Code Comments

- Use comments to explain **why**, not **what**
- Avoid obvious comments that just repeat the code
- Document complex business logic and algorithms
- Include TODO comments with context when needed

## API Documentation

For public APIs:
- Document all parameters and return values
- Include example usage
- Document error conditions
- Specify version compatibility

## Related Rules

- See [validation.md](validation.md) for Mermaid diagram standards
- See [python.md](python.md) for Python docstring requirements

