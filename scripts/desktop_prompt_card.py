from __future__ import annotations

import os
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import messagebox


REPO_ROOT = Path(__file__).resolve().parents[1]
PROMPTS_ROOT = REPO_ROOT / "Prompts"
REFRESH_MARKER = REPO_ROOT / ".prompt-card-refresh"
CATEGORIES = [
    "Favorites",
    "High-Frequency Workflows",
    "\U0001f9e9 \u89d2\u8272\u5361",
    "\U0001f4da \u4e13\u4e1a\u573a\u666f",
    "\U0001f9ea \u6d4b\u8bd5",
    "\U0001f4c4 \u6a21\u677f",
]


class PromptCard(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Prompt Repository")
        self.geometry("340x500+960+120")
        self.minsize(300, 420)
        self.configure(bg="#f7f7f4")
        self.attributes("-topmost", True)

        self._drag_start_x = 0
        self._drag_start_y = 0
        self._topmost = tk.BooleanVar(value=True)
        self._status = tk.StringVar(value="Ready")
        self._git_status = tk.StringVar(value="Git: checking...")
        self._list_title = tk.StringVar(value="Recent Prompts")
        self._search_query = tk.StringVar()
        self._last_refresh_marker = self._refresh_marker_stamp()
        self._selected_prompt: Path | None = None

        self._build_ui()
        self.refresh()
        self.update_git_status()
        self.after(3000, self._watch_refresh_marker)

    def _build_ui(self) -> None:
        header = tk.Frame(self, bg="#202124", padx=12, pady=10)
        header.pack(fill="x")
        header.bind("<ButtonPress-1>", self._start_drag)
        header.bind("<B1-Motion>", self._drag)

        title = tk.Label(
            header,
            text="Prompt Repository",
            fg="#ffffff",
            bg="#202124",
            font=("Segoe UI", 13, "bold"),
            anchor="w",
        )
        title.pack(side="left", fill="x", expand=True)
        title.bind("<ButtonPress-1>", self._start_drag)
        title.bind("<B1-Motion>", self._drag)

        topmost = tk.Checkbutton(
            header,
            text="Top",
            variable=self._topmost,
            command=self._toggle_topmost,
            fg="#ffffff",
            bg="#202124",
            activebackground="#202124",
            activeforeground="#ffffff",
            selectcolor="#202124",
        )
        topmost.pack(side="right")

        body = tk.Frame(self, bg="#f7f7f4", padx=12, pady=10)
        body.pack(fill="both", expand=True)

        controls = tk.Frame(body, bg="#f7f7f4")
        controls.pack(fill="x", pady=(0, 10))

        self._button(controls, "Refresh", self.refresh).pack(side="left", padx=(0, 6))
        self._button(controls, "Home", self.refresh).pack(side="left", padx=(0, 6))
        self._button(controls, "Open", self.open_repo).pack(side="left", padx=(0, 6))
        self._button(controls, "Sync", self.sync_repo).pack(side="right")

        search = tk.Frame(body, bg="#f7f7f4")
        search.pack(fill="x", pady=(0, 10))
        search_entry = tk.Entry(
            search,
            textvariable=self._search_query,
            relief="flat",
            bg="#ffffff",
            fg="#222222",
            insertbackground="#222222",
            font=("Segoe UI", 9),
        )
        search_entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 6))
        search_entry.bind("<Return>", lambda _event: self.search_prompts())
        self._button(search, "Search", self.search_prompts).pack(side="left", padx=(0, 6))
        self._button(search, "Clear", self.clear_search).pack(side="left")

        tk.Label(
            body,
            text="Directories",
            bg="#f7f7f4",
            fg="#2b2b2b",
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        ).pack(fill="x")

        self.categories_frame = tk.Frame(body, bg="#f7f7f4")
        self.categories_frame.pack(fill="x", pady=(4, 12))

        self.list_title_label = tk.Label(
            body,
            textvariable=self._list_title,
            bg="#f7f7f4",
            fg="#2b2b2b",
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        )
        self.list_title_label.pack(fill="x")

        list_container = tk.Frame(body, bg="#f7f7f4")
        list_container.pack(fill="both", expand=True, pady=(4, 8))

        self.list_canvas = tk.Canvas(
            list_container,
            bg="#f7f7f4",
            highlightthickness=0,
            bd=0,
        )
        self.list_scrollbar = tk.Scrollbar(
            list_container,
            orient="vertical",
            command=self.list_canvas.yview,
            width=18,
        )
        self.recent_frame = tk.Frame(self.list_canvas, bg="#f7f7f4")
        self.recent_window = self.list_canvas.create_window(
            (0, 0),
            window=self.recent_frame,
            anchor="nw",
        )
        self.list_canvas.configure(yscrollcommand=self.list_scrollbar.set)
        self.list_canvas.pack(side="left", fill="both", expand=True)
        self.list_scrollbar.pack(side="right", fill="y")
        self.recent_frame.bind("<Configure>", self._update_scroll_region)
        self.list_canvas.bind("<Configure>", self._resize_scroll_window)
        self.list_canvas.bind("<Enter>", self._bind_mousewheel)
        self.list_canvas.bind("<Leave>", self._unbind_mousewheel)

        git_status = tk.Label(
            self,
            textvariable=self._git_status,
            bg="#f7f7f4",
            fg="#555555",
            anchor="w",
            padx=10,
            pady=4,
            font=("Segoe UI", 9),
        )
        git_status.pack(fill="x")

        status = tk.Label(
            self,
            textvariable=self._status,
            bg="#ecebe6",
            fg="#555555",
            anchor="w",
            padx=10,
            pady=5,
            font=("Segoe UI", 9),
        )
        status.pack(fill="x")

    def _button(self, parent: tk.Widget, text: str, command) -> tk.Button:
        return tk.Button(
            parent,
            text=text,
            command=command,
            relief="flat",
            bg="#ffffff",
            fg="#222222",
            activebackground="#e7eefc",
            activeforeground="#111111",
            padx=10,
            pady=5,
            font=("Segoe UI", 9),
            cursor="hand2",
        )

    def refresh(self) -> None:
        self._clear(self.categories_frame)
        self._clear(self.recent_frame)

        for name in CATEGORIES:
            path = PROMPTS_ROOT / name
            count = len(list(path.glob("*.md"))) if path.exists() else 0
            label = f"{name}  ({count})"
            self._row(self.categories_frame, label, lambda p=path, n=name: self.show_category(n, p))

        self._list_title.set("Recent Prompts")
        recent = self._recent_prompts()
        if not recent:
            self._empty_row("No prompts found.")
        else:
            for path in recent:
                rel = path.relative_to(PROMPTS_ROOT)
                self._prompt_row(self.recent_frame, rel.as_posix(), path)

        self._status.set("Updated")
        self._reset_list_scroll()
        self.update_git_status()
        self._last_refresh_marker = self._refresh_marker_stamp()

    def _row(self, parent: tk.Widget, text: str, command) -> None:
        button = tk.Button(
            parent,
            text=text,
            command=command,
            relief="flat",
            bg="#fdfdfb",
            fg="#202124",
            activebackground="#e8f0fe",
            activeforeground="#111111",
            anchor="w",
            padx=10,
            pady=7,
            font=("Segoe UI", 9),
            cursor="hand2",
            wraplength=285,
            justify="left",
        )
        button.pack(fill="x", pady=2)

    def show_category(self, name: str, path: Path) -> None:
        self._clear(self.recent_frame)
        self._list_title.set(name)

        prompts = self._prompts_in_category(path)
        if not prompts:
            self._empty_row("No prompts in this directory.")
            self._status.set(f"{name}: 0 prompts")
            return

        for prompt in prompts:
            label = prompt.stem
            self._prompt_row(self.recent_frame, label, prompt)

        self._status.set(f"{name}: {len(prompts)} prompts")
        self._reset_list_scroll()

    def search_prompts(self) -> None:
        query = self._search_query.get().strip()
        self._clear(self.recent_frame)
        if not query:
            self.refresh()
            return

        matches = self._search_matches(query)
        self._list_title.set(f"Search: {query}")
        if not matches:
            self._empty_row("No matching prompts.")
            self._status.set("Search: 0 matches")
            self._reset_list_scroll()
            return

        for path in matches:
            rel = path.relative_to(PROMPTS_ROOT)
            self._prompt_row(self.recent_frame, rel.as_posix(), path)

        self._status.set(f"Search: {len(matches)} matches")
        self._reset_list_scroll()

    def clear_search(self) -> None:
        self._search_query.set("")
        self.refresh()

    def _search_matches(self, query: str) -> list[Path]:
        needle = query.casefold()
        matches: list[Path] = []
        for path in self._all_prompt_files():
            haystack = path.stem.casefold()
            try:
                haystack += "\n" + path.read_text(encoding="utf-8", errors="ignore").casefold()
            except OSError:
                pass
            if needle in haystack:
                matches.append(path)
        matches.sort(key=lambda item: item.stat().st_mtime, reverse=True)
        return matches

    def _prompts_in_category(self, path: Path) -> list[Path]:
        if not path.exists():
            return []
        files = [item for item in path.glob("*.md") if not self._is_hidden_prompt(item)]
        files.sort(key=lambda item: item.stem.lower())
        return files

    def _recent_prompts(self) -> list[Path]:
        files = self._all_prompt_files()
        files.sort(key=lambda item: item.stat().st_mtime, reverse=True)
        return files[:8]

    def _all_prompt_files(self) -> list[Path]:
        if not PROMPTS_ROOT.exists():
            return []
        return [
            path
            for path in PROMPTS_ROOT.rglob("*.md")
            if not self._is_hidden_prompt(path)
        ]

    def _is_hidden_prompt(self, path: Path) -> bool:
        skip = {"README.md", "Prompt_Template.md", "Role_Template.md", "\u6536\u85cf-\u6a21\u677f.md"}
        relative = path.relative_to(PROMPTS_ROOT)
        return path.name in skip or "\u6a21\u677f" in str(relative)

    def _empty_row(self, text: str) -> None:
        tk.Label(
            self.recent_frame,
            text=text,
            bg="#f7f7f4",
            fg="#777777",
            anchor="w",
        ).pack(fill="x", pady=2)

    def _prompt_row(self, parent: tk.Widget, text: str, path: Path) -> None:
        label = tk.Label(
            parent,
            text=text,
            bg="#fdfdfb",
            fg="#202124",
            anchor="w",
            padx=10,
            pady=7,
            font=("Segoe UI", 9),
            cursor="hand2",
            wraplength=285,
            justify="left",
        )
        label.pack(fill="x", pady=2)
        label.bind("<Button-1>", lambda _event, widget=label, p=path: self.select_prompt(widget, p))
        label.bind("<Double-Button-1>", lambda _event, p=path: self.fill_codex_input(p))

    def select_prompt(self, widget: tk.Label, path: Path) -> None:
        self._selected_prompt = path
        for child in self.recent_frame.winfo_children():
            if isinstance(child, tk.Label):
                child.configure(bg="#fdfdfb")
        widget.configure(bg="#e8f0fe")
        self._status.set(f"Selected: {path.stem}")

    def fill_codex_input(self, path: Path) -> None:
        text = self._prompt_text(path)
        if not text.strip():
            self._status.set("Prompt is empty")
            messagebox.showwarning("Prompt Repository", f"No prompt text found:\n{path}")
            return

        self.clipboard_clear()
        self.clipboard_append(text)
        self.update_idletasks()
        self._status.set(f"Copied prompt: {path.stem}")

    def _prompt_text(self, path: Path) -> str:
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return ""

        body = self._strip_frontmatter(content)
        section = self._section_after_heading(body, "Prompt 正文")
        if section.strip():
            return section.strip()

        return self._prompt_body_only(body).strip()

    @staticmethod
    def _strip_frontmatter(content: str) -> str:
        lines = content.splitlines()
        if len(lines) < 3 or lines[0].strip() != "---":
            return content
        for index in range(1, len(lines)):
            if lines[index].strip() == "---":
                return "\n".join(lines[index + 1 :]).strip()
        return content

    @staticmethod
    def _section_after_heading(content: str, heading: str) -> str:
        lines = content.splitlines()
        capture = False
        result: list[str] = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("## "):
                if capture:
                    break
                capture = stripped == f"## {heading}"
                continue
            if capture:
                result.append(line)
        return "\n".join(result)

    @staticmethod
    def _prompt_body_only(content: str) -> str:
        stop_headings = {
            "使用经验",
            "优化记录",
            "维护记录",
            "测试记录",
            "说明",
            "备注",
            "元数据",
        }
        lines = content.splitlines()
        result: list[str] = []
        seen_body = False

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("# "):
                continue
            if stripped.startswith("## "):
                heading = stripped.removeprefix("## ").strip()
                if heading in stop_headings:
                    break
                seen_body = True
                result.append(line)
                continue
            if stripped or seen_body:
                result.append(line)

        return "\n".join(result)

    def _update_scroll_region(self, _event: tk.Event | None = None) -> None:
        self.list_canvas.configure(scrollregion=self.list_canvas.bbox("all"))

    def _resize_scroll_window(self, event: tk.Event) -> None:
        self.list_canvas.itemconfigure(self.recent_window, width=event.width)

    def _reset_list_scroll(self) -> None:
        self.update_idletasks()
        self.list_canvas.yview_moveto(0)

    def _bind_mousewheel(self, _event: tk.Event) -> None:
        self.list_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self, _event: tk.Event) -> None:
        self.list_canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event: tk.Event) -> None:
        self.list_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def open_repo(self) -> None:
        self.open_path(REPO_ROOT)

    def open_path(self, path: Path) -> None:
        if not path.exists():
            messagebox.showwarning("Prompt Repository", f"Path not found:\n{path}")
            return
        os.startfile(str(path))

    def sync_repo(self) -> None:
        script = REPO_ROOT / "scripts" / "sync_github.ps1"
        if not script.exists():
            messagebox.showwarning("Prompt Repository", f"Sync script not found:\n{script}")
            return
        self._status.set("Syncing...")
        self.update_idletasks()
        command = [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(script),
        ]
        result = subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True)
        if result.returncode == 0:
            self._status.set("Synced")
            self.update_git_status()
            messagebox.showinfo("Prompt Repository", "GitHub sync completed.")
        else:
            self._status.set("Sync failed")
            self.update_git_status()
            messagebox.showerror("Prompt Repository", (result.stderr or result.stdout).strip())

    def update_git_status(self) -> None:
        git = self._git_command()
        if not git:
            self._git_status.set("Git: unavailable")
            return

        try:
            status = subprocess.run(
                [git, "status", "--porcelain"],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                timeout=8,
            )
            if status.returncode != 0:
                self._git_status.set("Git: status failed")
                return

            relation = subprocess.run(
                [git, "rev-list", "--left-right", "--count", "origin/main...HEAD"],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                timeout=8,
            )
            dirty = bool(status.stdout.strip())
            ahead = 0
            behind = 0
            if relation.returncode == 0:
                parts = relation.stdout.strip().split()
                if len(parts) == 2:
                    behind = int(parts[0])
                    ahead = int(parts[1])

            pieces = []
            if dirty:
                pieces.append("local changes")
            if ahead:
                pieces.append(f"{ahead} unpushed")
            if behind:
                pieces.append(f"{behind} behind")
            if not pieces:
                pieces.append("synced")
            self._git_status.set("Git: " + ", ".join(pieces))
        except (OSError, subprocess.SubprocessError, ValueError):
            self._git_status.set("Git: status unavailable")

    @staticmethod
    def _git_command() -> str | None:
        candidates = [
            "git",
            r"C:\Program Files\Git\cmd\git.exe",
            r"C:\Program Files\Git\bin\git.exe",
        ]
        for candidate in candidates:
            try:
                result = subprocess.run(
                    [candidate, "--version"],
                    text=True,
                    capture_output=True,
                    timeout=5,
                )
            except OSError:
                continue
            if result.returncode == 0:
                return candidate
        return None

    def _watch_refresh_marker(self) -> None:
        stamp = self._refresh_marker_stamp()
        if stamp > self._last_refresh_marker:
            self._last_refresh_marker = stamp
            self.refresh()
            self._status.set("Prompt repository updated")
        self.after(3000, self._watch_refresh_marker)

    @staticmethod
    def _refresh_marker_stamp() -> float:
        try:
            return REFRESH_MARKER.stat().st_mtime
        except OSError:
            return 0.0

    def _toggle_topmost(self) -> None:
        self.attributes("-topmost", self._topmost.get())

    def _start_drag(self, event: tk.Event) -> None:
        self._drag_start_x = event.x
        self._drag_start_y = event.y

    def _drag(self, event: tk.Event) -> None:
        x = self.winfo_pointerx() - self._drag_start_x
        y = self.winfo_pointery() - self._drag_start_y
        self.geometry(f"+{x}+{y}")

    @staticmethod
    def _clear(frame: tk.Widget) -> None:
        for child in frame.winfo_children():
            child.destroy()


def main() -> int:
    app = PromptCard()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
