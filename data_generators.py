"""Generate fake user data for simulation."""
import random
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dataclasses import dataclass, asdict

@dataclass
class CalendarEvent:
    time: str
    title: str
    description: str
    duration_minutes: int

@dataclass
class Email:
    time: str
    subject: str
    body: str
    sender: str
    priority: str

@dataclass
class FitnessMetric:
    time: str
    steps: int
    heart_rate: int
    calories_burned: int
    activity_type: str

@dataclass
class MusicPreference:
    time: str
    track_name: str
    artist: str
    genre: str
    mood: str

class DataGenerator:
    """Generate realistic fake data for a simulated day."""
    
    def __init__(self):
        self.calendar_templates = [
            ("Meeting", "Project deadline discussion", 60),
            ("Standup", "Daily team sync", 30),
            ("Lunch", "Team lunch at restaurant", 60),
            ("Review", "Code review session", 45),
            ("Presentation", "Client demo preparation", 90),
            ("Break", "Coffee break", 15),
            ("Workout", "Gym session", 60),
            ("Dinner", "Family dinner", 90),
        ]
        
        self.email_templates = [
            ("Urgent update", "I'm feeling stressed about the deadline. Can we discuss?", "colleague@company.com", "high"),
            ("Project status", "Everything is on track. Great work team!", "manager@company.com", "normal"),
            ("Meeting reminder", "Don't forget about our meeting at 3pm", "assistant@company.com", "normal"),
            ("Wellness check", "How are you doing? Haven't heard from you in a while.", "friend@email.com", "low"),
            ("Newsletter", "Weekly tech updates and industry news", "newsletter@tech.com", "low"),
        ]
        
        self.music_genres = ["pop", "rock", "electronic", "jazz", "classical", "hip-hop"]
        self.music_moods = ["upbeat", "calm", "energetic", "relaxing", "focused", "motivational"]
        self.track_names = [
            "Midnight Dreams", "Electric Pulse", "Ocean Waves", "City Lights",
            "Mountain Peak", "Desert Wind", "Starlight", "Thunderstorm"
        ]
        self.artists = [
            "The Beats", "Sound Waves", "Digital Dreams", "Acoustic Soul",
            "Neon Nights", "Crystal Clear", "Echo Valley", "Sky High"
        ]
    
    def generate_calendar_events(self, start_hour: int = 9, num_events: int = 5) -> List[CalendarEvent]:
        """Generate calendar events for a day."""
        events = []
        current_time = datetime.now().replace(hour=start_hour, minute=0, second=0, microsecond=0)
        
        for _ in range(num_events):
            template = random.choice(self.calendar_templates)
            event = CalendarEvent(
                time=current_time.strftime("%Y-%m-%d %H:%M:%S"),
                title=template[0],
                description=template[1],
                duration_minutes=template[2]
            )
            events.append(event)
            current_time += timedelta(minutes=template[2] + random.randint(15, 60))
        
        return events
    
    def generate_emails(self, num_emails: int = 8) -> List[Email]:
        """Generate emails throughout the day."""
        emails = []
        start_time = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
        
        for _ in range(num_emails):
            template = random.choice(self.email_templates)
            email = Email(
                time=start_time.strftime("%Y-%m-%d %H:%M:%S"),
                subject=template[0],
                body=template[1],
                sender=template[2],
                priority=template[3]
            )
            emails.append(email)
            start_time += timedelta(hours=random.randint(1, 3), minutes=random.randint(0, 59))
        
        return emails
    
    def generate_fitness_metrics(self, num_readings: int = 6) -> List[FitnessMetric]:
        """Generate fitness metrics throughout the day."""
        metrics = []
        start_time = datetime.now().replace(hour=7, minute=0, second=0, microsecond=0)
        base_steps = 0
        
        activities = ["walking", "running", "cycling", "gym", "yoga", "rest"]
        
        for _ in range(num_readings):
            activity = random.choice(activities)
            steps_increment = random.randint(500, 3000) if activity != "rest" else random.randint(0, 500)
            base_steps += steps_increment
            
            metric = FitnessMetric(
                time=start_time.strftime("%Y-%m-%d %H:%M:%S"),
                steps=base_steps,
                heart_rate=random.randint(60, 180) if activity != "rest" else random.randint(60, 80),
                calories_burned=random.randint(50, 500),
                activity_type=activity
            )
            metrics.append(metric)
            start_time += timedelta(hours=random.randint(2, 4))
        
        return metrics
    
    def generate_music_preferences(self, num_tracks: int = 10) -> List[MusicPreference]:
        """Generate music listening history."""
        preferences = []
        start_time = datetime.now().replace(hour=6, minute=0, second=0, microsecond=0)
        
        for _ in range(num_tracks):
            preference = MusicPreference(
                time=start_time.strftime("%Y-%m-%d %H:%M:%S"),
                track_name=random.choice(self.track_names),
                artist=random.choice(self.artists),
                genre=random.choice(self.music_genres),
                mood=random.choice(self.music_moods)
            )
            preferences.append(preference)
            start_time += timedelta(minutes=random.randint(15, 120))
        
        return preferences
    
    def generate_day_data(self) -> Dict[str, Any]:
        """Generate complete day data."""
        return {
            "calendar": [asdict(e) for e in self.generate_calendar_events()],
            "emails": [asdict(e) for e in self.generate_emails()],
            "fitness": [asdict(f) for f in self.generate_fitness_metrics()],
            "music": [asdict(m) for m in self.generate_music_preferences()],
            "timestamp": datetime.now().isoformat()
        }
    
    def save_day_data(self, filename: str = "simulated_day.json"):
        """Save generated data to JSON file."""
        data = self.generate_day_data()
        filepath = f"data/{filename}"
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        return filepath

