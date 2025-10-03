---
name: Feature Request
about: Suggest a new feature for Orca
title: '[FEATURE] '
labels: 'enhancement, needs-triage'
assignees: ''
---

## 🚀 Feature Request

### **Feature Description**
<!-- A clear and concise description of what you want to add -->


### **Motivation / Use Case**
<!-- Why is this feature needed? What problem does it solve? -->


### **Proposed Solution**
<!-- How would you like this feature to work? -->


### **Alternative Solutions**
<!-- Have you considered other approaches? -->


### **Additional Context**
<!-- Add any other context, screenshots, or examples -->


---

## 📋 Archon Integration (For Maintainers)

### Archon Task Creation
When this issue is accepted, create an Archon task:

```bash
# Use mcp__archon__manage_task to create task
Project: [Orca Project ID]
Title: [Feature title]
Description: [From above]
Feature: [Feature category]
Priority: [1-10]
Status: todo
```

### Implementation Workflow
1. Create Archon task from this issue
2. Create feature branch: `feature/TASK-XXX-description`
3. Implement with TASK-XXX in commits
4. Create PR with TASK-XXX reference
5. Update Archon task status through workflow

### Task Breakdown
<!-- Maintainer: Break down into subtasks if needed -->
- [ ] Subtask 1
- [ ] Subtask 2
- [ ] Subtask 3

---

🤖 _Feature request template for Orca-Archon Hybrid workflow_
