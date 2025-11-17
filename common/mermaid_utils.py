"""
Utility functions for fixing and validating Mermaid diagrams in markdown content.
"""
import re


def fix_mermaid_diagrams(content: str) -> str:
    """
    Fix common Mermaid diagram formatting issues in markdown content.

    Issues fixed:
    1. Mermaid code on a single line with semicolons -> multi-line format
    2. Missing code block wrappers -> add ```mermaid wrapper
    3. Semicolons between statements -> remove them
    4. Improperly formatted Mermaid blocks

    Args:
        content: Markdown content that may contain Mermaid diagrams

    Returns:
        Fixed markdown content with properly formatted Mermaid diagrams
    """
    if not content:
        return content

    # First, fix existing Mermaid blocks with semicolons
    mermaid_block_pattern = r'```mermaid\s*\n(.*?)```'

    def remove_semicolons_from_block(match):
        """Remove semicolons from Mermaid code blocks."""
        mermaid_content = match.group(1)
        # Remove semicolons at the end of lines
        fixed_content = re.sub(r';\s*$', '', mermaid_content, flags=re.MULTILINE)
        return f'```mermaid\n{fixed_content}```'

    content = re.sub(mermaid_block_pattern, remove_semicolons_from_block, content, flags=re.DOTALL)

    # Pattern for single-line Mermaid with semicolons (not already in code blocks)
    # This matches things like: graph TD A --> B; B --> C; C --> D;
    single_line_pattern = r'(?<!```mermaid\n)(?<!```)^(graph\s+(?:TD|LR|TB|RL|BT)|flowchart\s+(?:TD|LR|TB|RL|BT)|sequenceDiagram|classDiagram|stateDiagram|erDiagram|gantt|pie|journey)\s+(.+?;.+?)$'

    def fix_single_line_mermaid(match):
        """Convert single-line Mermaid to multi-line format."""
        diagram_type = match.group(1).strip()
        diagram_content = match.group(2).strip()

        # Split by semicolons and create multi-line format
        lines = []
        for line in diagram_content.split(';'):
            line = line.strip()
            if line:
                lines.append(f"    {line}")

        # Build proper Mermaid block
        result = ["\n```mermaid", diagram_type] + lines + ["```\n"]
        return '\n'.join(result)

    content = re.sub(single_line_pattern, fix_single_line_mermaid, content, flags=re.MULTILINE)

    # Pattern for unwrapped multi-line Mermaid code
    unwrapped_pattern = r'(?<!```mermaid\n)(?<!```)\n((?:graph|flowchart|sequenceDiagram|classDiagram|stateDiagram|erDiagram|gantt|pie|journey)\s+(?:TD|LR|TB|RL|BT)?\s*\n(?:(?!```)[^\n]*\n)+?)(?=\n|$)'

    def wrap_unwrapped_mermaid(match):
        """Wrap unwrapped Mermaid diagrams."""
        mermaid_content = match.group(1).strip()

        # Check if it looks like valid Mermaid (contains arrows or other indicators)
        if ('-->' in mermaid_content or '---' in mermaid_content or
            ':::' in mermaid_content or '|' in mermaid_content):
            # Remove any semicolons
            mermaid_content = re.sub(r';\s*$', '', mermaid_content, flags=re.MULTILINE)

            # Check if it's already wrapped (shouldn't be, but double-check)
            if not mermaid_content.startswith('```mermaid'):
                return f'\n```mermaid\n{mermaid_content}\n```\n'

        return match.group(0)

    content = re.sub(unwrapped_pattern, wrap_unwrapped_mermaid, content, flags=re.MULTILINE | re.DOTALL)

    return content


def validate_mermaid_syntax(content: str) -> list:
    """
    Validate Mermaid diagrams and return a list of potential issues.

    Args:
        content: Markdown content with Mermaid diagrams

    Returns:
        List of warning messages about potential Mermaid issues
    """
    warnings = []

    # Find all Mermaid blocks
    mermaid_blocks = re.findall(r'```mermaid\s*\n(.*?)```', content, flags=re.DOTALL)

    for i, block in enumerate(mermaid_blocks, 1):
        # Check for semicolons (common error)
        if ';' in block:
            warnings.append(f"Mermaid block {i}: Contains semicolons which may cause rendering issues")

        # Check if it's all on one line (common error)
        lines = [line.strip() for line in block.split('\n') if line.strip()]
        if len(lines) <= 2:  # Only diagram type and one line of content
            warnings.append(f"Mermaid block {i}: Diagram appears to be on a single line, may not render correctly")

        # Check for proper diagram type
        diagram_types = ['graph', 'flowchart', 'sequenceDiagram', 'classDiagram',
                        'stateDiagram', 'erDiagram', 'gantt', 'pie', 'journey']
        if not any(dtype in block for dtype in diagram_types):
            warnings.append(f"Mermaid block {i}: No valid diagram type found")

    return warnings

