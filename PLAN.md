# Bash Tool-Calling Dataset Plan

## Overview
Create a 50K example dataset to train an 8B parameter LLM (via Unsloth) to perform multi-turn bash tool calling.

**Goal**: User requests an action → LLM performs multi-turn tool calls → Task completed

---

## 1. Project Structure

```
TrainingdataBash/
├── PLAN.md                     # This file
├── schema/
│   └── tool_call_schema.json   # JSON schema definition
├── data/
│   ├── raw/                    # Generated raw examples by category
│   │   ├── file_operations/
│   │   ├── git_commands/
│   │   ├── text_processing/
│   │   └── ...
│   ├── processed/
│   │   └── train_dataset.jsonl # Final merged dataset
│   └── validation/
│       └── val_dataset.jsonl   # Validation split (~5%)
├── scripts/
│   ├── generate_examples.py    # Example generation script
│   ├── validate_schema.py      # Schema validation
│   └── merge_dataset.py        # Merge all categories
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_generate_dataset.ipynb
│   └── 03_unsloth_training.ipynb
├── configs/
│   └── generation_config.yaml  # Generation parameters
└── README.md
```

---

## 2. Dataset Format (Unsloth/ChatML Compatible)

Each example is a multi-turn conversation in JSON format:

```json
{
  "id": "example_00001",
  "conversations": [
    {
      "role": "system",
      "content": "You are a helpful assistant with access to a bash tool. Use it to help users accomplish tasks on their Linux system."
    },
    {
      "role": "user",
      "content": "Find all Python files in the current directory that were modified in the last 7 days"
    },
    {
      "role": "assistant",
      "content": null,
      "tool_calls": [
        {
          "id": "call_001",
          "type": "function",
          "function": {
            "name": "bash",
            "arguments": "{\"command\": \"find . -name '*.py' -mtime -7 -type f\"}"
          }
        }
      ]
    },
    {
      "role": "tool",
      "tool_call_id": "call_001",
      "content": "./src/main.py\n./tests/test_utils.py\n./scripts/deploy.py"
    },
    {
      "role": "assistant",
      "content": "I found 3 Python files modified in the last 7 days:\n\n1. `./src/main.py`\n2. `./tests/test_utils.py`\n3. `./scripts/deploy.py`\n\nWould you like me to show more details about any of these files?"
    }
  ],
  "metadata": {
    "category": "file_operations",
    "commands_used": ["find"],
    "difficulty": "medium",
    "turns": 3
  }
}
```

---

## 3. The 100 Bash Commands (by Category)

### Category 1: File Operations (20 commands)
| # | Command | Description |
|---|---------|-------------|
| 1 | ls | List directory contents |
| 2 | cd | Change directory |
| 3 | pwd | Print working directory |
| 4 | cp | Copy files/directories |
| 5 | mv | Move/rename files |
| 6 | rm | Remove files/directories |
| 7 | mkdir | Create directories |
| 8 | rmdir | Remove empty directories |
| 9 | touch | Create empty file/update timestamp |
| 10 | find | Search for files |
| 11 | locate | Find files by name (fast) |
| 12 | ln | Create links |
| 13 | stat | Display file status |
| 14 | file | Determine file type |
| 15 | du | Disk usage |
| 16 | df | Disk free space |
| 17 | tree | Directory tree view |
| 18 | basename | Strip directory from filename |
| 19 | dirname | Strip filename from path |
| 20 | realpath | Resolve absolute path |

### Category 2: Text Processing (15 commands)
| # | Command | Description |
|---|---------|-------------|
| 21 | cat | Concatenate/display files |
| 22 | head | Show first lines |
| 23 | tail | Show last lines |
| 24 | grep | Search text patterns |
| 25 | sed | Stream editor |
| 26 | awk | Pattern scanning/processing |
| 27 | cut | Remove sections from lines |
| 28 | sort | Sort lines |
| 29 | uniq | Report/omit repeated lines |
| 30 | wc | Word/line/char count |
| 31 | diff | Compare files |
| 32 | tr | Translate characters |
| 33 | tee | Read stdin, write to stdout and files |
| 34 | less | View file contents (pager) |
| 35 | more | View file contents (pager) |

