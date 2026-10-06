"""GUIDE Phần 1 - Dựng tác tử (agent) bằng Deep Agents.   >>> SINH VIÊN CÀI ĐẶT make_backend VÀ build_agent <<<

Pseudo-code: guides/pseudocode/01_agent.md
Kiểm tra:    pytest tests/test_02_agent.py
"""
from pathlib import Path
import os
import shutil
import subprocess
import sys

from deepagents import create_deep_agent
from deepagents.backends import LocalShellBackend
from deepagents.backends.protocol import ExecuteResponse

from .model import make_model
from .subagents import get_subagents

# ---- CÓ SẴN, KHÔNG SỬA: system prompt dùng chung cho mọi sinh viên (để đường cơ sở so sánh được) ----
PATHS_NOTE = (
    "PATHS: every path is relative to the sandbox root and never starts with '/'. "
    "The task files are in the folder workspace/ (for example workspace/app.log). "
    "Use exactly this relative form both in the file tools and in the shell (execute); "
    "the shell starts in the sandbox root. "
)
BASE_PROMPT = (
    "You are an engineering assistant working in a sandbox. "
    + PATHS_NOTE
    + "Use the shell to run Python and tests. "
    "When you are done, reply with a short summary that mentions only files you really created or changed."
)
SKILLS_NOTE = (
    " Skills are in the folder skills/ (one sub-folder per skill with a SKILL.md). "
    "As your FIRST action, read the SKILL.md of every skill whose description could apply to the task, "
    "then follow them. Never modify skills/."
)
SUBAGENTS_NOTE = (
    " You have specialised subagents (see the description of the task tool). "
    "For anything beyond a trivial step, delegate to a suitable subagent and put ALL the task rules and file paths "
    "in the delegation message, because a subagent sees only what you send. "
    "Check what a subagent returns before you rely on it."
)
WINDOWS_NOTE = (
    " Use `python` (not `python3`) and only the Python standard library; "
    "do not use pandas or assume optional packages are installed. For multi-line Python, write a .py file "
    "and run `python path/to/file.py`; do not put compound statements in `python -c`."
)
# --------------------------------------------------------------------------------------------------


class _GitBashBackend(LocalShellBackend):
    def __init__(self, *args, bash: Path, **kwargs):
        super().__init__(*args, **kwargs)
        self._bash = bash

    def execute(self, command: str, *, timeout: int | None = None) -> ExecuteResponse:
        try:
            result = subprocess.run(
                [str(self._bash), "-lc", command], cwd=self.cwd, env=self._env,
                capture_output=True, stdin=subprocess.DEVNULL, text=True,
                timeout=timeout or self._default_timeout,
            )
        except subprocess.TimeoutExpired:
            return ExecuteResponse(output="Error: Command timed out.", exit_code=124, truncated=False)
        output = result.stdout
        if result.stderr:
            output += ("\n" if output else "") + "\n".join(
                f"[stderr] {line}" for line in result.stderr.strip().splitlines()
            )
        if result.returncode:
            output = f"{output.rstrip()}\n\nExit code: {result.returncode}"
        if len(output) > self._max_output_bytes:
            output = output[:self._max_output_bytes] + f"\n\n... Output truncated at {self._max_output_bytes} bytes."
            return ExecuteResponse(output=output, exit_code=result.returncode, truncated=True)
        return ExecuteResponse(output=output or "<no output>", exit_code=result.returncode, truncated=False)


def make_backend(sandbox: Path):
    """Tạo backend (môi trường thực thi) cho tác tử.

    Yêu cầu:
      - Thư mục gốc (root_dir) là `sandbox`; đường dẫn tương đối `workspace/...` và `skills/...`
        phải dùng được ở CẢ công cụ tệp lẫn shell (shell chạy với thư mục làm việc = `sandbox`).
      - Tác tử chạy được lệnh shell và gọi được `python` (cần đặt PATH).
      - KHÔNG chuyển biến môi trường của bạn vào shell của tác tử (khóa API không được lộ).
    """
    sandbox = Path(sandbox).resolve()
    path_entries = [str(Path(sys.executable).parent)]
    if os.name == "nt":
        git = shutil.which("git")
        if git:
            unix_tools = Path(git).resolve().parent.parent / "usr" / "bin"
            if unix_tools.is_dir():
                path_entries.append(str(unix_tools))
    else:
        path_entries.extend(("/usr/local/bin", "/usr/bin", "/bin"))
    env = {
        "PATH": os.pathsep.join(path_entries),
        "HOME": str(sandbox),
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    backend = LocalShellBackend
    options = {}
    if os.name == "nt":
        git = shutil.which("git")
        bash = Path(git).resolve().parent.parent / "bin" / "bash.exe" if git else None
        if bash and bash.is_file():
            backend = _GitBashBackend
            options["bash"] = bash
    return backend(
        root_dir=sandbox,
        virtual_mode=True,
        inherit_env=False,
        env=env,
        timeout=120,
        **options,
    )


def build_agent(sandbox: Path, mode: str = "single", use_skills: bool = False, model=None):
    """Tạo tác tử Deep Agents.

    Tham số:
      sandbox:    thư mục chứa `workspace/` (và `skills/` nếu có).
      mode:       "single"    -> tác tử mặc định (có subagent `general-purpose` sẵn của Deep Agents)
                  "subagents" -> thêm các subagent từ `get_subagents()` (nối PATHS_NOTE vào `system_prompt` của MỖI subagent,
                                 vì subagent không nhận BASE_PROMPT) và thêm SUBAGENTS_NOTE vào prompt chính
      use_skills: True -> nạp thư mục "/skills/" qua tham số `skills=` của create_deep_agent
                  và thêm SKILLS_NOTE vào prompt.
      model:      mô hình ngôn ngữ; None -> dùng `make_model()`.
    mode không hợp lệ -> ném ValueError.
    Trả về: đồ thị (graph) đã biên dịch, gọi bằng `.invoke({"messages": [...]})`.
    """
    if mode not in {"single", "subagents"}:
        raise ValueError(f"Unknown agent mode: {mode}")

    prompt = BASE_PROMPT + (WINDOWS_NOTE if os.name == "nt" else "")
    kwargs = {}
    if mode == "subagents":
        kwargs["subagents"] = [
            {**sub, "system_prompt": sub["system_prompt"] + " " + PATHS_NOTE + (WINDOWS_NOTE if os.name == "nt" else "")}
            for sub in get_subagents()
        ]
        prompt += SUBAGENTS_NOTE
    if use_skills:
        kwargs["skills"] = ["/skills/"]
        prompt += SKILLS_NOTE

    return create_deep_agent(
        model=model or make_model(),
        system_prompt=prompt,
        backend=make_backend(sandbox),
        **kwargs,
    )
