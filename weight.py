import csv
import os
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate


def initialize_csv():
    start_date = datetime(2025, 7, 1)
    end_date = datetime(2026, 12, 31)
    current_date = start_date

    with open('weight_data.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Date', 'Weight1', 'Weight2', 'Weight3', 'Weight4'])

        while current_date <= end_date:
            date_str = current_date.strftime('%Y.%m.%d')
            writer.writerow([date_str, '', '', '', ''])
            current_date += timedelta(days=1)


def read_weight_data():
    dates = []
    daily_weights = []

    with open('weight_data.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            date_str = row['Date']
            weights = []

            for i in range(1, 5):
                weight_key = f'Weight{i}'
                if row[weight_key] and row[weight_key].strip():
                    try:
                        weights.append(float(row[weight_key]))
                    except ValueError:
                        continue

            if weights:
                avg_weight = sum(weights) / len(weights)
                dates.append(datetime.strptime(date_str, '%Y.%m.%d'))
                daily_weights.append(avg_weight)

    return dates, daily_weights


def calculate_statistics(weights):
    if not weights:
        return None, None, None

    avg_weight = np.mean(weights)
    max_weight = np.max(weights)
    min_weight = np.min(weights)

    return avg_weight, max_weight, min_weight


def calculate_weight_changes(weights):
    changes = []
    for i in range(1, len(weights)):
        change = weights[i] - weights[i - 1]
        changes.append(change)
    return changes


def calculate_bmi(weight_kg, height_cm=176):
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    return bmi


def get_latest_bmi(dates, weights, height_cm=176):
    if not weights:
        return None, None

    latest_date = dates[-1]
    latest_weight = weights[-1]
    latest_bmi = calculate_bmi(latest_weight, height_cm)

    return latest_date, latest_bmi


def create_plots(dates, weights, weight_changes):
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))

    # Raw weight data plot
    ax1.plot(dates, weights, 'b-', linewidth=1, alpha=0.7, label='Raw Data')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Weight (kg)')
    ax1.set_title('Weight Change Over Time')
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    # Smoothed weight data plot
    if len(weights) > 3:
        dates_num = [date.toordinal() for date in dates]
        spline = interpolate.UnivariateSpline(dates_num, weights, s=len(weights) * 0.8)
        smoothed_weights = spline(dates_num)

        ax2.plot(dates, smoothed_weights, 'r-', linewidth=2, label='Smoothed Data')
        ax2.plot(dates, weights, 'b-', linewidth=1, alpha=0.3, label='Raw Data')
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Weight (kg)')
        ax2.set_title('Smoothed Weight Change')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
    else:
        ax2.text(0.5, 0.5, 'Not enough data for smoothing',
                 horizontalalignment='center', verticalalignment='center',
                 transform=ax2.transAxes)
        ax2.set_title('Smoothed Weight Change')

    # Weight change rate plot
    if len(weight_changes) > 0:
        change_dates = dates[1:]
        ax3.plot(change_dates, weight_changes, 'g-', linewidth=1, alpha=0.7)
        ax3.axhline(y=0, color='r', linestyle='-', alpha=0.3)
        ax3.set_xlabel('Date')
        ax3.set_ylabel('Weight Change (kg/day)')
        ax3.set_title('Weight Change Rate Trend')
        ax3.grid(True, alpha=0.3)
    else:
        ax3.text(0.5, 0.5, 'Not enough data for change rate calculation',
                 horizontalalignment='center', verticalalignment='center',
                 transform=ax3.transAxes)
        ax3.set_title('Weight Change Rate Trend')

    plt.tight_layout()
    plt.savefig('weight_analysis.png')
    plt.show()


def main():
    HEIGHT_CM = 175  # Height in centimeters

    # Initialize CSV if it doesn't exist
    if not os.path.exists('weight_data.csv'):
        initialize_csv()
        print("CSV file created: weight_data.csv")
        print("Please fill in the weight data and run the program again.")
        return

    # Read and process data
    dates, daily_weights = read_weight_data()

    if not daily_weights:
        print("No weight data found in the CSV file.")
        return

    # Calculate statistics
    avg_weight, max_weight, min_weight = calculate_statistics(daily_weights)

    print(f"Statistics:")
    print(f"Average weight: {avg_weight:.2f} kg")
    print(f"Maximum weight: {max_weight:.2f} kg")
    print(f"Minimum weight: {min_weight:.2f} kg")
    print(f"Total data points: {len(daily_weights)} days")

    # Calculate and print latest BMI
    latest_date, latest_bmi = get_latest_bmi(dates, daily_weights, HEIGHT_CM)
    if latest_date and latest_bmi:
        date_str = latest_date.strftime('%Y.%m.%d')
        print(f"Latest BMI ({date_str}): {latest_bmi:.2f} (Height: {HEIGHT_CM}cm)")

    # Calculate weight changes
    weight_changes = calculate_weight_changes(daily_weights)

    # Create plots
    create_plots(dates, daily_weights, weight_changes)
    print("Plots saved as 'weight_analysis.png'")


if __name__ == "__main__":
    main()