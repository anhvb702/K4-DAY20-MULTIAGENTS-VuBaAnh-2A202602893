"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
        {
            "name": "explorer",
            "description": (
                "Use when the task needs repository or data inspection before changes; "
                "read relevant files and report findings without editing anything."
            ),
            "system_prompt": (
                "You are a careful research assistant. Inspect the requested files or data, "
                "ground conclusions in evidence, and return a concise report. Do not modify files."
            ),
        },
        {
            "name": "implementer",
            "description": (
                "Use for a well-scoped code or data change that can be completed independently; "
                "make the change, run relevant checks, and report exactly what changed."
            ),
            "system_prompt": (
                "You are an implementation assistant. Follow the task requirements, make only "
                "the requested changes, run relevant tests or checks, and report their results."
            ),
        },
        {
            "name": "reviewer",
            "description": (
                "Use to independently review a proposed or completed change for correctness, "
                "missed requirements, and edge cases; report findings without editing files."
            ),
            "system_prompt": (
                "You are an independent reviewer. Check the work against the stated requirements "
                "and relevant edge cases. Report concrete findings with evidence; do not edit files."
            ),
        },
    ]
