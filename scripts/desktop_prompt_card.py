from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
import tkinter as tk
from tkinter import messagebox


REPO_ROOT = Path(__file__).resolve().parents[1]
PROMPTS_ROOT = REPO_ROOT / "Prompts"
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
        self._list_title = tk.StringVar(value="Recent Prompts")

        self._build_ui()
        self.refresh()

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
                self._row(self.recent_frame, rel.as_posix(), lambda p=path: self.open_path(p))

        self._status.set("Updated")
        self._reset_list_scroll()

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
            self._row(self.recent_frame, label, lambda p=prompt: self.open_path(p))

        self._status.set(f"{name}: {len(prompts)} prompts")
        self._reset_list_scroll()

    def _prompts_in_category(self, path: Path) -> list[Path]:
        if not path.exists():
            return []
        files = [item for item in path.glob("*.md") if not self._is_hidden_prompt(item)]
        files.sort(key=lambda item: item.stem.lower())
        return files

    def _recent_prompts(self) -> list[Path]:
        if not PROMPTS_ROOT.exists():
            return []
        files = [
            path
            for path in PROMPTS_ROOT.rglob("*.md")
            if not self._is_hidden_prompt(path)
        ]
        files.sort(key=lambda item: item.stat().st_mtime, reverse=True)
        return files[:8]

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
            messagebox.showinfo("Prompt Repository", "GitHub sync completed.")
        else:
            self._status.set("Sync failed")
            messagebox.showerror("Prompt Repository", (result.stderr or result.stdout).strip())

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
