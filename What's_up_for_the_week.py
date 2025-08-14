# Import libraries
import os
from google import genai
from google.genai import types
import requests
import random
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# List of office locations
cities = ["Vancouver - Head Office", "Calgary", "Toronto", "Dublin"]
addresses = {"Vancouver - Head Office": "Suite 300, 4611 Canada Way, Burnaby, BC, V5G 4X3, Canada",
            "Calgary": "Suite 2500, 150 9th Avenue Southwest, Calgary, AB, T2P 3H9, Canada",
            "Toronto": "30th Floor, 16 York Street, Toronto, ON, M5J 0E6, Canada",
            "Dublin": "1st Floor, Fumbally Studios, Fumbally Lane, Dublin 8, Ireland"}
addresses_google = {"Vancouver - Head Office": "https://maps.app.goo.gl/RoodrZS65rcpnrUh7",
                  "Calgary": "https://maps.app.goo.gl/PzXHmzkNQUaXjiEg8",
                  "Toronto": "https://maps.app.goo.gl/uXRWgg9rufNVToev9",
                  "Dublin": "https://maps.app.goo.gl/ay2p62k3bP5ca4Fz5"}
coordinates = {"Vancouver - Head Office": {"latitude":49.25610802806419, "longitude": -122.99496835397048},
                  "Calgary": {"latitude": 51.045131096271355, "longitude": -114.06487835767157},
                  "Toronto": {"latitude": 43.64280134199292, "longitude": -79.3819525288358},  
                  "Dublin": {"latitude": 53.337035192957586, "longitude": -6.273515026926611}}
# Randomly select an office and its location
random_num = random.randint(0, 3)
city = cities[random_num]
address = addresses[city]
address_google = addresses_google[city]
coordinate = coordinates[city]
# Check what day is today
now = datetime.now()
today = now.strftime('%A, %B %d, %Y')

############################################################################################################
# Connect to a API and get the weather forecast
url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": round(coordinate['latitude'], 4),
    "longitude": round(coordinate['longitude'], 4),
    "hourly": ["temperature_2m", "precipitation_probability", "precipitation"],
    "timezone": "auto",
    "forecast_days": 4
}
weather_data = requests.get(url, params).json()

# Extract time and temperature data
times = weather_data['hourly']['time']
temperatures = weather_data['hourly']['temperature_2m']
precipitation_prob = weather_data['hourly']['precipitation_probability']
precipitation_mm = weather_data['hourly']['precipitation']

# Convert time strings to datetime objects
datetime_objects = [datetime.fromisoformat(time) for time in times]

# Create the plot with dual y-axes
fig, ax1 = plt.subplots(figsize=(15, 8))

# Plot temperature on the left y-axis
color1 = '#ff6b35'
ax1.set_xlabel('Date and Time', fontsize=12)
ax1.set_ylabel('Temperature (°C)', color=color1, fontsize=12)
line1 = ax1.plot(datetime_objects, temperatures, linewidth=2, color=color1, label='Temperature')
ax1.tick_params(axis='y', labelcolor=color1)

# Create second y-axis for precipitation probability and precipitation
ax2 = ax1.twinx()
color2 = '#4a90e2'
color3 = '#2ecc71'

# Plot precipitation probability as a line
ax2.set_ylabel('Precipitation Probability (%) / Precipitation (1/10 mm)', color=color2, fontsize=12)
line2 = ax2.plot(datetime_objects, precipitation_prob, linewidth=2, color=color2, alpha=0.7, label='Precipitation Probability (%)')

# Add precipitation bars with color coding based on intensity
precipitation_scaled = [p * 10 for p in precipitation_mm]  # Scale by 10 for visibility

# Create color list based on precipitation intensity
bar_colors = []
for p in precipitation_mm:
    if p == 0:
        bar_colors.append('none')  # No color for no precipitation
    elif p < 2.5:
        bar_colors.append('#87CEEB')  # Light blue for light rain (< 2.5 mm/hr)
    elif p <= 7.5:
        bar_colors.append('#4682B4')  # Darker blue for moderate rain (2.5-7.5 mm/hr)
    else:
        bar_colors.append('#191970')  # Dark blue for heavy rain (> 7.5 mm/hr)

bars = ax2.bar(datetime_objects, precipitation_scaled, alpha=0.8, color=bar_colors, width=0.02)

ax2.tick_params(axis='y', labelcolor=color2)

