import folium
import json
from folium import FeatureGroup, LayerControl

# 1. Load your updated JSON data
with open('universities.json', 'r', encoding='utf-8') as f:
    universities = json.load(f)

# 2. Define the color map for all difficulty levels
color_map = {
    "Very High": "darkred",
    "High": "red",
    "Medium-High": "orange",
    "Medium": "blue",
    "Low": "green"
}

# 3. Create the base map
m = folium.Map(location=[20, 0], zoom_start=2)

# 4. Build one FeatureGroup per difficulty
feature_groups = {}
for lvl in {u['difficulty'] for u in universities}:
    fg = FeatureGroup(name=f"{lvl} Admission Difficulty")
    fg.add_to(m)
    feature_groups[lvl] = fg


# 5. A full-detail popup builder
def build_popup_html(u):
    # Ratings
    ratings = "".join(f"<li>{k}: {v}</li>" for k, v in u.get("ratings", {}).items() if v not in (None, "null"))
    if not ratings:
        ratings = "<li>No ranking data</li>"

    # Acceptance
    acc = u.get("acceptance", {})
    acc_html = f"Overall {acc.get('overall', 'n/a')}, Int’l {acc.get('international', 'n/a')}, {acc.get('gender', '')}"

    # Professors
    profs = ", ".join(u.get("key_professors", [])) or "N/A"

    # Scholarships
    state_sch = u.get("scholarships_state", "N/A")
    uni_schs = ", ".join(u.get("scholarships_university", [])) or "N/A"

    html = f"""
    <h4>{u['name']}</h4>
    <ul>
      <li><strong>Type:</strong> {u.get('university_type', 'Unknown')}</li>
      <li><strong>Difficulty:</strong> {u['difficulty']}</li>
      <li><strong>University Ratings:</strong>
        <ul>{ratings}</ul>
      </li>
      <li><strong>Acceptance Rate:</strong> {acc_html}</li>
      <li><strong>Accessibility for Russians:</strong> {u.get('accessibility_russians', 'N/A')}</li>
      <li><strong>Key Professors (AI/NLP):</strong> {profs}</li>
      <li><strong>State Scholarships:</strong> {state_sch}</li>
      <li><strong>University Scholarships:</strong> {uni_schs}</li>
    </ul>
    """
    return folium.Popup(html, max_width=350)


# 6. Add each university marker, ensuring every difficulty is present
for u in universities:
    lvl = u['difficulty']
    fg = feature_groups.get(lvl)
    if not fg:
        # If somehow the difficulty is typo’d, assign to 'Medium'
        fg = feature_groups.setdefault("Medium", FeatureGroup(name="Medium Admission Difficulty"))
        fg.add_to(m)
    folium.CircleMarker(
        location=(u['lat'], u['lon']),
        radius=6,
        color=color_map.get(lvl, 'gray'),
        fill=True,
        fill_color=color_map.get(lvl, 'gray'),
        fill_opacity=0.7,
        tooltip=folium.Tooltip(f"{u['name']} ({lvl})"),
        popup=build_popup_html(u)
    ).add_to(fg)

# 7. Add layer control and save
LayerControl(collapsed=False).add_to(m)
m.save('universities_map.html')
print("Map regenerated and saved to universities_map.html")
