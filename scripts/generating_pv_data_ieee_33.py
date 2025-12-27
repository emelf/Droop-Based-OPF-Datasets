import pvlib
import pandas as pd
import numpy as np

# Location parameters (Oslo, Norway)
latitude = 59.91
longitude = 10.75
timezone = 'Europe/Oslo'
altitude = 25  # meters above sea level

# Create location object
location = pvlib.location.Location(
    latitude=latitude,
    longitude=longitude,
    tz=timezone,
    altitude=altitude
)

# Define time range: June 21, 2024 (summer solstice - maximum solar)
date = '2024-06-21'
times = pd.date_range(
    start=f'{date} 00:00',
    end=f'{date} 23:45',
    freq='15min',
    tz=timezone
)

# Calculate solar position
solar_position = location.get_solarposition(times)

# Calculate clear-sky irradiance (Ineichen model)
clearsky = location.get_clearsky(times, model='ineichen')

# Extract GHI (Global Horizontal Irradiance) in W/m²
ghi = clearsky['ghi']

# Convert to power output for 1 MW system
# Typical conversion: P(MW) = GHI(W/m²) / 1000 × η_system
# Where η_system accounts for panel efficiency, inverter losses, temperature, etc.
# Typical overall efficiency: 0.15-0.20 (we'll use 0.17)

P_rated = 1.0  # MW
efficiency = 0.17  # system efficiency factor
P_solar = (ghi / 1000.0) * (P_rated / efficiency) * efficiency  # Simplifies to: ghi/1000 * P_rated

# Alternative simpler formula (commonly used):
P_solar = ghi / 1000.0 * P_rated  # Direct scaling

# Create DataFrame
solar_data = pd.DataFrame({
    'timestamp': times,
    'GHI_W_m2': ghi.values,
    'P_MW': P_solar.values
})

print(f"Generated {len(solar_data)} time steps")
print(f"Peak production: {P_solar.max():.3f} MW at {times[P_solar.argmax()]}")
print(f"Total energy: {P_solar.sum() * 0.25:.2f} MWh")  # 0.25 = 15min in hours

# High variability: add cloud factor
np.random.seed(42)  # For reproducibility
cloud_factor = 1 + 0.3 * np.random.randn(len(times))
cloud_factor = np.clip(cloud_factor, 0.3, 1.3)  # Limit range
P_solar_variable = P_solar * cloud_factor

# solar_data.to_csv('solar_production_oslo_june21.csv', index=False)

pd.DataFrame({
    'timestamp': times,
    'P_pu': P_solar_variable
}).to_csv(r'normalized_timeseries//solar_production_normalized.csv', index=False)

## FOR PLOTTING PURPOSES ONLY - COMMENTED OUT
# import matplotlib.pyplot as plt
# plt.figure(figsize=(12, 6))
# plt.plot(solar_data['timestamp'], solar_data['P_MW'], linewidth=2, label='Clear-sky (low variability)', alpha=0.7)
# plt.plot(solar_data['timestamp'], P_solar_variable, linewidth=2, label='Cloud-affected (high variability)', alpha=0.7)
# plt.xlabel('Time', fontsize=12)
# plt.ylabel('Active Power (MW)', fontsize=12)
# plt.title('1 MW Solar PV Production - Variability Comparison', fontsize=14)
# plt.grid(True, alpha=0.3)
# plt.legend(fontsize=11)
# plt.tight_layout()
# plt.savefig('solar_production_comparison.png', dpi=150)
# plt.show()