### Category 3: File Permissions & Ownership (5 commands)
| # | Command | Description |
|---|---------|-------------|
| 36 | chmod | Change file permissions |
| 37 | chown | Change file owner |
| 38 | chgrp | Change file group |
| 39 | umask | Set default permissions |
| 40 | id | Print user/group IDs |

### Category 4: Process Management (10 commands)
| # | Command | Description |
|---|---------|-------------|
| 41 | ps | Report process status |
| 42 | top | Dynamic process viewer |
| 43 | htop | Interactive process viewer |
| 44 | kill | Send signal to process |
| 45 | killall | Kill processes by name |
| 46 | pkill | Kill processes by pattern |
| 47 | pgrep | Find processes by pattern |
| 48 | bg | Background a process |
| 49 | fg | Foreground a process |
| 50 | nohup | Run immune to hangups |

### Category 5: System Information (10 commands)
| # | Command | Description |
|---|---------|-------------|
| 51 | uname | System information |
| 52 | hostname | Show/set hostname |
| 53 | uptime | System uptime |
| 54 | whoami | Current username |
| 55 | who | Who is logged in |
| 56 | w | Who and what they're doing |
| 57 | date | Show/set date and time |
| 58 | cal | Display calendar |
| 59 | free | Memory usage |
| 60 | lscpu | CPU information |

### Category 6: Network (12 commands)
| # | Command | Description |
|---|---------|-------------|
| 61 | curl | Transfer data from URLs |
| 62 | wget | Download files |
| 63 | ssh | Secure shell |
| 64 | scp | Secure copy |
| 65 | rsync | Remote sync |
| 66 | ping | Test network connectivity |
| 67 | netstat | Network statistics |
| 68 | ss | Socket statistics |
| 69 | ifconfig | Network interface config |
| 70 | ip | IP routing/devices |
| 71 | host | DNS lookup |
| 72 | dig | DNS lookup (detailed) |

### Category 7: Archive & Compression (6 commands)
| # | Command | Description |
|---|---------|-------------|
| 73 | tar | Archive files |
| 74 | gzip | Compress files |
| 75 | gunzip | Decompress files |
| 76 | zip | Create zip archives |
| 77 | unzip | Extract zip archives |
| 78 | xz | Compress with xz |

### Category 8: Package Management (6 commands)
| # | Command | Description |
|---|---------|-------------|
| 79 | apt | Debian package manager |
| 80 | apt-get | Debian package manager (classic) |
| 81 | dpkg | Debian package tool |
| 82 | pip | Python package manager |
| 83 | npm | Node.js package manager |
| 84 | snap | Snap package manager |

### Category 9: Git Version Control (8 commands)
| # | Command | Description |
|---|---------|-------------|
| 85 | git init | Initialize repository |
| 86 | git clone | Clone repository |
| 87 | git add | Stage changes |
| 88 | git commit | Commit changes |
| 89 | git push | Push to remote |
| 90 | git pull | Pull from remote |
| 91 | git status | Show status |
| 92 | git log | Show commit history |

### Category 10: User & Environment (8 commands)
| # | Command | Description |
|---|---------|-------------|
| 93 | echo | Print text |
| 94 | env | Environment variables |
| 95 | export | Set environment variable |
| 96 | source | Execute script in current shell |
| 97 | alias | Create command alias |
| 98 | which | Locate command |
| 99 | whereis | Locate binary/source/man |
| 100 | history | Command history |

---

## 4. Task Scenario Categories

To ensure diversity, we generate examples across these scenario types:

