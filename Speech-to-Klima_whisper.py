import whisper
import torch
import ffmpeg

#Load model and audio
model = whisper.load_model('tiny')
audio = whisper.load_audio('data/niko_planung.mp3')
audio = whisper.pad_or_trim(audio)

mel = whisper.log_mel_spectrogram(audio).to(model.device)

#Detect the language
_, probs = model.detect_language(mel)
print(f"Detected Language: {max(probs, key=probs.get)}")

# decode the audio
options = whisper.DecodingOptions()
result = whisper.decode(model, mel, options)

# print the recognized text
print(result.text)

import re
detected_text = result.text.lower()

def GetRegexTime(text):
   hour_pattern = re.compile(r'(\w+)\s*stunde(n)?')
   minute_pattern = re.compile(r'(\w+)\s*minute(n)?')
   second_pattern = re.compile(r'(\w+)\s*sekunde(n)?')
   hour_match = hour_pattern.search(text)
   minute_match = minute_pattern.search(text)
   second_match = second_pattern.search(text)
   # Die Zahl aus dem Regex herausziehen Gruppe 1 = (|d+) Gruppe 2 = n
   hours = hour_match.group(1) if hour_match else 0
   minutes = minute_match.group(1) if minute_match else 0
   seconds = second_match.group(1) if second_match else 0

   return hours, minutes, seconds

def GetRegexIntensity(text):
  intensity_pattern = re.compile(r'(\d+)\s*(prozent?|%)')
  intensity_match = intensity_pattern.search(text)
  intensity = int(intensity_match.group(1)) if intensity_match else None
  return intensity

def GetRegexPlace(text):
  place_pattern = re.compile(r'(\bin\b|\bvon\b|\baus\b)\s*(\w+)')
  place_match = place_pattern.search(text)
  place = place_match.group(2) if place_match else ""
  return place

keywords = ["sonne", "regen", "temperatur", "luftfeuchtigkeit"]
detected_numbers = re.findall(r'\d+', detected_text)
numbers = [int(num) for num in detected_numbers]
print(f"numbers: {numbers}")

def GetCommandType(text):
  ContainKeyword = False
  if "in" in text:
    for keyword in keywords:
      if keyword in text:
        ContainKeyword = True
    commandType = 0 if ContainKeyword else 2
  else:
    commandType = 1
  return commandType

def GetFeature(text):
  features = []
  for keyword in keywords:
    if keyword in text:
      features.append(keyword)
  return features

def TimeToNumerical3(time):
  try:
    time = int(time)
    return time
  except ValueError:
    if time == "null":
      time = 0
    if time == "einer":
      time = 1
    if time == "zwei":
      time = 2
    if time == "drei":
      time = 3
    if time == "vier":
      time = 4
    if time == "fünf":
      time = 5
    if time == "sechs":
      time = 6
    if time == "sieben":
      time = 7
    if time == "acht":
      time = 8
    if time == "neun":
      time = 9
    if time == "zehn":
      time = 10
    if time == "elf":
      time = 11
    if time == "zwölf":
      time = 12
    if time == "dreizehn":
      time = 13
    if time == "vierzehn":
      time = 14
    if time == "fünfzehn":
      time = 15
    if time == "sechzehn":
      time = 16
    if time == "siebzehn":
      time = 17
    if time == "achtzehn":
      time = 18
    if time == "neunzehn":
      time = 19
    if time == "zwanzig":
      time = 20

    return time
  
CommandType = GetCommandType(detected_text)
print(f"Command Type: {CommandType}")

Features = GetFeature(detected_text)
print(f"Feature: {Features}")

Intensity = GetRegexIntensity(detected_text)
print(f"Intensity: {Intensity}")

hours, minutes, seconds = GetRegexTime(detected_text)
hours = TimeToNumerical3(hours)
minutes = TimeToNumerical3(minutes)
seconds = TimeToNumerical3(seconds)
print(f"hours: {hours}")
print(f"minutes: {minutes}")
print(f"seconds: {seconds}")
relative_unixTime = (hours*60+minutes)*60+seconds
print(f"unix time: {relative_unixTime}")

Place = None
if CommandType == 2:
  Place = GetRegexPlace(detected_text)
print(f"Place: {Place}")

import json
dictionary = {
    "command": CommandType,
    "feature": Features[0],
    "data":[
        {
          "value": Intensity,
          "Time": relative_unixTime
        },
        {
          "value": Intensity
        },
        {
          "place": Place
        }
    ]
}
json_object = json.dumps(dictionary, indent=0)
with open("outputs/sample.json", "w") as outfile:
    outfile.write(json_object)