# Format x-axis to show dates and times nicely
# Set time labels every 6 hours starting from midnight
from datetime import datetime, timedelta

# Find the first midnight in the data
start_time = datetime_objects[0]
# Calculate offset to next 00, 06, 12, or 18 hour
target_hours = [0, 6, 12, 18]
current_hour = start_time.hour
next_target = min([h for h in target_hours if h >= current_hour] + [target_hours[0] + 24])
if next_target >= 24:
    next_target -= 24
    start_offset_hours = (24 - current_hour) + next_target
else:
    start_offset_hours = next_target - current_hour

# Create custom time locator starting from proper alignment
time_ticks = []
for i, dt in enumerate(datetime_objects):
    if dt.hour in [0, 6, 12, 18]:
        time_ticks.append(dt)

ax1.set_xticks([mdates.date2num(tick) for tick in time_ticks])
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')

# Add date labels manually at midnight (00:00) of each day
date_positions = []
date_labels = []
for i, dt in enumerate(datetime_objects):
    if dt.hour == 0:  # Midnight - start of new day
        date_positions.append(dt)
        date_labels.append(dt.strftime('%A %m/%d'))

# Add secondary x-axis for dates
ax3 = ax1.twiny()
ax3.set_xlim(ax1.get_xlim())
ax3.set_xticks([mdates.date2num(pos) for pos in date_positions])
ax3.set_xticklabels(date_labels)
ax3.tick_params(axis='x', which='major', pad=20)  # Add some padding above

# Add grid for better readability
ax1.grid(True, alpha=0.3)

# Add legend with precipitation intensity info
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()

# Create custom legend entries for precipitation intensity
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

# Create a text-only entry for the precipitation header (invisible line)
text_entry = Line2D([0], [0], linestyle='', marker='', color='none')

precip_legend = [
    Patch(color='#87CEEB', alpha=0.8),
    Patch(color='#4682B4', alpha=0.8),
    Patch(color='#191970', alpha=0.8)
]

all_handles = lines1 + lines2 + [text_entry] + precip_legend
all_labels = labels1 + labels2 + ['Hourly Precipitation (mm × 10):', '  Light rain (< 2.5mm/hr)', '  Moderate rain (2.5-7.5mm/hr)', '  Heavy rain (> 7.5mm/hr)']
ax1.legend(all_handles, all_labels, loc='upper left')

# Customize the plot
plt.title('Hourly Temperature, Precipitation Probability & Precipitation Forecast', fontsize=16, fontweight='bold')

# Show temperature and precipitation range in subtitle
min_temp = min(temperatures)
max_temp = max(temperatures)
max_precip = max(precipitation_prob)
total_precip = sum(precipitation_mm)
plt.suptitle(f'Location: {city} | Temp: {min_temp}°C - {max_temp}°C | Max Rain: {max_precip}% | Total: {total_precip:.1f}mm', 
             fontsize=10, y=0.95)

# Add some styling - do this after suptitle to adjust spacing
plt.tight_layout()
plt.subplots_adjust(top=0.82)  # Make more room for both title and suptitle

plt.show()

# Print some basic stats
print("")
print(f"Weather Statistics:")
print(f"Temperature - Min: {min_temp}°C, Max: {max_temp}°C, Avg: {sum(temperatures)/len(temperatures):.1f}°C")
print(f"Precipitation Probability - Max: {max_precip}%, Avg: {sum(precipitation_prob)/len(precipitation_prob):.1f}%")
print(f"Precipitation - Total: {total_precip:.1f}mm, Max hourly: {max(precipitation_mm):.1f}mm")
print("")

############################################################################################################
# Connect to Google AI Studio API
api_key = os.getenv('GEMINI_API_KEY')
client = genai.Client(api_key=api_key)
grounding_tool = types.Tool(google_search=types.GoogleSearch())
config = types.GenerateContentConfig(tools=[grounding_tool])
# Choose model to query
model = "gemini-2.5-flash-lite"
# Create query
query = f"""Today is {today}. During the next 3 days I will be in the address {address}, with Google Maps link {address_google} and coordinates {coordinate}.
        Please browse the internet and tell me only two (2) interesting activities going on each day close to that location. If weekday, activities after 6pm"""
# Send query to model and save the response
response = client.models.generate_content(model=model, contents=query, config=config)
# Share the response
print(response.text)
print("")


