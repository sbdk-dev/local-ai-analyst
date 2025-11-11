# Documentation Templates

Templates for creating consistent, high-quality documentation.

---

## Available Templates

### [getting-started-template.md](getting-started-template.md)
**Use for**: Step-by-step beginner guides
**Includes**:
- Prerequisites checklist
- Step-by-step instructions with verification
- Troubleshooting sections
- Clear next steps

**Example uses**:
- Installation guides
- First-time setup walkthroughs
- Tutorial-style content

---

### [concept-template.md](concept-template.md)
**Use for**: Explaining architectural concepts and principles
**Includes**:
- Overview and purpose
- Key concepts breakdown
- Architecture diagrams
- Real-world examples
- Benefits and trade-offs

**Example uses**:
- Explaining execution-first pattern
- Describing semantic layer architecture
- Statistical rigor principles

---

### [reference-template.md](reference-template.md)
**Use for**: API documentation and technical references
**Includes**:
- Complete specification tables
- Parameter documentation
- Error handling
- Usage examples
- Performance characteristics

**Example uses**:
- MCP tool documentation
- Query language reference
- Configuration options

---

## How to Use Templates

### 1. Copy the Template

```bash
cp docs/templates/getting-started-template.md docs/getting-started/my-new-guide.md
```

### 2. Fill in the Placeholders

Templates use `[placeholders]` for sections you need to customize:
- `[Document Title]` → Your document's title
- `[Target Audience]` → Who should read this
- `[X minutes]` → Estimated reading/completion time
- etc.

### 3. Follow the Structure

Keep the template structure but adapt content to your needs. The structure is designed for:
- Scannability (headers, bullets, tables)
- Progressive disclosure (simple → complex)
- Actionable content (examples, verification steps)

### 4. Add Cross-Links

At the end of each document, link to:
- Next logical document in learning path
- Related concepts
- Reference material

Example:
```markdown
## Next Steps

- [Related Guide](../user-guide/related.md)
- [Concept Deep-Dive](../concepts/concept.md)
- [API Reference](../reference/api.md)
```

---

## Template Standards

### Required Sections

**All documents must have**:
- Clear title
- Target audience statement
- Prerequisites (if applicable)
- Last updated date

**Getting Started documents must have**:
- Time to complete estimate
- Step-by-step instructions
- Verification steps
- Troubleshooting
- Next steps

**Concept documents must have**:
- Overview
- Key concepts explanation
- How it works
- Related concepts

**Reference documents must have**:
- Quick reference section
- Complete specification
- Examples by use case

### Code Example Standards

**Always include**:
```python
# Code example with inline comments
example_function(
    param="value"  # Explain parameters
)
```

**Expected Output**:
```
Show what users should see when they run this
```

**Explanation**: What this code does and why

### Link Standards

**Internal links** (within docs):
```markdown
[Link Text](../section/document.md)
```

**External links** (outside docs):
```markdown
[Link Text](https://external-url.com)
```

**Anchor links** (within same document):
```markdown
[Link Text](#section-heading)
```

### Formatting Standards

**Headings**:
- H1 (`#`) - Document title only
- H2 (`##`) - Major sections
- H3 (`###`) - Subsections
- H4 (`####`) - Minor subsections (use sparingly)

**Lists**:
- Use `-` for unordered lists
- Use `1.` for ordered lists (markdown auto-numbers)
- Indent with 2 spaces for nested lists

**Emphasis**:
- `**bold**` for emphasis
- `*italic*` for minor emphasis (use sparingly)
- `code` for technical terms, commands, filenames

**Code blocks**:
- Always specify language: ```python not just ```
- Include comments for clarity
- Keep examples runnable

**Tables**:
```markdown
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Value 1  | Value 2  | Value 3  |
```

---

## Validation Checklist

Before committing a new document, verify:

### Content Quality
- [ ] Title is clear and descriptive
- [ ] Target audience identified
- [ ] Prerequisites listed (if any)
- [ ] All sections from template filled in
- [ ] Code examples tested and working
- [ ] Expected outputs included
- [ ] Clear next steps provided

### Formatting
- [ ] Consistent heading hierarchy
- [ ] Code blocks have language specified
- [ ] Tables formatted correctly
- [ ] Lists use consistent style

### Links
- [ ] All internal links valid (use relative paths)
- [ ] External links working
- [ ] Cross-references to related content
- [ ] "Next steps" section includes relevant links

### Metadata
- [ ] Last updated date included
- [ ] Feedback link present (if applicable)
- [ ] Related topics listed

---

## Example: Using Getting Started Template

### Before (Template)
```markdown
# [Document Title]

**Target Audience**: [Who should read this]
**Prerequisites**: [What users should have/know before starting]
**Time to Complete**: [X minutes]

---

## Step 1: [First Major Step]
[Instructions]
```

### After (Completed)
```markdown
# Installing AI Analyst

**Target Audience**: Data analysts, new users
**Prerequisites**: Python 3.11+, pip installed
**Time to Complete**: 15 minutes

---

## Step 1: Install Dependencies

Install AI Analyst using pip:

```bash
pip install ai-analyst
```

**Expected Output**:
```
Successfully installed ai-analyst-1.0.0
```

### Verification
Check installation:
```bash
ai-analyst --version
```

Should show: `ai-analyst version 1.0.0`
```

---

## Creating New Templates

If you need a template for a new document type:

1. Review existing templates for patterns
2. Identify required sections for new type
3. Create template following standards above
4. Test template with sample content
5. Add to this README with description

**Example new template types**:
- Architecture diagram guide template
- Performance benchmark template
- Troubleshooting entry template
- API migration guide template

---

## Questions?

- [Contributing Guide](../../CONTRIBUTING.md)
- [Documentation Architecture](../../DOCUMENTATION_ARCHITECTURE.md)
- [Migration Guide](../../DOCUMENTATION_MIGRATION_GUIDE.md)

---

**Last Updated**: 2025-11-08
**Maintained by**: Documentation Engineer