### Simple Tasks (Single Command) - 15K examples
- Direct command execution
- Basic flag usage
- Simple queries

### Compound Tasks (2-3 Commands) - 20K examples
- Piped commands
- Sequential operations
- Find and act patterns

### Complex Tasks (4+ Commands) - 10K examples
- Multi-step workflows
- Error recovery scenarios
- Conditional operations

### Error Handling Scenarios - 5K examples
- Permission denied → fix with sudo/chmod
- File not found → search/create
- Command failed → alternative approach

---

## 5. Example Distribution (50K Total)

| Category | Examples | Percentage |
|----------|----------|------------|
| File Operations | 10,000 | 20% |
| Text Processing | 8,000 | 16% |
| Git Operations | 6,000 | 12% |
| System Info & Process | 5,000 | 10% |
| Network Operations | 5,000 | 10% |
| Archive/Compression | 4,000 | 8% |
| Package Management | 4,000 | 8% |
| Permissions/Ownership | 3,000 | 6% |
| User/Environment | 3,000 | 6% |
| Mixed/Complex Tasks | 2,000 | 4% |

---

## 6. Generation Strategy

### Phase 1: Template Creation
- Create 500 base templates per category
- Each template has variables for customization
- Templates cover different difficulty levels

### Phase 2: Variation Generation
- Expand templates with different:
  - File names, paths, patterns
  - Flag combinations
  - Error scenarios
  - Output formats

### Phase 3: Multi-turn Expansion
- Add follow-up questions
- Include clarifications
- Error recovery turns

### Phase 4: Realistic Outputs
- Generate realistic command outputs
- Include common error messages
- Vary output lengths

---

## 7. Quality Assurance

1. **Schema Validation**: All examples pass JSON schema
2. **Command Validity**: All bash commands are syntactically correct
3. **Conversation Flow**: Natural dialogue progression
4. **Diversity Check**: No more than 1% duplicate patterns
5. **Balance Check**: Even distribution across categories

---

## 8. Unsloth Training Configuration

```python
# Recommended for 8B model
model_config = {
    "model_name": "unsloth/llama-3-8b-bnb-4bit",  # or similar
    "max_seq_length": 4096,  # Multi-turn needs longer context
    "load_in_4bit": True,
    "dtype": None,  # Auto-detect
}

training_config = {
    "per_device_train_batch_size": 2,
    "gradient_accumulation_steps": 4,
    "warmup_steps": 100,
    "num_train_epochs": 3,
    "learning_rate": 2e-4,
    "fp16": True,
    "logging_steps": 10,
    "output_dir": "outputs",
    "optim": "adamw_8bit",
}

lora_config = {
    "r": 16,
    "lora_alpha": 16,
    "lora_dropout": 0,
    "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj",
                       "gate_proj", "up_proj", "down_proj"],
}
```

---

## 9. Notebook Structure

### Notebook 1: Data Exploration (`01_data_exploration.ipynb`)
- Load and inspect generated data
- Visualize distributions
- Check quality metrics

### Notebook 2: Dataset Generation (`02_generate_dataset.ipynb`)
- Run generation scripts
- Validate outputs
- Merge into final dataset

### Notebook 3: Unsloth Training (`03_unsloth_training.ipynb`)
- Load model with Unsloth
- Prepare dataset
- Fine-tune with LoRA
- Evaluate and save

---

## 10. Timeline & Milestones

1. **Schema & Structure Setup** - Define all schemas and create directory structure
2. **Template Creation** - Create base templates for all categories
3. **Generation Scripts** - Build automation for example generation
4. **Generate Dataset** - Run generation to create 50K examples
5. **Quality Assurance** - Validate and clean dataset
6. **Training Notebook** - Set up Unsloth training pipeline
7. **Training & Evaluation** - Fine-tune and test the model

---

## Next Steps

1. Create the directory structure
2. Implement the JSON schema
3. Build generation scripts
4. Start template creation for each category
