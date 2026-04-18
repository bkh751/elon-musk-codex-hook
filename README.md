### Usage

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 .codex/hooks/inject_5step.py",
            "statusMessage":"inject"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 .codex/hooks/loop_5step.py",
            "statusMessage":"loop"
          }
        ]
      }
    ]
  }
}
```