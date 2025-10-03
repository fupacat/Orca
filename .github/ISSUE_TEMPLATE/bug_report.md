---
name: Bug Report
about: Report a bug in Orca
title: '[BUG] '
labels: 'bug, needs-triage'
assignees: ''
---

## 🐛 Bug Report

### **Describe the Bug**
<!-- A clear and concise description of what the bug is -->


### **To Reproduce**
Steps to reproduce the behavior:
1.
2.
3.
4.

### **Expected Behavior**
<!-- What you expected to happen -->


### **Actual Behavior**
<!-- What actually happened -->


### **Screenshots / Logs**
<!-- If applicable, add screenshots or error logs -->
```
Paste error messages or logs here
```

---

## 🔍 Environment

**Orca Version:**
<!-- Run: git describe --tags or git rev-parse --short HEAD -->

**Operating System:**
<!-- e.g., Windows 11, macOS 14, Ubuntu 22.04 -->

**Python Version:**
<!-- Run: python --version -->

**Shell:**
<!-- e.g., Bash, Zsh, PowerShell -->

**MCP Servers:**
- [ ] Archon MCP (version/status):
- [ ] Serena MCP (version/status):

---

## 📋 Additional Context

### **Related Components**
<!-- Check all that apply -->
- [ ] Workflow orchestration
- [ ] Agent execution
- [ ] MCP integration (Archon/Serena)
- [ ] Slash commands
- [ ] Testing infrastructure
- [ ] Documentation
- [ ] Other: ___________

### **Workaround**
<!-- Do you have a workaround? -->


### **Impact**
<!-- How does this bug affect you? -->
- [ ] Blocks work completely
- [ ] Major inconvenience
- [ ] Minor issue
- [ ] Cosmetic

---

## 📋 Archon Integration (For Maintainers)

### Archon Task Creation
When bug is confirmed, create an Archon task:

```bash
# Use mcp__archon__manage_task to create task
Project: [Orca Project ID]
Title: Fix: [Bug title]
Description: [From above]
Feature: bugfix
Priority: [Based on severity]
Status: todo
```

### Fix Workflow
1. Create Archon task from this issue
2. Create fix branch: `fix/TASK-XXX-description`
3. Implement fix with TASK-XXX in commits
4. Add regression tests
5. Create PR with TASK-XXX reference
6. Update Archon task status through workflow

### Root Cause Analysis (Post-fix)
<!-- Document root cause after investigation -->
**Cause:**

**Fix:**

**Prevention:**

---

🤖 _Bug report template for Orca-Archon Hybrid workflow_
