import json
import os
import librosa
import numpy as np
from typing import List, Tuple, Dict, Any

class BeatDetector:
    def __init__(self, audio_path: str, draft_content_path: str):
        """
        Initialize BeatDetector with audio file and draft_content.json paths
        
        Args:
            audio_path: Path to the audio file
            draft_content_path: Path to draft_content.json
        """
        self.audio_path = audio_path
        self.draft_content_path = draft_content_path
        self.beat_times: List[float] = []
        self.beat_values: List[int] = []
        
    def detect_beats(self, bpm: float = None) -> Tuple[List[float], List[int]]:
        """
        Detect beats in the audio file using librosa
        
        Args:
            bpm: Optional BPM hint for beat detection
            
        Returns:
            Tuple of (beat_times, beat_values)
        """
        # Load audio file
        y, sr = librosa.load(self.audio_path)
        
        # Detect tempo and beats
        if bpm:
            tempo = bpm
            beat_frames = librosa.beat.beat_track(y=y, sr=sr, bpm=bpm)[1]
        else:
            tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
            
        # Convert beat frames to time (in milliseconds)
        self.beat_times = librosa.frames_to_time(beat_frames, sr=sr) * 1000
        
        # Generate beat values (1-4 for a 4/4 time signature)
        self.beat_values = [(i % 4) + 1 for i in range(len(self.beat_times))]
        
        return self.beat_times, self.beat_values
        
    def save_beat_file(self, output_path: str) -> str:
        """
        Save beat detection results to a .beat file
        
        Args:
            output_path: Directory to save the .beat file
            
        Returns:
            Path to the saved .beat file
        """
        beat_data = {
            "time": [int(t) for t in self.beat_times],
            "value": self.beat_values
        }
        
        # Generate beat file path
        audio_filename = os.path.splitext(os.path.basename(self.audio_path))[0]
        beat_file_path = os.path.join(output_path, f"{audio_filename}.beat")
        
        # Save beat file
        with open(beat_file_path, 'w') as f:
            json.dump(beat_data, f, indent=4)
            
        return beat_file_path
        
    def update_draft_content(self, beat_file_path: str) -> None:
        """
        Update draft_content.json with beat detection results
        
        Args:
            beat_file_path: Path to the .beat file
        """
        # Read draft_content.json
        with open(self.draft_content_path, 'r', encoding='utf-8') as f:
            draft_content = json.load(f)
            
        # Find the beats material
        beats_material = None
        for material in draft_content['materials']['beats']:
            if material['type'] == 'beats':
                beats_material = material
                break
                
        if not beats_material:
            raise ValueError("No beats material found in draft_content.json")
            
        # Update beats material
        beats_material.update({
            "ai_beats": {
                "beat_speed_infos": [],
                "beats_path": beat_file_path,
                "beats_url": "",
                "melody_path": "",
                "melody_percents": [0.0, 0.6],
                "melody_url": ""
            },
            "enable_ai_beats": True,
            "gear": 0,
            "gear_count": 2,
            "mode": 1,
            "user_beats": [],
            "user_delete_ai_beats": {
                "beat_0": [],
                "beat_1": [],
                "beat_2": [],
                "beat_3": [],
                "beat_4": [],
                "melody_0": []
            }
        })
        
        # Save updated draft_content.json
        with open(self.draft_content_path, 'w', encoding='utf-8') as f:
            json.dump(draft_content, f, indent=2)
            
    def process(self, output_dir: str, bpm: float = None) -> str:
        """
        Process audio file: detect beats, save beat file, and update draft_content.json
        
        Args:
            output_dir: Directory to save the .beat file
            bpm: Optional BPM hint for beat detection
            
        Returns:
            Path to the saved .beat file
        """
        # Detect beats
        self.detect_beats(bpm)
        
        # Save beat file
        beat_file_path = self.save_beat_file(output_dir)
        
        # Update draft_content.json
        self.update_draft_content(beat_file_path)
        
        return beat_file_path 