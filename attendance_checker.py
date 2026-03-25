"""
Attendance Checker — A Tkinter app for tracking college attendance,
managing timetables, and calculating 75% criteria compliance.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import math
from datetime import datetime, date, timedelta

# ─── Paths ─────────────────────────────────────────────────────────────
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")

# ─── Color Palette ─────────────────────────────────────────────────────
BG_DARK       = "#1a1b2e"
BG_CARD       = "#242640"
BG_INPUT      = "#2e3050"
BG_HOVER      = "#353760"
ACCENT        = "#6c63ff"
ACCENT_HOVER  = "#7f78ff"
GREEN         = "#2ecc71"
GREEN_DIM     = "#1a7a42"
RED           = "#e74c3c"
RED_DIM       = "#8b2e26"
YELLOW        = "#f1c40f"
TEXT_PRIMARY   = "#e8e8f0"
TEXT_SECONDARY = "#9a9ab8"
TEXT_DARK      = "#5a5a78"
BORDER        = "#3a3c5e"

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]


# ═══════════════════════════════════════════════════════════════════════
#  Data Layer (Multi-Profile)
# ═══════════════════════════════════════════════════════════════════════
def default_profile():
    return {
        "subjects": [],
        "timetable": {d: {} for d in DAYS},
        "semester_end": "",
        "attendance": {}
    }


def default_store():
    return {
        "active_profile": "Student 1",
        "profiles": {
            "Student 1": default_profile()
        }
    }


def load_store():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
            # Migrate legacy single-profile format
            if "profiles" not in data:
                store = default_store()
                name = "Student 1"
                p = default_profile()
                p.update({k: data[k] for k in p if k in data})
                store["profiles"][name] = p
                return store
            return data
        except Exception:
            return default_store()
    return default_store()


def save_store(store):
    with open(DATA_FILE, "w") as f:
        json.dump(store, f, indent=2)


# ═══════════════════════════════════════════════════════════════════════
#  Main Application
# ═══════════════════════════════════════════════════════════════════════
class AttendanceApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Attendance Checker")
        self.state("normal")
        self.minsize(800, 600)
        self.configure(bg=BG_DARK)

        self.store = load_store()
        self.data = self.store["profiles"][self.store["active_profile"]]
        self._build_styles()
        self._build_ui()

    # ── Styles ─────────────────────────────────────────────────────────
    def _build_styles(self):
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        # Notebook
        self.style.configure("TNotebook", background=BG_DARK, borderwidth=0)
        self.style.configure("TNotebook.Tab",
                             background=BG_CARD, foreground=TEXT_SECONDARY,
                             padding=[18, 10], font=("Segoe UI Semibold", 11))
        self.style.map("TNotebook.Tab",
                       background=[("selected", ACCENT)],
                       foreground=[("selected", "#ffffff")])

        # Frames
        self.style.configure("Card.TFrame", background=BG_CARD)
        self.style.configure("Dark.TFrame", background=BG_DARK)

        # Labels
        self.style.configure("TLabel", background=BG_CARD,
                             foreground=TEXT_PRIMARY, font=("Segoe UI", 11))
        self.style.configure("Title.TLabel", background=BG_DARK,
                             foreground=TEXT_PRIMARY, font=("Segoe UI Bold", 20))
        self.style.configure("Subtitle.TLabel", background=BG_CARD,
                             foreground=TEXT_SECONDARY, font=("Segoe UI", 10))
        self.style.configure("Heading.TLabel", background=BG_CARD,
                             foreground=TEXT_PRIMARY, font=("Segoe UI Semibold", 13))
        self.style.configure("Green.TLabel", background=BG_CARD,
                             foreground=GREEN, font=("Segoe UI Bold", 13))
        self.style.configure("Red.TLabel", background=BG_CARD,
                             foreground=RED, font=("Segoe UI Bold", 13))
        self.style.configure("Yellow.TLabel", background=BG_CARD,
                             foreground=YELLOW, font=("Segoe UI Bold", 13))
        self.style.configure("BigStat.TLabel", background=BG_CARD,
                             foreground=ACCENT, font=("Segoe UI Bold", 28))
        self.style.configure("StatDesc.TLabel", background=BG_CARD,
                             foreground=TEXT_SECONDARY, font=("Segoe UI", 10))

        # Buttons
        self.style.configure("Accent.TButton",
                             background=ACCENT, foreground="#ffffff",
                             font=("Segoe UI Semibold", 11), padding=[16, 8])
        self.style.map("Accent.TButton",
                       background=[("active", ACCENT_HOVER)])

        self.style.configure("Green.TButton",
                             background=GREEN, foreground="#ffffff",
                             font=("Segoe UI Semibold", 10), padding=[12, 6])
        self.style.map("Green.TButton",
                       background=[("active", GREEN_DIM)])

        self.style.configure("Red.TButton",
                             background=RED, foreground="#ffffff",
                             font=("Segoe UI Semibold", 10), padding=[12, 6])
        self.style.map("Red.TButton",
                       background=[("active", RED_DIM)])

        self.style.configure("Small.TButton",
                             background=BG_INPUT, foreground=TEXT_PRIMARY,
                             font=("Segoe UI", 10), padding=[8, 4])
        self.style.map("Small.TButton",
                       background=[("active", BG_HOVER)])

        # Entry
        self.style.configure("TEntry",
                             fieldbackground=BG_INPUT, foreground=TEXT_PRIMARY,
                             insertcolor=TEXT_PRIMARY, font=("Segoe UI", 11),
                             padding=[8, 6])

        # Spinbox
        self.style.configure("TSpinbox",
                             fieldbackground=BG_INPUT, foreground=TEXT_PRIMARY,
                             arrowcolor=ACCENT, font=("Segoe UI", 11),
                             padding=[6, 4])

        # Checkbutton
        self.style.configure("TCheckbutton", background=BG_CARD,
                             foreground=TEXT_PRIMARY, font=("Segoe UI", 11))
        self.style.map("TCheckbutton",
                       background=[("active", BG_CARD)])

        # Separator
        self.style.configure("TSeparator", background=BORDER)

        # Treeview
        self.style.configure("Treeview",
                             background=BG_INPUT, foreground=TEXT_PRIMARY,
                             fieldbackground=BG_INPUT,
                             font=("Segoe UI", 11), rowheight=36)
        self.style.configure("Treeview.Heading",
                             background=BG_CARD, foreground=ACCENT,
                             font=("Segoe UI Semibold", 11))
        self.style.map("Treeview",
                       background=[("selected", ACCENT)],
                       foreground=[("selected", "#ffffff")])

    # ── Main UI ────────────────────────────────────────────────────────
    def _build_ui(self):
        # Title bar
        header = ttk.Frame(self, style="Dark.TFrame")
        header.pack(fill="x", padx=24, pady=(18, 4))
        ttk.Label(header, text="📋 Attendance Checker", style="Title.TLabel").pack(side="left")

        # Profile selector in header
        profile_frame = ttk.Frame(header, style="Dark.TFrame")
        profile_frame.pack(side="right")

        tk.Label(profile_frame, text="👤", bg=BG_DARK, fg=ACCENT,
                 font=("Segoe UI", 14)).pack(side="left", padx=(0, 6))

        self.profile_var = tk.StringVar(value=self.store["active_profile"])
        self.profile_combo = ttk.Combobox(
            profile_frame, textvariable=self.profile_var,
            values=list(self.store["profiles"].keys()),
            state="readonly", width=18,
            font=("Segoe UI Semibold", 11))
        self.profile_combo.pack(side="left", padx=(0, 8))
        self.profile_combo.bind("<<ComboboxSelected>>", self._on_profile_switch)

        ttk.Button(profile_frame, text="+ New", style="Green.TButton",
                   command=self._add_profile_quick).pack(side="left", padx=2)
        ttk.Button(profile_frame, text="🗑", style="Red.TButton",
                   command=self._delete_profile_quick).pack(side="left", padx=2)

        # Watermark footer (pack first so it stays at bottom)
        watermark = tk.Frame(self, bg=BG_DARK)
        watermark.pack(side="bottom", fill="x")
        tk.Label(watermark, text="Made by Aditya",
                 bg=BG_DARK, fg=TEXT_DARK,
                 font=("Segoe UI Semibold", 9),
                 anchor="center").pack(pady=(0, 8))

        # Notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=24, pady=(8, 12))

        self._build_setup_tab()
        self._build_attendance_tab()
        self._build_dashboard_tab()
        self.notebook.bind("<<NotebookTabChanged>>", lambda e: self._refresh_dashboard())

    # ── Profile Management ─────────────────────────────────────────
    def _on_profile_switch(self, event=None):
        name = self.profile_var.get()
        if name not in self.store["profiles"]:
            return
        self.store["active_profile"] = name
        self.data = self.store["profiles"][name]
        self._save()
        self._reload_all_tabs()

    def _add_profile_quick(self):
        dialog = tk.Toplevel(self)
        dialog.title("New Profile")
        dialog.geometry("350x150")
        dialog.configure(bg=BG_CARD)
        dialog.resizable(False, False)
        dialog.grab_set()

        ttk.Label(dialog, text="Enter student name:",
                  font=("Segoe UI Semibold", 12)).pack(pady=(20, 8))
        name_entry = ttk.Entry(dialog, font=("Segoe UI", 12))
        name_entry.pack(padx=24, fill="x")
        name_entry.focus_set()

        def _create(event=None):
            name = name_entry.get().strip()
            if not name:
                return
            if name in self.store["profiles"]:
                messagebox.showwarning("Duplicate", f"Profile '{name}' already exists.",
                                       parent=dialog)
                return
            self.store["profiles"][name] = default_profile()
            self.store["active_profile"] = name
            self.data = self.store["profiles"][name]
            self._save()
            self._refresh_profile_combo()
            self._reload_all_tabs()
            dialog.destroy()

        name_entry.bind("<Return>", _create)
        ttk.Button(dialog, text="Create", style="Accent.TButton",
                   command=_create).pack(pady=(12, 0))

    def _delete_profile_quick(self):
        name = self.profile_var.get()
        if len(self.store["profiles"]) <= 1:
            messagebox.showwarning("Cannot Delete", "You need at least one profile.")
            return
        if not messagebox.askyesno("Delete Profile",
                                    f"Delete profile '{name}' and all its data?"):
            return
        del self.store["profiles"][name]
        # Switch to first remaining profile
        first = list(self.store["profiles"].keys())[0]
        self.store["active_profile"] = first
        self.data = self.store["profiles"][first]
        self._save()
        self._refresh_profile_combo()
        self._reload_all_tabs()

    def _refresh_profile_combo(self):
        self.profile_combo["values"] = list(self.store["profiles"].keys())
        self.profile_var.set(self.store["active_profile"])

    def _reload_all_tabs(self):
        """Reload all tab contents for the current profile."""
        self._rebuild_setup_tab()
        self._rebuild_attendance_tab()
        self._refresh_dashboard()

    # ═══════════════════════════════════════════════════════════════════
    #  TAB 1: SETUP
    # ═══════════════════════════════════════════════════════════════════
    def _build_setup_tab(self):
        self.setup_tab = ttk.Frame(self.notebook, style="Dark.TFrame")
        self.notebook.add(self.setup_tab, text="  ⚙  Setup  ")
        self._rebuild_setup_tab()

    def _rebuild_setup_tab(self):
        for w in self.setup_tab.winfo_children():
            w.destroy()

        tab = self.setup_tab

        canvas = tk.Canvas(tab, bg=BG_DARK, highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas, style="Dark.TFrame")

        scroll_frame.bind("<Configure>",
                          lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        content = scroll_frame

        # ── Section: Subjects ──────────────────────────────────────
        subj_card = self._card(content, "📚 Subjects")

        entry_row = ttk.Frame(subj_card, style="Card.TFrame")
        entry_row.pack(fill="x", pady=(0, 8))

        self.subj_entry = ttk.Entry(entry_row)
        self.subj_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.subj_entry.bind("<Return>", lambda e: self._add_subject())

        ttk.Button(entry_row, text="+ Add", style="Accent.TButton",
                   command=self._add_subject).pack(side="right")

        self.subj_listbox = tk.Listbox(subj_card, bg=BG_INPUT, fg=TEXT_PRIMARY,
                                       selectbackground=ACCENT, selectforeground="#fff",
                                       font=("Segoe UI", 11), height=6,
                                       borderwidth=0, highlightthickness=0)
        self.subj_listbox.pack(fill="x", pady=(0, 8))

        ttk.Button(subj_card, text="🗑  Remove Selected", style="Red.TButton",
                   command=self._remove_subject).pack(anchor="e")

        self._populate_subject_list()

        # ── Section: Semester End ──────────────────────────────────
        sem_card = self._card(content, "📅 Semester End Date")

        date_row = ttk.Frame(sem_card, style="Card.TFrame")
        date_row.pack(fill="x", pady=(0, 4))

        ttk.Label(date_row, text="Day:").pack(side="left", padx=(0, 4))
        self.day_var = tk.StringVar(value="1")
        ttk.Spinbox(date_row, from_=1, to=31, width=4,
                     textvariable=self.day_var).pack(side="left", padx=(0, 12))

        ttk.Label(date_row, text="Month:").pack(side="left", padx=(0, 4))
        self.month_var = tk.StringVar(value="1")
        ttk.Spinbox(date_row, from_=1, to=12, width=4,
                     textvariable=self.month_var).pack(side="left", padx=(0, 12))

        ttk.Label(date_row, text="Year:").pack(side="left", padx=(0, 4))
        self.year_var = tk.StringVar(value=str(datetime.now().year))
        ttk.Spinbox(date_row, from_=2024, to=2030, width=6,
                     textvariable=self.year_var).pack(side="left")

        # Load saved semester end
        if self.data["semester_end"]:
            try:
                d = datetime.strptime(self.data["semester_end"], "%Y-%m-%d")
                self.day_var.set(str(d.day))
                self.month_var.set(str(d.month))
                self.year_var.set(str(d.year))
            except Exception:
                pass

        # ── Section: Timetable ─────────────────────────────────────
        tt_card = self._card(content, "🗓️ Weekly Timetable")
        ttk.Label(tt_card, text="Set number of lectures per subject on each day (0 = no class):",
                  style="Subtitle.TLabel").pack(anchor="w", pady=(0, 8))

        self.tt_vars = {}  # { day: { subject: StringVar (count) } }

        for day in DAYS:
            self.tt_vars[day] = {}

        self.tt_card_inner = tt_card  # store ref for rebuilding
        self._rebuild_timetable_checks()

        # ── Save Setup Button ──────────────────────────────────────
        ttk.Button(content, text="💾  Save Setup", style="Accent.TButton",
                   command=self._save_setup).pack(pady=(16, 24))

    def _card(self, parent, title_text):
        """Create a styled card frame with a title."""
        outer = ttk.Frame(parent, style="Dark.TFrame")
        outer.pack(fill="x", padx=8, pady=(12, 0))

        card = ttk.Frame(outer, style="Card.TFrame")
        card.pack(fill="x", ipadx=16, ipady=12)

        ttk.Label(card, text=title_text, style="Heading.TLabel").pack(
            anchor="w", padx=12, pady=(8, 8))

        inner = ttk.Frame(card, style="Card.TFrame")
        inner.pack(fill="x", padx=16, pady=(0, 8))
        return inner

    def _populate_subject_list(self):
        self.subj_listbox.delete(0, tk.END)
        for s in self.data["subjects"]:
            self.subj_listbox.insert(tk.END, f"  {s}")

    def _add_subject(self):
        name = self.subj_entry.get().strip()
        if not name:
            return
        if name in self.data["subjects"]:
            messagebox.showwarning("Duplicate", f"'{name}' already exists.")
            return
        self.data["subjects"].append(name)
        self.data["attendance"][name] = {"attended": 0, "total": 0}
        self.subj_entry.delete(0, tk.END)
        self._populate_subject_list()
        self._rebuild_timetable_checks()
        self._save()

    def _remove_subject(self):
        sel = self.subj_listbox.curselection()
        if not sel:
            return
        name = self.data["subjects"][sel[0]]
        self.data["subjects"].pop(sel[0])
        self.data["attendance"].pop(name, None)
        # Remove from timetable
        for day in DAYS:
            self.data["timetable"][day].pop(name, None)
        self._populate_subject_list()
        self._rebuild_timetable_checks()
        self._save()

    def _rebuild_timetable_checks(self):
        """Rebuild spinboxes inside the timetable section."""
        for day in DAYS:
            self.tt_vars[day] = {}

        if not hasattr(self, 'tt_card_inner'):
            return

        card = self.tt_card_inner
        # Remove existing day frames (skip the subtitle label)
        children = card.winfo_children()
        for child in children:
            if isinstance(child, ttk.Frame):
                child.destroy()

        for day in DAYS:
            day_frame = ttk.Frame(card, style="Card.TFrame")
            day_frame.pack(fill="x", pady=(0, 8))

            ttk.Label(day_frame, text=f"  {day}",
                      font=("Segoe UI Semibold", 11),
                      foreground=ACCENT, background=BG_CARD).pack(anchor="w")

            grid_frame = ttk.Frame(day_frame, style="Card.TFrame")
            grid_frame.pack(fill="x", padx=(20, 0))

            self.tt_vars[day] = {}
            saved_tt = self.data["timetable"].get(day, {})
            for col, subj in enumerate(self.data["subjects"]):
                # Get saved count (handle legacy list format gracefully)
                if isinstance(saved_tt, dict):
                    saved_count = saved_tt.get(subj, 0)
                else:
                    # Legacy: list format — count occurrences
                    saved_count = saved_tt.count(subj) if subj in saved_tt else 0

                var = tk.StringVar(value=str(saved_count))
                self.tt_vars[day][subj] = var

                subj_frame = ttk.Frame(grid_frame, style="Card.TFrame")
                subj_frame.pack(side="left", padx=(0, 18))

                ttk.Label(subj_frame, text=subj, font=("Segoe UI", 10)).pack(anchor="w")
                ttk.Spinbox(subj_frame, from_=0, to=5, width=3,
                            textvariable=var).pack(anchor="w")

    def _save_setup(self):
        # Save semester end
        try:
            d = int(self.day_var.get())
            m = int(self.month_var.get())
            y = int(self.year_var.get())
            sem_end = date(y, m, d)
            self.data["semester_end"] = sem_end.isoformat()
        except Exception:
            messagebox.showerror("Invalid Date", "Please enter a valid semester end date.")
            return

        # Save timetable (store as { subject: count } per day)
        for day in DAYS:
            self.data["timetable"][day] = {}
            for subj, var in self.tt_vars[day].items():
                try:
                    count = int(var.get())
                except ValueError:
                    count = 0
                if count > 0:
                    self.data["timetable"][day][subj] = count

        self._save()
        messagebox.showinfo("Saved", "Setup saved successfully! ✓")
        # Rebuild attendance tab
        self._rebuild_attendance_tab()

    # ═══════════════════════════════════════════════════════════════════
    #  TAB 2: ATTENDANCE
    # ═══════════════════════════════════════════════════════════════════
    def _build_attendance_tab(self):
        self.att_tab = ttk.Frame(self.notebook, style="Dark.TFrame")
        self.notebook.add(self.att_tab, text="  ✅  Attendance  ")
        self._rebuild_attendance_tab()

    def _rebuild_attendance_tab(self):
        for w in self.att_tab.winfo_children():
            w.destroy()

        canvas = tk.Canvas(self.att_tab, bg=BG_DARK, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.att_tab, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas, style="Dark.TFrame")

        scroll_frame.bind("<Configure>",
                          lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        content = scroll_frame

        # ── Today's Classes ────────────────────────────────────────
        today_name = DAYS[datetime.now().weekday()] if datetime.now().weekday() < 6 else None
        today_tt = self.data["timetable"].get(today_name, {}) if today_name else {}
        # Handle legacy list format
        if isinstance(today_tt, list):
            today_tt = {s: today_tt.count(s) for s in set(today_tt)}

        today_card = self._card(content,
                                f"📆 Today's Classes — {today_name or 'Sunday (No classes)'}")

        if today_tt:
            self.today_vars = []  # list of (subj, lecture_num, BooleanVar)
            for subj, count in today_tt.items():
                for lec_num in range(1, count + 1):
                    row = ttk.Frame(today_card, style="Card.TFrame")
                    row.pack(fill="x", pady=3)

                    label = f"  {subj}" if count == 1 else f"  {subj}  (Lecture {lec_num}/{count})"
                    var = tk.BooleanVar(value=True)
                    self.today_vars.append((subj, lec_num, var))
                    ttk.Checkbutton(row, text=label, variable=var).pack(side="left")

            ttk.Button(today_card, text="📝 Log Today's Attendance",
                       style="Accent.TButton",
                       command=self._log_today).pack(pady=(12, 0))
        else:
            ttk.Label(today_card, text="No classes scheduled today.",
                      style="Subtitle.TLabel").pack(pady=8)

        # ── Manual Entry ───────────────────────────────────────────
        manual_card = self._card(content, "✏️ Manual Entry")

        ttk.Label(manual_card, text="Directly set attended / total for a subject:",
                  style="Subtitle.TLabel").pack(anchor="w", pady=(0, 8))

        # Subject selector
        sel_row = ttk.Frame(manual_card, style="Card.TFrame")
        sel_row.pack(fill="x", pady=(0, 8))

        ttk.Label(sel_row, text="Subject:").pack(side="left", padx=(0, 8))
        self.manual_subj_var = tk.StringVar()
        subj_combo = ttk.Combobox(sel_row, textvariable=self.manual_subj_var,
                                   values=self.data["subjects"], state="readonly",
                                   width=30)
        subj_combo.pack(side="left")
        if self.data["subjects"]:
            subj_combo.current(0)

        nums_row = ttk.Frame(manual_card, style="Card.TFrame")
        nums_row.pack(fill="x", pady=(0, 8))

        ttk.Label(nums_row, text="Attended:").pack(side="left", padx=(0, 4))
        self.manual_attended = ttk.Entry(nums_row, width=6)
        self.manual_attended.pack(side="left", padx=(0, 16))

        ttk.Label(nums_row, text="Total:").pack(side="left", padx=(0, 4))
        self.manual_total = ttk.Entry(nums_row, width=6)
        self.manual_total.pack(side="left")

        def on_subj_selected(event=None):
            subj = self.manual_subj_var.get()
            if subj and subj in self.data["attendance"]:
                att = self.data["attendance"][subj]
                self.manual_attended.delete(0, tk.END)
                self.manual_attended.insert(0, str(att["attended"]))
                self.manual_total.delete(0, tk.END)
                self.manual_total.insert(0, str(att["total"]))

        subj_combo.bind("<<ComboboxSelected>>", on_subj_selected)
        on_subj_selected()  # populate initial values

        ttk.Button(manual_card, text="💾 Update Attendance",
                   style="Green.TButton",
                   command=self._manual_update).pack(anchor="e", pady=(4, 0))

        # ── Quick Attendance (all subjects) ────────────────────────
        quick_card = self._card(content, "⚡ Quick Overview")

        for subj in self.data["subjects"]:
            att = self.data["attendance"].get(subj, {"attended": 0, "total": 0})
            row = ttk.Frame(quick_card, style="Card.TFrame")
            row.pack(fill="x", pady=3)

            ttk.Label(row, text=f"  {subj}", width=20, anchor="w").pack(side="left")

            pct = (att["attended"] / att["total"] * 100) if att["total"] > 0 else 0
            color_style = "Green.TLabel" if pct >= 75 else ("Yellow.TLabel" if pct >= 73 else "Red.TLabel")

            ttk.Label(row, text=f'{att["attended"]}/{att["total"]}',
                      width=8).pack(side="left", padx=(0, 8))
            ttk.Label(row, text=f'{pct:.1f}%',
                      style=color_style, width=8).pack(side="left")

            # +1 / -1 buttons for quick adjustments
            btn_frame = ttk.Frame(row, style="Card.TFrame")
            btn_frame.pack(side="right")

            def _make_adj(s=subj):
                def _present():
                    self.data["attendance"][s]["attended"] += 1
                    self.data["attendance"][s]["total"] += 1
                    self._save()
                    self._rebuild_attendance_tab()

                def _absent():
                    self.data["attendance"][s]["total"] += 1
                    self._save()
                    self._rebuild_attendance_tab()
                return _present, _absent

            present_fn, absent_fn = _make_adj()
            ttk.Button(btn_frame, text="✓ Present", style="Green.TButton",
                       command=present_fn).pack(side="left", padx=2)
            ttk.Button(btn_frame, text="✗ Absent", style="Red.TButton",
                       command=absent_fn).pack(side="left", padx=2)

    def _log_today(self):
        for subj, lec_num, var in self.today_vars:
            if subj not in self.data["attendance"]:
                self.data["attendance"][subj] = {"attended": 0, "total": 0}
            self.data["attendance"][subj]["total"] += 1
            if var.get():
                self.data["attendance"][subj]["attended"] += 1
        self._save()
        messagebox.showinfo("Logged", "Today's attendance logged! ✓")
        self._rebuild_attendance_tab()

    def _manual_update(self):
        subj = self.manual_subj_var.get()
        if not subj:
            return
        try:
            attended = int(self.manual_attended.get())
            total = int(self.manual_total.get())
        except ValueError:
            messagebox.showerror("Error", "Enter valid numbers for attended and total.")
            return

        if attended < 0 or total < 0 or attended > total:
            messagebox.showerror("Error", "Attended must be between 0 and Total.")
            return

        self.data["attendance"][subj] = {"attended": attended, "total": total}
        self._save()
        messagebox.showinfo("Updated", f"Attendance for '{subj}' updated! ✓")
        self._rebuild_attendance_tab()

    # ═══════════════════════════════════════════════════════════════════
    #  TAB 3: DASHBOARD
    # ═══════════════════════════════════════════════════════════════════
    def _build_dashboard_tab(self):
        self.dash_tab = ttk.Frame(self.notebook, style="Dark.TFrame")
        self.notebook.add(self.dash_tab, text="  📊  Dashboard  ")

    def _refresh_dashboard(self):
        for w in self.dash_tab.winfo_children():
            w.destroy()

        canvas = tk.Canvas(self.dash_tab, bg=BG_DARK, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.dash_tab, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas, style="Dark.TFrame")

        scroll_frame.bind("<Configure>",
                          lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        content = scroll_frame

        # ── Overall Stats Row ──────────────────────────────────────
        stats_outer = ttk.Frame(content, style="Dark.TFrame")
        stats_outer.pack(fill="x", padx=8, pady=(12, 0))

        total_att = sum(a["attended"] for a in self.data["attendance"].values())
        total_cls = sum(a["total"] for a in self.data["attendance"].values())
        overall_pct = (total_att / total_cls * 100) if total_cls > 0 else 0

        # Remaining working days
        rem_days = self._remaining_working_days()

        stats = [
            ("Overall %", f"{overall_pct:.1f}%",
             "All subjects combined"),
            ("Attended", f"{total_att}/{total_cls}",
             "Total classes"),
            ("Days Left", str(rem_days) if rem_days is not None else "—",
             "Working days remaining"),
            ("Subjects", str(len(self.data["subjects"])),
             "Enrolled"),
        ]

        for i, (label, value, sub) in enumerate(stats):
            card = ttk.Frame(stats_outer, style="Card.TFrame")
            card.pack(side="left", fill="both", expand=True, padx=4, ipady=12, ipadx=12)

            ttk.Label(card, text=value, style="BigStat.TLabel").pack(pady=(12, 0))
            ttk.Label(card, text=label, style="TLabel").pack()
            ttk.Label(card, text=sub, style="Subtitle.TLabel").pack(pady=(0, 8))

        # ── Per-Subject Table ──────────────────────────────────────
        table_card = self._card(content, "📋 Subject-wise Breakdown")

        cols = ("subject", "attended", "total", "pct", "can_skip", "must_attend", "rem")
        col_headings = {
            "subject": "Subject",
            "attended": "Attended",
            "total": "Total",
            "pct": "Attendance %",
            "can_skip": "Can Skip",
            "must_attend": "Must Attend",
            "rem": "Rem. Classes"
        }
        col_widths = {
            "subject": 120,
            "attended": 80,
            "total": 80,
            "pct": 100,
            "can_skip": 90,
            "must_attend": 100,
            "rem": 100
        }

        tree = ttk.Treeview(table_card, columns=cols, show="headings",
                            height=min(len(self.data["subjects"]) + 1, 12))

        for col_id in cols:
            tree.heading(col_id, text=col_headings[col_id], anchor="center")
            anchor = "w" if col_id == "subject" else "center"
            tree.column(col_id, width=col_widths[col_id], anchor=anchor, minwidth=60)

        # Color tags
        tree.tag_configure("safe", foreground=GREEN)
        tree.tag_configure("danger", foreground=RED)
        tree.tag_configure("warn", foreground=YELLOW)

        # Populate rows
        for subj in self.data["subjects"]:
            att = self.data["attendance"].get(subj, {"attended": 0, "total": 0})
            attended = att["attended"]
            total = att["total"]

            pct = (attended / total * 100) if total > 0 else 0

            # Can skip: how many future classes can be skipped and still be ≥ 75%
            if pct >= 75 and total > 0:
                can_skip = math.floor(attended / 0.75) - total
            else:
                can_skip = 0

            # Must attend: consecutive classes to attend to reach 75%
            if pct < 75 and total > 0:
                must = math.ceil((0.75 * total - attended) / 0.25)
                must = max(must, 0)
            elif total == 0:
                must = 0
            else:
                must = 0

            rem_classes = self._remaining_classes_for_subject(subj)

            # Pick tag
            tag = "safe" if pct >= 75 else ("warn" if pct >= 73 else "danger")

            tree.insert("", "end", values=(
                subj,
                attended,
                total,
                f"{pct:.1f}%",
                str(can_skip) if can_skip > 0 else "—",
                str(must) if must > 0 else "✓",
                str(rem_classes) if rem_classes is not None else "—"
            ), tags=(tag,))

        tree.pack(fill="x", pady=(0, 8))

        # ── Insights ───────────────────────────────────────────────
        insight_card = self._card(content, "💡 Insights")

        safe_subjects = []
        danger_subjects = []
        for subj in self.data["subjects"]:
            att = self.data["attendance"].get(subj, {"attended": 0, "total": 0})
            if att["total"] == 0:
                continue
            pct = att["attended"] / att["total"] * 100
            if pct >= 75:
                can_skip = math.floor(att["attended"] / 0.75) - att["total"]
                safe_subjects.append((subj, pct, can_skip))
            else:
                must = math.ceil((0.75 * att["total"] - att["attended"]) / 0.25)
                danger_subjects.append((subj, pct, max(must, 0)))

        if danger_subjects:
            ttk.Label(insight_card, text="⚠️ Subjects Below 75%:",
                      style="Red.TLabel").pack(anchor="w", pady=(0, 4))
            for subj, pct, must in danger_subjects:
                ttk.Label(insight_card,
                          text=f"   • {subj}: {pct:.1f}% — attend next {must} classes to recover",
                          foreground=RED, background=BG_CARD,
                          font=("Segoe UI", 10)).pack(anchor="w")

        if safe_subjects:
            ttk.Label(insight_card, text="\n✅ Safe Subjects:",
                      style="Green.TLabel").pack(anchor="w", pady=(8, 4))
            for subj, pct, can_skip in safe_subjects:
                ttk.Label(insight_card,
                          text=f"   • {subj}: {pct:.1f}% — can skip {can_skip} more classes",
                          foreground=GREEN, background=BG_CARD,
                          font=("Segoe UI", 10)).pack(anchor="w")

        if not safe_subjects and not danger_subjects:
            ttk.Label(insight_card,
                      text="No attendance data yet. Start logging to see insights!",
                      style="Subtitle.TLabel").pack(pady=12)

        # Add padding at bottom
        ttk.Frame(content, style="Dark.TFrame", height=24).pack()

    # ── Calculation Helpers ────────────────────────────────────────
    def _remaining_working_days(self):
        """Count weekdays Mon-Sat from tomorrow to semester end."""
        if not self.data["semester_end"]:
            return None
        try:
            end = datetime.strptime(self.data["semester_end"], "%Y-%m-%d").date()
        except Exception:
            return None

        today = date.today()
        if today >= end:
            return 0

        count = 0
        current = today + timedelta(days=1)
        while current <= end:
            if current.weekday() < 6:  # Mon=0 ... Sat=5
                count += 1
            current += timedelta(days=1)
        return count

    def _remaining_classes_for_subject(self, subject):
        """Count remaining scheduled classes from tomorrow to semester end."""
        if not self.data["semester_end"]:
            return None
        try:
            end = datetime.strptime(self.data["semester_end"], "%Y-%m-%d").date()
        except Exception:
            return None

        today = date.today()
        if today >= end:
            return 0

        # Which weekdays is this subject scheduled and how many lectures?
        scheduled_days = {}  # weekday_index -> count
        for i, day_name in enumerate(DAYS):
            tt = self.data["timetable"].get(day_name, {})
            if isinstance(tt, list):
                # Legacy list format
                c = tt.count(subject)
            else:
                c = tt.get(subject, 0)
            if c > 0:
                scheduled_days[i] = c

        count = 0
        current = today + timedelta(days=1)
        while current <= end:
            if current.weekday() in scheduled_days:
                count += scheduled_days[current.weekday()]
            current += timedelta(days=1)
        return count

    # ── Persistence helper ─────────────────────────────────────────
    def _save(self):
        save_store(self.store)


# ═══════════════════════════════════════════════════════════════════════
#  Entry Point
# ═══════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = AttendanceApp()
    app.mainloop()
