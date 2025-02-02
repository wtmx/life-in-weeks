# import libraries
import pandas as pd
import math
from datetime import date, timedelta
import altair as alt
import os
from gdrive_upload import upload_file

# create useful constants
c_label_lived = "lived weeks"
c_label_remaining = "remaining weeks"
c_label_current = "this week"

c_width = 1080 / 2.2
c_height = 1500 / 2.2

# insert arbitrary life expectancy and birthday details

life_exp = 85
birth_year = 1992
birth_month = 12
birth_day = 29

# calculate current date, day of birth and day of death

current_date = date.today()
day_of_birth = date(year = birth_year, month = birth_month, day = birth_day)
day_of_death = date(year = birth_year + life_exp, month = birth_month, day = birth_day)

# calculate days since birth until now + days between now and day of death

lived_life = current_date - day_of_birth
rest_of_life = day_of_death - current_date

lived_life_years = (lived_life.days / 365.25)
lived_life_years_floor = math.floor(lived_life_years)

lived_life_weeks = (lived_life_years - lived_life_years_floor) * 365.25 / 7
lived_life_weeks_floor = math.floor(lived_life_weeks)

rest_of_life_years = (rest_of_life.days / 365.25)
rest_of_life_years_floor = math.floor(rest_of_life_years)

rest_of_life_weeks = (rest_of_life_years - rest_of_life_years_floor) * 365.25 / 7
rest_of_life_weeks_floor = math.floor(rest_of_life_weeks)

# Create a function to generate week data
def generate_week_data():
    data = []
    
    # Add lived weeks for current year
    for week in range(lived_life_weeks_floor):
        week_date = day_of_birth + timedelta(weeks=week + lived_life_years_floor * 52)
        data.append({
            'week': week,
            'year': lived_life_years_floor,
            'label': c_label_lived,
            'date': week_date.isoformat(),
            'age_at_week': (week_date - day_of_birth).days / 365.25
        })
    
    # Add current week
    data.append({
        'week': lived_life_weeks_floor,
        'year': lived_life_years_floor,
        'label': c_label_current,
        'date': current_date.isoformat(),
        'age_at_week': (current_date - day_of_birth).days / 365.25
    })
    
    # Add remaining weeks for current year
    for week in range(lived_life_weeks_floor + 1, 52):
        week_date = day_of_birth + timedelta(weeks=week + lived_life_years_floor * 52)
        data.append({
            'week': week,
            'year': lived_life_years_floor,
            'label': c_label_remaining,
            'date': week_date.isoformat(),
            'age_at_week': (week_date - day_of_birth).days / 365.25
        })
    
    # Add past years
    for year in range(0, lived_life_years_floor):
        for week in range(52):
            week_date = day_of_birth + timedelta(weeks=week + year * 52)
            data.append({
                'week': week,
                'year': year,
                'label': c_label_lived,
                'date': week_date.isoformat(),
                'age_at_week': (week_date - day_of_birth).days / 365.25
            })
    
    # Add future years
    for year in range(lived_life_years_floor + 1, lived_life_years_floor + rest_of_life_years_floor + 1):
        for week in range(52):
            week_date = day_of_birth + timedelta(weeks=week + year * 52)
            data.append({
                'week': week,
                'year': year,
                'label': c_label_remaining,
                'date': week_date.isoformat(),
                'age_at_week': (week_date - day_of_birth).days / 365.25
            })
    
    return pd.DataFrame(data)

# Generate the complete dataset
df_complete = generate_week_data()

# Add metadata columns useful for Tableau
df_complete['is_current_week'] = df_complete['label'] == c_label_current
df_complete['week_number'] = df_complete.index + 1

# Create output directory if it doesn't exist
output_dir = "graphs"
os.makedirs(output_dir, exist_ok=True)

# Save the data for Tableau
df_complete.to_csv(os.path.join(output_dir, "life_in_weeks.csv"), index=False)

# Upload to Google Drive
csv_path = os.path.join(output_dir, "life_in_weeks.csv")
file_id = upload_file(csv_path)
if file_id:
    print(f"File uploaded successfully to Google Drive. File ID: {file_id}")
    print(f"Public URL: https://drive.google.com/uc?export=download&id={file_id}")
else:
    print("Failed to upload file to Google Drive")

# Create the visualization data without date column for Altair
df_viz = df_complete.drop('date', axis=1)

# Continue with the original Altair visualization
chart = (
    alt.Chart(df_viz)
    .mark_square(
        color="black",
        size=100 / 2
    ).encode(
        x=alt.X("week", axis=None),
        y=alt.Y("year", axis=None),
    ).properties(
        width=c_width,
        height=c_height
    ).properties(
        title="Your Life in Weeks"
    )
)

chart = chart + (
    alt.Chart(df_viz)
    .mark_square(
        filled=True,
        opacity=1,
        size=60 / 2
    ).encode(
        x=alt.X("week", axis=None),
        y=alt.Y("year", axis=None),
        color=alt.Color(
            "label", 
            scale=alt.Scale(range=["black", "white", "red"]),
            legend=alt.Legend(orient="bottom"), 
            title=""
        )
    ).properties(
        width=c_width,
        height=c_height
    ).properties(
        title="Your Life in Weeks"
    )
)

# final chart config changes
chart_config = (
    chart
    .configure_title(
        fontSize=40,
        font="Staatliches",
        align="center",
        color="black",
        baseline="bottom",
        dy=40
    ).configure_view(
        strokeWidth=0
    )
)

# Save the Altair visualization
chart_config.save(os.path.join(output_dir, "output.html"))