#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox
import random
import json
import os
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, List

# --- Age rules ---
STARTING_AGE    = 18
RETIREMENT_AGE  = 60

# --- Starting stat values ---
STARTING_MONEY      = 5_000
STARTING_HAPPINESS  = 50
STARTING_HEALTH     = 70
STARTING_EDUCATION  = 20

# --- Game-over thresholds (stats must NOT fall to these or below) ---
MIN_HEALTH    = 5
MIN_HAPPINESS = 10

# --- What each action costs ---
UNIVERSITY_COST = 15_000
TRAVEL_COST     = 10_000
REST_COST       = 2_000
BUSINESS_COST   = 50_000
BUSINESS_INCOME = 80_000

# --- Human-readable degree names (education_level 0-3) ---
EDU_NAMES = {
    0: "High School",
    1: "Bachelor's Degree",
    2: "Master's Degree",
    3: "PhD",
}

# --- Job table: job name → requirements and per-year effects ---
JOBS = {
    "Entry Level": {"min_edu": 0, "salary": 35_000,  "happiness": -5,  "health": -3},
    "Mid-Level":   {"min_edu": 1, "salary": 65_000,  "happiness":  0,  "health": -3},
    "Senior":      {"min_edu": 2, "salary": 100_000, "happiness":  5,  "health": -3},
    "Executive":   {"min_edu": 2, "salary": 150_000, "happiness": 10,  "health": -3},
}

# --- Destinations picked at random when the player travels ---
DESTINATIONS = [
    "Japan", "Italy", "Brazil", "Norway", "Thailand",
    "New Zealand", "Spain", "Egypt", "Iceland",
]

# --- Folder that holds all save files ---
SAVE_FOLDER = "life_simulator_saves"


# ============================================================
# SECTION 2: COLOURS AND FONTS  (dark theme, blue accents)
# ============================================================

# All colours used in the game — change one entry to restyle everything
C = {
    "bg":       "#0d1117",  # Very dark background
    "panel":    "#161b22",  # Panel / sidebar background
    "card":     "#21262d",  # Inner cards / text boxes
    "border":   "#30363d",  # Thin border / divider lines
    "accent":   "#58a6ff",  # Blue accent — titles, highlights
    "text":     "#e6edf3",  # Primary text (near-white)
    "muted":    "#8b949e",  # Secondary / label text (grey)
    "gold":     "#e3b341",  # Money (yellow-gold)
    "blue":     "#79c0ff",  # Happiness bar
    "green":    "#56d364",  # Health bar / success
    "purple":   "#d2a8ff",  # Education bar
    "orange":   "#f0883e",  # Action result text
    "red":      "#f85149",  # Danger / negative events
    "teal":     "#39d353",  # Positive events / welcome
    "btn":      "#1f6feb",  # Default button blue
    "btn_dark": "#0d419d",  # Darker blue for secondary buttons
}

# Font tuples — (family, size, style)
F = {
    "huge":   ("Arial", 30, "bold"),
    "big":    ("Arial", 18, "bold"),
    "title":  ("Arial", 13, "bold"),
    "normal": ("Arial", 11),
    "small":  ("Arial", 9),
    "mono":   ("Courier New", 10),
    "btn":    ("Arial", 11, "bold"),
}

@dataclass
class Stats:
    """
    Holds the four core player statistics.

    Using @dataclass means Python auto-generates __init__ for us,
    so we don't have to write it by hand.
    """
    money:     float = STARTING_MONEY
    happiness: int   = STARTING_HAPPINESS
    health:    int   = STARTING_HEALTH
    education: int   = STARTING_EDUCATION

    def clamp(self):
        """Keep every stat inside its legal range after any change."""
        self.money     = max(0.0, self.money)
        self.happiness = max(0, min(100, self.happiness))
        self.health    = max(0, min(100, self.health))
        self.education = max(0, min(100, self.education))


