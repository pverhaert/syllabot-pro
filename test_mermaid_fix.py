"""
Test script to demonstrate Mermaid diagram fixing capabilities.
Run this to see how the mermaid_utils fixes common issues.
"""
from common.mermaid_utils import fix_mermaid_diagrams, validate_mermaid_syntax
from rich.console import Console

console = Console()

# Test case 1: Single line with semicolons (the issue from the screenshot)
test1 = """
# Chapter on Data Processing

Here's the workflow:

graph TD A[Ruwe CV Data] --> B{Data Preprocessing & NLP}; B --> C[Feature Extraction: Skills, Ervaring, Opleiding]; C --> D{Matching Algoritme: Cosinusgelijkenis}; D --> E[Similarity Score Berekening]; E --> F[Rangschikking van Kandidaten]; F --> G[Recruiter Review];

This shows the complete process.
"""

# Test case 2: Mermaid block with semicolons
test2 = """
# Database Schema

```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : places;
    ORDER ||--|{ LINE-ITEM : contains;
    CUSTOMER }|..|{ DELIVERY-ADDRESS : uses;
```

Above is the schema.
"""

# Test case 3: Unwrapped mermaid code
test3 = """
# Process Flow

flowchart LR
    Start --> Process
    Process --> Decision{Is Valid?}
    Decision -->|Yes| Success
    Decision -->|No| Error

That's the flow diagram.
"""

def run_test(test_name: str, content: str):
    console.print(f"\n{'='*80}", style="bold blue")
    console.print(f"TEST: {test_name}", style="bold blue")
    console.print(f"{'='*80}", style="bold blue")

    console.print("\n[yellow]BEFORE:[/yellow]")
    console.print(content)

    # Fix the content
    fixed = fix_mermaid_diagrams(content)

    console.print("\n[green]AFTER:[/green]")
    console.print(fixed)

    # Validate
    warnings = validate_mermaid_syntax(fixed)
    if warnings:
        console.print("\n[yellow]⚠️  Warnings:[/yellow]")
        for warning in warnings:
            console.print(f"  - {warning}", style="yellow")
    else:
        console.print("\n[green]✅ No warnings - Mermaid syntax looks good![/green]")

if __name__ == "__main__":
    console.print("\n[bold cyan]MERMAID DIAGRAM FIX DEMONSTRATION[/bold cyan]\n")
    console.print("This script demonstrates how the automatic Mermaid fixing works.\n")

    run_test("Single line with semicolons (your reported issue)", test1)
    run_test("Mermaid block with semicolons", test2)
    run_test("Unwrapped mermaid code", test3)

    console.print("\n" + "="*80, style="bold green")
    console.print("✅ All tests completed! The fix is now integrated into your application.", style="bold green")
    console.print("="*80 + "\n", style="bold green")