class Player:
    """
    Tracks everything about the player throughout the game:
    age, stats, job, education, business, and life history.
    """

    def __init__(self, name: str):
        """
        Create a brand-new player starting at age 18.

        Args:
            name: The character name the user typed in
        """
        self.name:            str           = name
        self.age:             int           = STARTING_AGE
        self.stats:           Stats         = Stats()
        self.current_job:     Optional[str] = None    # None means unemployed
        self.job_salary:      float         = 0.0
        self.has_business:    bool          = False
        self.business_income: float         = 0.0
        self.education_level: int           = 0       # 0=HS  1=Bach  2=MSc  3=PhD
        self.history:         List[str]     = []      # Log of major life events
        self.is_alive:        bool          = True
        self.end_reason:      str           = ""      # "retirement"/"health"/"happiness"

    # ------ Simple helpers ------

    def get_total_income(self) -> float:
        """Return the player's total yearly income (job + business)."""
        return self.job_salary + self.business_income

    def get_degree_name(self) -> str:
        """Return the human-readable name of the current education level."""
        return EDU_NAMES.get(self.education_level, "Unknown")

    # ------ Core year logic ------

    def apply_yearly_effects(self) -> List[str]:
        """
        Apply the automatic changes that happen every year:
        - Add income from job and/or business
        - Reduce happiness by 2 (natural decay)
        - Reduce health by 3 (aging), plus 5 extra after age 50
        - Advance age by 1
        - Check game-over conditions

        Returns:
            A list of short message strings (used to fill the story log)
        """
        msgs: List[str] = []

        # Add yearly income
        income = self.get_total_income()
        if income > 0:
            self.stats.money += income
            msgs.append(f"Yearly income: +${income:,.0f}")

        # Natural happiness decay
        self.stats.happiness -= 2
        msgs.append("Happiness -2  (natural decay)")

        # Natural health decay — gets worse after age 50
        health_loss = 3
        if self.age > 50:
            health_loss += 5
            msgs.append(f"Health -{health_loss}  (extra aging after 50)")
        else:
            msgs.append(f"Health -{health_loss}")
        self.stats.health -= health_loss

        # Age up
        self.age += 1

        # Clamp all stats to valid ranges
        self.stats.clamp()

        # Check whether the game should end
        if self.stats.health <= MIN_HEALTH:
            self.is_alive  = False
            self.end_reason = "health"
        elif self.stats.happiness <= MIN_HAPPINESS:
            self.is_alive  = False
            self.end_reason = "happiness"

        return msgs

    def apply_event(self, event: "Event"):
        """
        Apply a random event's stat changes and record it in history.

        Args:
            event: The Event object to apply
        """
        self.stats.money     += event.money_change
        self.stats.happiness += event.happiness_change
        self.stats.health    += event.health_change
        self.stats.education += event.education_change
        self.stats.clamp()
        # Record at the age *before* the yearly effects incremented it
        self.history.append(f"Age {self.age - 1}: {event.name}")

    # ------ Scoring ------

    def calculate_score(self) -> int:
        """
        Calculate the final life score.
        Formula: (money ÷ 1000) + (happiness × 2) + health + education
        """
        return int(
            (self.stats.money / 1000)
            + (self.stats.happiness * 2)
            + self.stats.health
            + self.stats.education
        )

    def get_life_outcome(self) -> str:
        """Return the outcome sentence that matches the player's final score."""
        score = self.calculate_score()
        if score >= 500:
            return "🌟 LEGENDARY LIFE: You lived an extraordinary life full of success and happiness!"
        elif score >= 350:
            return "⭐ GREAT LIFE: You achieved much and lived a fulfilling life!"
        elif score >= 200:
            return "👍 GOOD LIFE: You had ups and downs, but overall a decent life!"
        elif score >= 100:
            return "😐 AVERAGE LIFE: You got by, though things could have been better."
        else:
            return "😞 ROUGH LIFE: Life was challenging, but you made it through."

    # ------ Save / Load ------

    def to_dict(self) -> dict:
        """Convert the player to a plain dictionary for JSON serialisation."""
        return {
            "name":            self.name,
            "age":             self.age,
            "years_lived":     self.age - STARTING_AGE,
            "stats": {
                "money":     self.stats.money,
                "happiness": self.stats.happiness,
                "health":    self.stats.health,
                "education": self.stats.education,
            },
            "current_job":     self.current_job,
            "job_salary":      self.job_salary,
            "has_business":    self.has_business,
            "business_income": self.business_income,
            "education_level": self.education_level,
            "history":         self.history,
            "is_alive":        self.is_alive,
            "end_reason":      self.end_reason,
            "save_timestamp":  datetime.now().isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Player":
        """
        Recreate a Player from a dictionary loaded from a save file.

        Args:
            data: Dictionary with all saved player fields

        Returns:
            A Player object with all state restored
        """
        p = cls(data["name"])
        p.age             = data["age"]
        p.stats           = Stats(**data["stats"])     # ** unpacks the dict into keyword args
        p.current_job     = data.get("current_job")
        p.job_salary      = data.get("job_salary",      0.0)
        p.has_business    = data.get("has_business",    False)
        p.business_income = data.get("business_income", 0.0)
        p.education_level = data.get("education_level", 0)
        p.history         = data.get("history",         [])
        p.is_alive        = data.get("is_alive",        True)
        p.end_reason      = data.get("end_reason",      "")
        return p


@dataclass
class Event:
    """
    One possible random life event.

    Attributes:
        name:         Short event title shown in popups
        description:  One-sentence story about what happened
        *_change:     How much each stat changes (negative = bad)
        is_positive:  True for good events, False for bad ones
    """
    name:             str
    description:      str
    money_change:     float = 0
    happiness_change: int   = 0
    health_change:    int   = 0
    education_change: int   = 0
    is_positive:      bool  = True


class EventSystem:
    """
    Holds the 12 possible random events and picks one at random
    with a 40% chance each year.
    """

    # All 12 events — 6 positive, 6 negative
    ALL_EVENTS: List[Event] = [
        # ---- Positive events ----
        Event("Promotion at Work",
              "Your hard work paid off — your boss called with great news!",
              money_change=8_000, happiness_change=10, health_change=-5,
              is_positive=True),

        Event("Lottery Win",
              "On a whim you bought a lottery ticket. The numbers matched — all of them!",
              money_change=50_000, happiness_change=20,
              is_positive=True),

        Event("Inheritance",
              "A letter arrived from a solicitor — a distant relative left you a generous gift.",
              money_change=30_000, happiness_change=15,
              is_positive=True),

        Event("Best Year Ever",
              "Everything aligned perfectly this year — relationships, finances, and health all thrived.",
              money_change=15_000, happiness_change=25, health_change=10,
              is_positive=True),

        Event("Breakthrough",
              "A flash of insight sparked a breakthrough that opened exciting new doors.",
              money_change=10_000, happiness_change=15, education_change=15,
              is_positive=True),

        Event("Award Recognition",
              "Your peers nominated you for a prestigious award — and you won!",
              money_change=5_000, happiness_change=20, education_change=10,
              is_positive=True),

        # ---- Negative events ----
        Event("Fell Ill",
              "A serious illness knocked you off your feet and drained your savings.",
              money_change=-1_000, happiness_change=-10, health_change=-15,
              is_positive=False),

        Event("Job Loss",
              "The company announced layoffs — and your name was on the list.",
              money_change=-5_000, happiness_change=-20, health_change=-10,
              is_positive=False),

        Event("Relationship Troubles",
              "A painful breakup left you emotionally drained and questioning everything.",
              happiness_change=-25, health_change=-5,
              is_positive=False),

        Event("Accident",
              "A freak accident sent you to hospital; the bills piled up fast.",
              money_change=-3_000, happiness_change=-10, health_change=-20,
              is_positive=False),

        Event("Family Crisis",
              "A family emergency demanded your time, energy, and a large chunk of savings.",
              money_change=-15_000, happiness_change=-15, health_change=-10,
              is_positive=False),

        Event("Burnout",
              "The pressure finally caught up with you — body and mind forced you to stop.",
              money_change=2_000, happiness_change=-15, health_change=-20,
              is_positive=False),
    ]

    @staticmethod
    def roll() -> Optional[Event]:
        """
        Attempt to trigger a random event (40% chance).

        Returns:
            A random Event, or None if no event happens this year
        """
        if random.random() < 0.40:
            return random.choice(EventSystem.ALL_EVENTS)
        return None

@dataclass
class ActionResult:
    """
    Returned by every action method so the GUI knows what happened.

    Attributes:
        success:      True if the action was completed; False if it was blocked
        message:      Human-readable description of the outcome
        *_change:     How much each stat changed (for display)
    """
    success:          bool
    message:          str
    money_change:     float = 0
    happiness_change: int   = 0
    health_change:    int   = 0
    education_change: int   = 0


class Actions:
    """
    One static method for each of the five player actions.
    Each method validates requirements, modifies the player's stats,
    updates history, and returns an ActionResult.
    """

    @staticmethod
    def go_to_university(player: Player) -> ActionResult:
        """
        Spend a year studying to earn the next academic degree.

        Requirements: not already at PhD; must have $15,000.

        Args:
            player: The current player

        Returns:
            ActionResult describing success or the reason for failure
        """
        if player.education_level >= 3:
            return ActionResult(False,
                "You already have a PhD — the highest degree possible!")

        if player.stats.money < UNIVERSITY_COST:
            return ActionResult(False,
                f"University costs ${UNIVERSITY_COST:,}. "
                f"You only have ${player.stats.money:,.0f}.")

        # Apply the effects
        player.stats.money     -= UNIVERSITY_COST
        player.education_level += 1
        player.stats.education += 25
        player.stats.happiness += 5
        player.stats.health    -= 5
        player.stats.clamp()

        degree = EDU_NAMES[player.education_level]
        player.history.append(f"Age {player.age}: Earned {degree}")

        return ActionResult(True,
            f"You earned your {degree}!  📚 +25  😊 +5  ❤️ -5",
            money_change=-UNIVERSITY_COST,
            happiness_change=5, health_change=-5, education_change=25)

    @staticmethod
    def get_a_job(player: Player, job_name: str) -> ActionResult:
        """
        Start (or switch to) the chosen job.

        Requirements: the job's minimum education level.

        Args:
            player:   The current player
            job_name: Key from the JOBS dictionary

        Returns:
            ActionResult describing success or the reason for failure
        """
        if job_name not in JOBS:
            return ActionResult(False, "That job doesn't exist.")

        info = JOBS[job_name]
        if player.education_level < info["min_edu"]:
            return ActionResult(False,
                f"You need a {EDU_NAMES[info['min_edu']]} for this job.")

        player.current_job = job_name
        player.job_salary  = float(info["salary"])
        h_ch  = info["happiness"]
        he_ch = info["health"]
        player.stats.happiness += h_ch
        player.stats.health    += he_ch
        player.stats.clamp()

        player.history.append(
            f"Age {player.age}: Started {job_name} (${player.job_salary:,.0f}/yr)")

        return ActionResult(True,
            f"You got the {job_name} job!  💰 ${player.job_salary:,.0f}/yr  "
            f"😊 {h_ch:+d}  ❤️ {he_ch:+d}",
            happiness_change=h_ch, health_change=he_ch)

    @staticmethod
    def start_business(player: Player) -> ActionResult:
        """
        Launch a business that earns $80,000/year ongoing income.

        Requirements: Master's or PhD; $50,000 startup money; no existing business.

        Args:
            player: The current player

        Returns:
            ActionResult describing success or the reason for failure
        """
        if player.has_business:
            return ActionResult(False, "You already own a business!")
        if player.education_level < 2:
            return ActionResult(False,
                "You need at least a Master's Degree to start a business.")
        if player.stats.money < BUSINESS_COST:
            return ActionResult(False,
                f"Starting a business costs ${BUSINESS_COST:,}. "
                f"You only have ${player.stats.money:,.0f}.")

        player.stats.money     -= BUSINESS_COST
        player.has_business     = True
        player.business_income  = float(BUSINESS_INCOME)
        player.stats.happiness += 20
        player.stats.health    -= 15
        player.stats.education += 10
        player.stats.clamp()

        player.history.append(f"Age {player.age}: Founded own business")

        return ActionResult(True,
            f"You founded your own business!  💰 +${BUSINESS_INCOME:,}/yr  "
            f"😊 +20  ❤️ -15  📚 +10",
            money_change=-BUSINESS_COST,
            happiness_change=20, health_change=-15, education_change=10)

    @staticmethod
    def travel(player: Player) -> ActionResult:
        """
        Take a trip to a random destination. Cost: $10,000.
        Effects: Happiness +30, Health +15, Education +5.

        Args:
            player: The current player

        Returns:
            ActionResult describing success or the reason for failure
        """
        if player.stats.money < TRAVEL_COST:
            return ActionResult(False,
                f"Travel costs ${TRAVEL_COST:,}. "
                f"You only have ${player.stats.money:,.0f}.")

        destination = random.choice(DESTINATIONS)
        player.stats.money     -= TRAVEL_COST
        player.stats.happiness += 30
        player.stats.health    += 15
        player.stats.education += 5
        player.stats.clamp()

        player.history.append(f"Age {player.age}: Traveled to {destination}")

        return ActionResult(True,
            f"You traveled to {destination}!  😊 +30  ❤️ +15  📚 +5",
            money_change=-TRAVEL_COST,
            happiness_change=30, health_change=15, education_change=5)

    @staticmethod
    def rest_and_relax(player: Player) -> ActionResult:
        """
        Take the year off to recover. Cost: up to $2,000 lost productivity.
        Effects: Happiness +15, Health +25.

        Args:
            player: The current player

        Returns:
            ActionResult (always succeeds)
        """
        # Can't spend more than the player currently has
        cost = min(REST_COST, player.stats.money)
        player.stats.money     -= cost
        player.stats.happiness += 15
        player.stats.health    += 25
        player.stats.clamp()

        return ActionResult(True,
            f"You took the year to rest!  😊 +15  ❤️ +25  💰 -${cost:,.0f}",
            money_change=-cost, happiness_change=15, health_change=25)


# ============================================================
# SECTION 7: STORY GENERATOR
# ============================================================

class StoryGenerator:
    """
    Generates a personalised 2-3 sentence narrative for each year
    based on the player's stats, job, business, and what just happened.
    """

    @staticmethod
    def generate(player: Player,
                 result: ActionResult,
                 event: Optional[Event]) -> str:
        """
        Build a short story paragraph about the player's year.

        Args:
            player: Current player state (stats already updated)
            result: What action the player took
            event:  Random event that happened, or None

        Returns:
            A 2-3 sentence story string
        """
        name = player.name
        age  = player.age - 1     # Age at the START of this year
        s    = player.stats

        # Decide the emotional tone from the happiness level
        if s.happiness >= 70:
            mood = "high"
        elif s.happiness >= 35:
            mood = "medium"
        else:
            mood = "low"

        sentences: List[str] = []

        # --- Opening sentence: describe what the player did ---
        msg = result.message.lower()

        if any(w in msg for w in ["degree", "phd", "bachelor", "master", "earned"]):
            sentences.append(
                f"At {age}, {name} devoted the year to study, pouring over textbooks "
                f"and emerging with a new qualification to be proud of.")

        elif "job" in msg and "/yr" in msg:
            if mood == "high":
                sentences.append(
                    f"Age {age} was a confident year professionally — {name} stepped into "
                    f"a new role with real enthusiasm and quickly made an impression.")
            elif mood == "low":
                sentences.append(
                    f"At {age}, {name} took on new work, though the daily grind felt "
                    f"heavier than expected.")
            else:
                sentences.append(
                    f"At {age}, {name} settled into a new job, finding steady income "
                    f"and a reliable routine.")

        elif "business" in msg or "founded" in msg:
            sentences.append(
                f"Age {age} marked a bold new chapter — {name} left the safety of employment "
                f"behind and launched their own business from scratch.")

        elif "traveled" in msg:
            dest = "a distant land"
            for d in DESTINATIONS:
                if d.lower() in msg:
                    dest = d
                    break
            sentences.append(
                f"At {age}, {name} packed a bag and flew to {dest}, chasing new sights "
                f"and the kind of perspective only travel can offer.")

        elif "rested" in msg:
            sentences.append(
                f"Age {age} was a year of deliberate rest — {name} pressed pause on "
                f"ambition and let body and mind quietly recover.")

        else:
            sentences.append(f"At {age}, {name} navigated another chapter of life's twists.")

        # --- Middle sentence: financial or career colour ---
        if s.money > 120_000 and mood == "high":
            sentences.append(
                f"Financial security gave {name} a rare sense of freedom — "
                f"choices felt like opportunities rather than gambles.")
        elif s.money < 3_000:
            sentences.append(
                f"Every expense was a calculation; money was tight enough that "
                f"{name} had to think twice before any purchase.")
        elif player.has_business and mood != "low":
            sentences.append(
                f"The business continued to grow, and {name} quietly savoured "
                f"the satisfaction of having built something entirely their own.")
        elif player.current_job and mood == "low":
            sentences.append(
                f"The job was steady, but {name} sometimes wondered late at night "
                f"whether this was really the life they had imagined.")

        # --- Closing sentence: health or general wellbeing ---
        if s.health >= 75 and mood == "high":
            sentences.append(
                f"{name} felt genuinely well — energised, clear-headed, "
                f"and ready for whatever came next.")
        elif s.health < 25:
            sentences.append(
                f"Health had become a real worry, a quiet voice reminding "
                f"{name} that the body cannot be ignored indefinitely.")
        elif mood == "low":
            sentences.append(
                f"Despite the difficulties, {name} held on to small moments of joy "
                f"and reminded themselves that harder years had passed before.")
        elif s.education >= 75:
            sentences.append(
                f"Years of learning had sharpened {name}'s perspective in ways "
                f"that no salary could fully capture.")
        else:
            sentences.append(
                f"Life moved on, each year adding another line to {name}'s story.")

        # Return at most 3 sentences joined together
        return " ".join(sentences[:3])



class SaveSystem:
    """Handles saving and loading game state as JSON files."""

    @staticmethod
    def ensure_folder():
        """Create the saves directory if it does not already exist."""
        if not os.path.exists(SAVE_FOLDER):
            os.makedirs(SAVE_FOLDER)

    @staticmethod
    def save(player: Player) -> str:
        """
        Write the player's current state to a JSON file.

        File name format:  PlayerName_YYYYMMDD_HHMMSS.json

        Args:
            player: The player to save

        Returns:
            The filename that was written (not the full path)
        """
        SaveSystem.ensure_folder()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = player.name.replace(" ", "_")
        filename  = f"{safe_name}_{timestamp}.json"
        filepath  = os.path.join(SAVE_FOLDER, filename)
        with open(filepath, "w", encoding="utf-8") as fh:
            json.dump(player.to_dict(), fh, indent=2)
        return filename

    @staticmethod
    def load(filename: str) -> Optional[Player]:
        """
        Load a player from a JSON save file.

        Args:
            filename: Just the file name (not the full path)

        Returns:
            A Player object, or None if the file could not be loaded
        """
        filepath = os.path.join(SAVE_FOLDER, filename)
        if not os.path.exists(filepath):
            return None
        try:
            with open(filepath, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            return Player.from_dict(data)
        except (json.JSONDecodeError, KeyError):
            return None

    @staticmethod
    def list_saves() -> List[str]:
        """Return all save file names, most recent first."""
        SaveSystem.ensure_folder()
        files = [f for f in os.listdir(SAVE_FOLDER) if f.endswith(".json")]
        return sorted(files, reverse=True)




class LifeSimulatorGUI:
    """
    The complete Tkinter GUI application for Life Simulator.

    This class manages three screens:
      1. Main menu  (title + New Game / Load Game / Quit)
      2. Game screen (stats panel + story log + action buttons)
      3. Game over  (final summary + score + outcome)

    All game-rule logic lives in the classes above — this class
    only handles *displaying* information and *reacting* to button clicks.
    """

    def __init__(self):
        """Create the root window, initialise state, and show the main menu."""

        # --- Root window setup ---
        self.root = tk.Tk()
        self.root.title("Life Simulator")
        self.root.configure(bg=C["bg"])
        self.root.resizable(True, True)

        # --- Game state ---
        self.player:       Optional[Player] = None   # Active player (None = no game)
        self.game_active:  bool             = False  # False = ignore button clicks

        # --- Widget references saved for later updates ---
        self.action_buttons: List[tk.Button]    = []
        self.bar_happiness:  Optional[tk.Canvas] = None
        self.bar_health:     Optional[tk.Canvas] = None
        self.bar_education:  Optional[tk.Canvas] = None
        self.story_box:      Optional[tk.Text]   = None

        # --- Tkinter variables bound to labels (auto-update when set) ---
        self.var_age       = tk.StringVar()
        self.var_money     = tk.StringVar()
        self.var_happiness = tk.StringVar()
        self.var_health    = tk.StringVar()
        self.var_education = tk.StringVar()
        self.var_degree    = tk.StringVar()
        self.var_job       = tk.StringVar()
        self.var_business  = tk.StringVar()

        # Open the main menu and hand control to Tkinter
        self._screen_main_menu()
        self.root.mainloop()



    def _clear(self):
        """Destroy every widget inside the root window (used when switching screens)."""
        for w in self.root.winfo_children():
            w.destroy()

    def _btn(self, parent, text: str, cmd,
             width: int = 16, bg: str = None) -> tk.Button:
        """
        Create a flat, dark-themed button with hover colour.

        Args:
            parent: Parent widget
            text:   Label text (may include emoji)
            cmd:    Callback function
            width:  Width in characters
            bg:     Background colour (defaults to the blue accent)

        Returns:
            A configured tk.Button — caller must pack/grid it
        """
        b = tk.Button(
            parent, text=text, command=cmd,
            font=F["btn"], bg=bg or C["btn"],
            fg=C["text"],
            activebackground=C["accent"], activeforeground="white",
            relief="flat", padx=8, pady=7,
            width=width, cursor="hand2", border=0,
        )
        return b

    def _lbl(self, parent, text: str = "", font=None,
             fg: str = None, bg: str = None, **kw) -> tk.Label:
        """Create a tk.Label using dark-theme defaults."""
        return tk.Label(
            parent, text=text,
            font=font or F["normal"],
            fg=fg or C["text"],
            bg=bg or C["panel"],
            **kw,
        )

    # ==========================================================
    # ── SCREEN 1: Main Menu ───────────────────────────────────
    # ==========================================================

    def _screen_main_menu(self):
        """Display the main menu: title, New Game, Load Game, Quit."""
        self._clear()
        self.root.geometry("600x420")
        self.root.title("Life Simulator")
        self.game_active = False

        # Centre the content vertically and horizontally
        frame = tk.Frame(self.root, bg=C["bg"])
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(frame, text="LIFE SIMULATOR",
                 font=F["huge"], fg=C["accent"], bg=C["bg"]).pack(pady=(0, 8))

        tk.Label(frame, text="Make choices  •  Live your life  •  See the results",
                 font=F["normal"], fg=C["muted"], bg=C["bg"]).pack(pady=(0, 44))

        self._btn(frame, "🎮   New Game",  self._screen_new_game,  width=24).pack(pady=8)
        self._btn(frame, "📂   Load Game", self._screen_load_game, width=24).pack(pady=8)
        self._btn(frame, "🚪   Quit",      self.root.quit,
                  width=24, bg="#3a1a1a").pack(pady=8)


    def _screen_new_game(self):
        """Show the name-entry screen and create a new Player when confirmed."""
        self._clear()
        self.root.geometry("500x320")
        self.root.title("Life Simulator — New Game")

        frame = tk.Frame(self.root, bg=C["bg"])
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(frame, text="Create Your Character",
                 font=F["big"], fg=C["accent"], bg=C["bg"]).pack(pady=(0, 20))

        tk.Label(frame, text="What is your character's name?",
                 font=F["normal"], fg=C["text"], bg=C["bg"]).pack()

        name_var = tk.StringVar()
        entry = tk.Entry(
            frame, textvariable=name_var,
            font=("Arial", 14), bg=C["card"], fg=C["text"],
            insertbackground=C["text"], relief="flat", width=24,
        )
        entry.pack(pady=14, ipady=6)
        entry.focus()

        def confirm():
            name = name_var.get().strip()
            if not name:
                messagebox.showwarning("Name Required",
                                       "Please enter a name for your character!")
                return
            self.player = Player(name)
            self._screen_game()

        entry.bind("<Return>", lambda _e: confirm())
        self._btn(frame, "▶   Start Life!", confirm, width=22).pack(pady=10)
        self._btn(frame, "← Back", self._screen_main_menu, width=22,
                  bg=C["card"]).pack(pady=4)

    # ==========================================================
    # ── SCREEN 3: Load Game ───────────────────────────────────
    # ==========================================================

    def _screen_load_game(self):
        """Show a list of save files and resume the one the player picks."""
        saves = SaveSystem.list_saves()
        if not saves:
            messagebox.showinfo("No Saves",
                                "No saved games found!\nStart a new game first.")
            return

        self._clear()
        self.root.geometry("640x460")
        self.root.title("Life Simulator — Load Game")

        frame = tk.Frame(self.root, bg=C["bg"])
        frame.pack(expand=True, fill="both", padx=32, pady=28)

        tk.Label(frame, text="Load a Saved Game",
                 font=F["big"], fg=C["accent"], bg=C["bg"]).pack(pady=(0, 16))

        # Listbox + scrollbar
        lb_frame = tk.Frame(frame, bg=C["bg"])
        lb_frame.pack(fill="both", expand=True)

        sb = tk.Scrollbar(lb_frame)
        sb.pack(side="right", fill="y")

        lb = tk.Listbox(
            lb_frame, font=F["mono"],
            bg=C["card"], fg=C["text"],
            selectbackground=C["accent"],
            height=10, relief="flat",
            yscrollcommand=sb.set,
        )
        lb.pack(side="left", fill="both", expand=True)
        sb.config(command=lb.yview)

        for s in saves:
            lb.insert("end", s)

        def load_selected(_event=None):
            sel = lb.curselection()
            if not sel:
                messagebox.showwarning("Select a Save",
                                       "Please click a save file first!")
                return
            player = SaveSystem.load(saves[sel[0]])
            if player:
                self.player = player
                self._screen_game()
            else:
                messagebox.showerror("Load Failed",
                                     "Could not read that save file.")

        lb.bind("<Double-Button-1>", load_selected)

        btn_row = tk.Frame(frame, bg=C["bg"])
        btn_row.pack(pady=14)
        self._btn(btn_row, "📂  Load Selected", load_selected, width=18).pack(
            side="left", padx=8)
        self._btn(btn_row, "← Back", self._screen_main_menu, width=18,
                  bg=C["card"]).pack(side="left", padx=8)


    def _screen_game(self):
        """Build and display the main gameplay screen."""
        self._clear()
        self.root.geometry("1020x680")
        self.root.title(f"Life Simulator — {self.player.name}")
        self.game_active   = True
        self.action_buttons = []
        self.bar_happiness  = None
        self.bar_health     = None
        self.bar_education  = None

        # ── Top bar ──────────────────────────────────────────
        top = tk.Frame(self.root, bg=C["panel"], height=46)
        top.pack(fill="x")
        top.pack_propagate(False)

        tk.Label(top, text="🎮  LIFE SIMULATOR",
                 font=F["title"], fg=C["accent"], bg=C["panel"]).pack(
            side="left", padx=16, pady=12)

        tk.Label(top, textvariable=self.var_age,
                 font=F["normal"], fg=C["muted"], bg=C["panel"]).pack(
            side="right", padx=16)

        # ── Content row ──────────────────────────────────────
        content = tk.Frame(self.root, bg=C["bg"])
        content.pack(fill="both", expand=True, padx=8, pady=6)

        # Left panel — stats (fixed width)
        left = tk.Frame(content, bg=C["panel"], width=265)
        left.pack(side="left", fill="y", padx=(0, 6))
        left.pack_propagate(False)
        self._build_stats_panel(left)

        # Right panel — story log (takes remaining space)
        right = tk.Frame(content, bg=C["panel"])
        right.pack(side="right", fill="both", expand=True)
        self._build_story_panel(right)

        # ── Bottom action bar ────────────────────────────────
        bottom = tk.Frame(self.root, bg=C["panel"])
        bottom.pack(fill="x", padx=8, pady=(0, 8))
        self._build_action_bar(bottom)

        # Fill in all labels and bars
        self._refresh_stats()

        # Opening message
        if self.player.age == STARTING_AGE:
            intro = (
                f"Welcome, {self.player.name}!  Your life begins at age {STARTING_AGE}. "
                f"You have ${STARTING_MONEY:,} to get started.  "
                f"Each year you pick one action — choose wisely.  "
                f"Retirement waits at age {RETIREMENT_AGE}!"
            )
        else:
            intro = (
                f"Game loaded.  {self.player.name} is age {self.player.age} with "
                f"{RETIREMENT_AGE - self.player.age} years until retirement."
            )
        self._story_add(intro, "welcome")

    # ── Left panel: stats ─────────────────────────────────────

    def _build_stats_panel(self, parent: tk.Frame):
        """
        Populate the left sidebar with the four stat displays,
        three progress bars, and career information.

        Args:
            parent: The left tk.Frame to fill
        """
        pad = {"padx": 14}

        # Section title
        tk.Label(parent, text="📊  STATS",
                 font=F["title"], fg=C["accent"], bg=C["panel"]).pack(
            pady=(14, 4), anchor="w", **pad)

        # Thin accent line under title
        tk.Frame(parent, bg=C["accent"], height=2).pack(
            fill="x", padx=14, pady=(0, 10))

        # ── Money (no bar — just a large number) ─────────────
        tk.Label(parent, text="💰  Money",
                 font=F["small"], fg=C["muted"], bg=C["panel"]).pack(
            anchor="w", **pad)
        tk.Label(parent, textvariable=self.var_money,
                 font=("Arial", 15, "bold"), fg=C["gold"], bg=C["panel"]).pack(
            anchor="w", padx=14, pady=(2, 12))

        # ── Happiness, Health, Education bars ────────────────
        self.bar_happiness = self._make_stat_row(
            parent, "😊  Happiness", self.var_happiness, C["blue"])

        self.bar_health = self._make_stat_row(
            parent, "❤️   Health", self.var_health, C["green"])

        self.bar_education = self._make_stat_row(
            parent, "📚  Education", self.var_education, C["purple"])

        # Divider
        tk.Frame(parent, bg=C["border"], height=1).pack(
            fill="x", padx=14, pady=12)

        # ── Career information ────────────────────────────────
        for label_text, var, col in [
            ("🎓  Degree",   self.var_degree,   C["text"]),
            ("💼  Job",      self.var_job,       C["text"]),
            ("🏢  Business", self.var_business,  C["green"]),
        ]:
            tk.Label(parent, text=label_text,
                     font=F["small"], fg=C["muted"], bg=C["panel"]).pack(
                anchor="w", padx=14)
            tk.Label(parent, textvariable=var,
                     font=F["normal"], fg=col, bg=C["panel"],
                     wraplength=230, justify="left").pack(
                anchor="w", padx=14, pady=(2, 8))

    def _make_stat_row(self, parent: tk.Frame, label: str,
                       var: tk.StringVar, bar_color: str) -> tk.Canvas:
        """
        Add one stat block: a label row (text left, value right)
        and a coloured Canvas progress bar below it.

        Args:
            parent:    Frame to add into
            label:     Stat name (e.g. "😊  Happiness")
            var:       StringVar holding the "72 / 100" text
            bar_color: Fill colour for the bar

        Returns:
            The Canvas widget so we can redraw it when the stat changes
        """
        row = tk.Frame(parent, bg=C["panel"])
        row.pack(fill="x", padx=14, pady=(0, 2))

        tk.Label(row, text=label,
                 font=F["small"], fg=C["muted"], bg=C["panel"]).pack(side="left")
        tk.Label(row, textvariable=var,
                 font=F["small"], fg=bar_color, bg=C["panel"]).pack(side="right")

        canvas = tk.Canvas(parent, height=10, bg=C["card"],
                           highlightthickness=0, relief="flat")
        canvas.pack(fill="x", padx=14, pady=(0, 12))
        canvas.bar_color = bar_color   # stored for use in _draw_bar
        # Redraw when the canvas is resized (e.g. user resizes window)
        canvas.bind("<Configure>",
                    lambda _e: self._draw_bar(canvas,
                        self._bar_value_from_var(var)))
        return canvas

    @staticmethod
    def _bar_value_from_var(var: tk.StringVar) -> int:
        """
        Extract the integer value from a StringVar like '72 / 100'.

        Args:
            var: StringVar holding 'VALUE / 100' text

        Returns:
            The integer value, or 0 if parsing fails
        """
        try:
            return int(var.get().split("/")[0].strip())
        except (ValueError, AttributeError):
            return 0

    def _draw_bar(self, canvas: tk.Canvas, value: int):
        """
        Redraw a progress bar canvas to show the given value (0-100).

        Args:
            canvas: The Canvas bar to update
            value:  Current stat value
        """
        canvas.update_idletasks()
        w = canvas.winfo_width()
        if w < 5:
            w = 220   # Fallback before the window is fully laid out

        # Clamp value to 0-100 range
        value = max(0, min(100, value))
        filled = int((value / 100) * w)

        canvas.delete("all")
        # Background track
        canvas.create_rectangle(0, 0, w, 10, fill=C["card"], outline="")
        # Filled portion
        if filled > 0:
            canvas.create_rectangle(0, 0, filled, 10,
                                    fill=canvas.bar_color, outline="")

    def _redraw_bars(self):
        """Redraw all three progress bars from the player's current stats."""
        if not self.player:
            return
        s = self.player.stats
        if self.bar_happiness:
            self._draw_bar(self.bar_happiness, s.happiness)
        if self.bar_health:
            self._draw_bar(self.bar_health,    s.health)
        if self.bar_education:
            self._draw_bar(self.bar_education, s.education)

    # ── Right panel: story log ────────────────────────────────

    def _build_story_panel(self, parent: tk.Frame):
        """
        Build the scrollable text area that shows the life narrative.

        Args:
            parent: The right panel frame
        """
        tk.Label(parent, text="📖  Your Life Story",
                 font=F["title"], fg=C["accent"], bg=C["panel"]).pack(
            padx=12, pady=(12, 6), anchor="w")

        wrap = tk.Frame(parent, bg=C["panel"])
        wrap.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        sb = tk.Scrollbar(wrap)
        sb.pack(side="right", fill="y")

        self.story_box = tk.Text(
            wrap,
            font=F["normal"], bg=C["bg"], fg=C["text"],
            wrap="word", relief="flat",
            padx=12, pady=10,
            yscrollcommand=sb.set,
            state="disabled",   # Read-only; we unlock briefly when inserting text
        )
        self.story_box.pack(side="left", fill="both", expand=True)
        sb.config(command=self.story_box.yview)

        # Colour tags — used as the second argument in _story_add
        tags = {
            "welcome":    C["teal"],
            "year_hdr":   C["accent"],
            "action":     C["orange"],
            "yearly":     C["muted"],
            "good_event": C["teal"],
            "bad_event":  C["red"],
            "narrative":  C["text"],
            "info":       C["muted"],
        }
        for tag_name, colour in tags.items():
            self.story_box.tag_configure(tag_name, foreground=colour)

    def _story_add(self, text: str, tag: str = "narrative"):
        """
        Append a line of text to the story log and scroll to the bottom.

        Args:
            text: The text to add
            tag:  Colour tag (must match one configured above)
        """
        self.story_box.config(state="normal")
        self.story_box.insert("end", text + "\n", tag)
        self.story_box.config(state="disabled")
        self.story_box.see("end")

    # ── Bottom: action buttons ────────────────────────────────

    def _build_action_bar(self, parent: tk.Frame):
        """
        Build two button rows at the bottom of the screen:
        Row 1 — five year-action buttons
        Row 2 — Save Game and Main Menu

        Args:
            parent: The bottom frame
        """
        tk.Label(parent, text="  Choose your action for this year:",
                 font=F["normal"], fg=C["muted"], bg=C["panel"]).pack(
            anchor="w", pady=(8, 4))

        row1 = tk.Frame(parent, bg=C["panel"])
        row1.pack(fill="x", padx=8, pady=2)

        # Button colour per action type — makes the UI more readable
        action_defs = [
            ("📚  University", "university", "#1a3a6e"),
            ("💼  Get Job",    "job",        "#2d1a5e"),
            ("🏢  Business",   "business",   "#4a2500"),
            ("✈️   Travel",    "travel",     "#004d4d"),
            ("😌  Rest",       "rest",       "#1a4a1a"),
        ]
        for label, action_key, btn_color in action_defs:
            btn = self._btn(row1, label,
                            lambda a=action_key: self._do_action(a),
                            width=14, bg=btn_color)
            btn.pack(side="left", padx=4, pady=4)
            self.action_buttons.append(btn)

        row2 = tk.Frame(parent, bg=C["panel"])
        row2.pack(fill="x", padx=8, pady=(0, 8))

        self._btn(row2, "💾  Save Game",  self._save_game,           width=16).pack(
            side="left", padx=4)
        self._btn(row2, "🏠  Main Menu",  self._confirm_quit_to_menu, width=16,
                  bg=C["card"]).pack(side="left", padx=4)


    def _refresh_stats(self):
        """Update every label and progress bar to match the player's current stats."""
        p = self.player
        years_left = max(0, RETIREMENT_AGE - p.age)

        self.var_age.set(
            f"{p.name}  |  Age {p.age}  |  {years_left} years to retirement")
        self.var_money.set(f"${p.stats.money:,.0f}")
        self.var_happiness.set(f"{p.stats.happiness} / 100")
        self.var_health.set(f"{p.stats.health} / 100")
        self.var_education.set(f"{p.stats.education} / 100")
        self.var_degree.set(p.get_degree_name())
        self.var_job.set(
            f"{p.current_job}\n${p.job_salary:,.0f} / year"
            if p.current_job else "None")
        self.var_business.set(
            f"Active  (+${p.business_income:,.0f} / yr)"
            if p.has_business else "None")

        self._redraw_bars()



    def _set_buttons(self, enabled: bool):
        """Enable or disable all five action buttons."""
        state = "normal" if enabled else "disabled"
        for btn in self.action_buttons:
            btn.config(state=state)

    def _do_action(self, action_type: str):
        """
        Called when the player clicks one of the five action buttons.

        Flow:
          1. Validate and apply the chosen action
          2. Apply automatic yearly effects
          3. Maybe trigger a random event (40% chance)
          4. Generate the story narrative
          5. Refresh the display
          6. Check game-over conditions

        Args:
            action_type: One of 'university', 'job', 'business', 'travel', 'rest'
        """
        if not self.game_active:
            return

        self._set_buttons(False)

        # --- Resolve the chosen action ---
        if action_type == "university":
            result = Actions.go_to_university(self.player)

        elif action_type == "job":
            result = self._dialog_job()
            if result is None:           # Player cancelled the job dialog
                self._set_buttons(True)
                return

        elif action_type == "business":
            result = Actions.start_business(self.player)

        elif action_type == "travel":
            result = Actions.travel(self.player)

        else:                            # "rest"
            result = Actions.rest_and_relax(self.player)

        # --- Action blocked? Show why and stop ---
        if not result.success:
            messagebox.showwarning("Can't Do That", result.message)
            self._set_buttons(True)
            return

        # --- Show year header and action outcome in the story log ---
        self._story_add(
            f"\n{'─' * 40}  Age {self.player.age}  {'─' * 3}", "year_hdr")
        self._story_add(f"✅  {result.message}", "action")

        # --- Apply automatic yearly effects ---
        year_msgs = self.player.apply_yearly_effects()
        for msg in year_msgs:
            self._story_add(f"   • {msg}", "yearly")

        # --- Random event (40% chance) ---
        event = EventSystem.roll()
        if event:
            self.player.apply_event(event)
            self._popup_event(event)      # Show modal popup; blocks until dismissed

            if event.is_positive:
                self._story_add(
                    f"🎉  {event.name}: {event.description}", "good_event")
            else:
                self._story_add(
                    f"⚠️   {event.name}: {event.description}", "bad_event")

        # --- Narrative story paragraph ---
        story = StoryGenerator.generate(self.player, result, event)
        self._story_add(f"\n📖  {story}\n", "narrative")

        # --- Refresh all stats labels and bars ---
        self._refresh_stats()

        # --- Check game-over conditions ---
        game_over = (not self.player.is_alive) or (self.player.age >= RETIREMENT_AGE)
        if game_over:
            if self.player.age >= RETIREMENT_AGE:
                self.player.end_reason = "retirement"
            self.game_active = False
            self._set_buttons(False)
            # Small delay so the player can read the last story entry
            self.root.after(900, self._screen_game_over)
            return

        self._set_buttons(True)

    # ── Job-selection dialog ──────────────────────────────────

    def _dialog_job(self) -> Optional[ActionResult]:
        """
        Open a modal dialog listing all four jobs for the player to choose.

        Returns:
            An ActionResult if a job was chosen, or None if cancelled
        """
        dialog = tk.Toplevel(self.root)
        dialog.title("Choose a Job")
        dialog.geometry("510x410")
        dialog.configure(bg=C["bg"])
        dialog.transient(self.root)
        dialog.grab_set()    # Block clicks on the main window while open

        result_holder: List[Optional[ActionResult]] = [None]

        tk.Label(dialog, text="Choose Your Job",
                 font=F["big"], fg=C["accent"], bg=C["bg"]).pack(pady=(20, 14))

        jobs_frame = tk.Frame(dialog, bg=C["bg"])
        jobs_frame.pack(fill="both", expand=True, padx=22)

        for job_name, info in JOBS.items():
            req       = EDU_NAMES[info["min_edu"]]
            qualified = self.player.education_level >= info["min_edu"]

            card = tk.Frame(jobs_frame, bg=C["card"], pady=8)
            card.pack(fill="x", pady=4)

            # Capture job_name and qualified in the closure correctly
            def make_cmd(jn=job_name, q=qualified):
                def _go():
                    if not q:
                        messagebox.showwarning(
                            "Not Qualified",
                            f"You need a {EDU_NAMES[JOBS[jn]['min_edu']]} "
                            f"for this job.")
                        return
                    result_holder[0] = Actions.get_a_job(self.player, jn)
                    dialog.destroy()
                return _go

            fg = C["text"] if qualified else C["muted"]
            tk.Button(
                card,
                text=f"{job_name}  —  ${info['salary']:,} / year",
                command=make_cmd(),
                font=F["normal"], bg=C["card"], fg=fg,
                relief="flat", padx=10, pady=5,
                width=36, anchor="w", cursor="hand2",
                activebackground=C["btn"], activeforeground="white",
                border=0,
            ).pack(padx=10, fill="x")

            tk.Label(
                card,
                text=f"   Requires: {req}  |  "
                     f"Happiness {info['happiness']:+d}  |  "
                     f"Health {info['health']:+d}",
                font=F["small"], fg=C["muted"], bg=C["card"],
            ).pack(anchor="w", padx=10)

        self._btn(dialog, "Cancel", dialog.destroy,
                  width=14, bg=C["card"]).pack(pady=14)

        self.root.wait_window(dialog)   # Block until the dialog closes
        return result_holder[0]

    # ── Random-event popup ────────────────────────────────────

    def _popup_event(self, event: Event):
        """
        Show a styled popup that describes the random event and its stat effects.
        The player must click 'Continue' to dismiss it.

        Args:
            event: The event that triggered this year
        """
        popup = tk.Toplevel(self.root)
        popup.title("Life Event!")
        popup.geometry("420x310")
        popup.configure(bg=C["bg"])
        popup.transient(self.root)
        popup.grab_set()

        # Different header colour for good vs bad events
        if event.is_positive:
            icon, hdr_col = "🎉", C["teal"]
        else:
            icon, hdr_col = "⚠️ ", C["red"]

        tk.Label(popup, text=f"{icon}  {event.name}",
                 font=F["big"], fg=hdr_col, bg=C["bg"]).pack(pady=(22, 10))

        tk.Label(popup, text=event.description,
                 font=F["normal"], fg=C["text"], bg=C["bg"],
                 wraplength=370, justify="center").pack(pady=(0, 18))

        # Stat effects card
        effects_frame = tk.Frame(popup, bg=C["card"], padx=24, pady=12)
        effects_frame.pack(padx=36, fill="x")

        # Only show stats that actually changed
        effect_rows = [
            ("Money",     event.money_change,     C["gold"]),
            ("Happiness", event.happiness_change, C["blue"]),
            ("Health",    event.health_change,    C["green"]),
            ("Education", event.education_change, C["purple"]),
        ]
        for label, value, colour in effect_rows:
            if value == 0:
                continue
            if label == "Money":
                # Money is a float — format with $ sign
                val_str = (f"+${value:,.0f}" if value > 0
                           else f"-${abs(value):,.0f}")
            else:
                val_str = f"{int(value):+d}"

            tk.Label(effects_frame,
                     text=f"{label}:  {val_str}",
                     font=F["normal"], fg=colour, bg=C["card"],
                     anchor="w").pack(anchor="w")

        self._btn(popup, "Continue  ▶", popup.destroy, width=16).pack(pady=20)
        self.root.wait_window(popup)


    def _save_game(self):
        """Save the current game and show a confirmation popup."""
        if not self.player:
            messagebox.showwarning("No Game", "No active game to save!")
            return
        filename = SaveSystem.save(self.player)
        messagebox.showinfo("Game Saved ✅",
                            f"Your game was saved!\n\nFile:  {filename}")

    def _confirm_quit_to_menu(self):
        """Ask the player to confirm before going back to the main menu."""
        if messagebox.askyesno(
            "Return to Menu",
            "Go back to the main menu?\nAny unsaved progress will be lost.",
        ):
            self.game_active = False
            self._screen_main_menu()


    def _screen_game_over(self):
        """Display the final life-summary screen with score and outcome."""
        self._clear()
        self.root.geometry("740x680")
        self.root.title("Life Simulator — Game Over")
        p = self.player

        # ── Scrollable container ──────────────────────────────
        outer = tk.Frame(self.root, bg=C["bg"])
        outer.pack(fill="both", expand=True)

        cv = tk.Canvas(outer, bg=C["bg"], highlightthickness=0)
        sb = tk.Scrollbar(outer, orient="vertical", command=cv.yview)
        cv.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        cv.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(cv, bg=C["bg"])
        win_id = cv.create_window((0, 0), window=inner, anchor="nw")

        def _on_resize(_e=None):
            cv.configure(scrollregion=cv.bbox("all"))
            cv.itemconfig(win_id, width=cv.winfo_width())

        inner.bind("<Configure>", _on_resize)
        cv.bind("<Configure>",    _on_resize)

        # ── End-reason title ──────────────────────────────────
        if p.end_reason == "retirement":
            title, tcol = "🎉  You Reached Retirement!", C["teal"]
        elif p.end_reason == "health":
            title, tcol = "💀  Your Health Gave Out", C["red"]
        else:
            title, tcol = "😔  You Lost the Will to Continue", C["orange"]

        tk.Label(inner, text=title,
                 font=F["big"], fg=tcol, bg=C["bg"]).pack(pady=(26, 4))

        tk.Label(inner, text=f"The Life of {p.name}",
                 font=F["title"], fg=C["muted"], bg=C["bg"]).pack(pady=(0, 18))

        # ── Stats summary card ────────────────────────────────
        card = tk.Frame(inner, bg=C["card"], padx=30, pady=20)
        card.pack(fill="x", padx=48, pady=4)

        stat_rows = [
            (f"Final Age:       {p.age}",                   C["text"]),
            (f"Years Lived:     {p.age - STARTING_AGE}",    C["text"]),
            ("",                                             C["text"]),  # spacer
            (f"💰  Money:       ${p.stats.money:,.0f}",      C["gold"]),
            (f"😊  Happiness:   {p.stats.happiness} / 100", C["blue"]),
            (f"❤️   Health:      {p.stats.health} / 100",   C["green"]),
            (f"📚  Education:   {p.stats.education} / 100", C["purple"]),
            (f"🎓  Degree:      {p.get_degree_name()}",      C["text"]),
        ]
        for txt, col in stat_rows:
            tk.Label(card, text=txt, font=F["normal"],
                     fg=col, bg=C["card"], anchor="w").pack(anchor="w")

        # ── Score ─────────────────────────────────────────────
        score = p.calculate_score()
        tk.Label(inner, text=f"Final Score:  {score}",
                 font=("Arial", 22, "bold"), fg=C["accent"], bg=C["bg"]).pack(
            pady=(18, 6))

        tk.Label(inner, text=p.get_life_outcome(),
                 font=F["normal"], fg=C["teal"], bg=C["bg"],
                 wraplength=580, justify="center").pack(pady=(0, 16))

        # ── Major life events ─────────────────────────────────
        if p.history:
            tk.Label(inner, text="Major Life Events (last 10)",
                     font=F["title"], fg=C["muted"], bg=C["bg"]).pack(
                pady=(6, 4))

            hist_card = tk.Frame(inner, bg=C["card"], padx=22, pady=12)
            hist_card.pack(fill="x", padx=48, pady=(0, 4))

            for entry in p.history[-10:]:
                tk.Label(hist_card, text=f"  •  {entry}",
                         font=F["normal"], fg=C["text"], bg=C["card"],
                         anchor="w").pack(anchor="w")

        # ── End buttons ───────────────────────────────────────
        btn_row = tk.Frame(inner, bg=C["bg"])
        btn_row.pack(pady=22)

        self._btn(btn_row, "🔄  Play Again",
                  self._screen_new_game, width=18).pack(side="left", padx=10)

        self._btn(btn_row, "🏠  Main Menu",
                  self._screen_main_menu, width=18,
                  bg=C["card"]).pack(side="left", padx=10)


def main():
    """Create and run the Life Simulator GUI application."""
    LifeSimulatorGUI()


if __name__ == "__main__":
    main()
