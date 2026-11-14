"""
Population Data Visualizer  (PS No. 18)
Reads population.csv (City, Year, Population), cleans it, then shows
a summary or charts.
Growth % = (latest - earliest) / earliest * 100
"""

import pandas as pd
import matplotlib.pyplot as plt

FILE_NAME = "population.csv"


# ---------- STEP 1: load the file and remove bad rows ----------
def load_and_clean():
    try:
        raw = pd.read_csv(FILE_NAME, header=None,
                          names=["City", "Year", "Population"],
                          dtype=str, skipinitialspace=True)
    except FileNotFoundError:
        print(f"Error: file '{FILE_NAME}' not found.")
        return None
    except pd.errors.EmptyDataError:
        print("Error: the file is empty.")
        return None

    if raw.empty:
        print("Error: the file is empty.")
        return None
    
    # If the first line is the header (City,Year,Population), drop it
    if str(raw.iloc[0]["Year"]).strip().lower() == "year":
        raw = raw.iloc[1:]

    clean_rows = []     # good rows are collected here
    seen = set()        # (city, year) pairs already used -> finds duplicates
    row_no = 0

    for _, row in raw.iterrows():
        row_no += 1

        if row.isna().any():
            print(f"Row {row_no} skipped: missing value.")
            continue

        city = row["City"].strip()
        year_text = row["Year"].strip()
        pop_text = row["Population"].strip()

        try:
            year = int(year_text)
        except ValueError:
            print(f"Row {row_no} skipped: invalid Year '{year_text}'.")
            continue

        try:
            population = int(pop_text)
        except ValueError:
            print(f"Row {row_no} skipped: invalid Population '{pop_text}'.")
            continue

        if population <= 0:
            print(f"Row {row_no} skipped: Population must be positive.")
            continue

        if (city, year) in seen:
            print(f"Row {row_no} skipped: duplicate City and Year.")
            continue
        seen.add((city, year))

        clean_rows.append({"City": city, "Year": year, "Population": population})

    print(f"Valid rows: {len(clean_rows)}")
    if not clean_rows:
        return None
    return pd.DataFrame(clean_rows)


# ---------- STEP 2: groupby() -> earliest, latest and growth of each city ----------
def analyse(df):
    df = df.sort_values("Year", kind="stable")          # oldest year first
    cities = df.groupby("City", sort=False).agg(
        Earliest=("Population", "first"),               # first row of each city
        Latest=("Population", "last"),                  # last row of each city
        Years=("Year", "nunique"),                      # how many different years
    )
    cities["Growth"] = (cities["Latest"] - cities["Earliest"]) / cities["Earliest"] * 100
    cities["Growth"] = cities["Growth"].where(cities["Years"] > 1)   # 1 year -> no growth
    return cities


# ---------- MENU OPTION 1: summary ----------
def show_summary(df):
    cities = analyse(df)
    latest_year = df["Year"].max()
    total = cities["Latest"].sum()
    biggest = cities["Latest"].idxmax()
    biggest_pop = cities["Latest"].max()

    if cities["Growth"].notna().any():
        fastest = cities["Growth"].idxmax()
        print(f"Total population ({latest_year}): {total}")
        print(f"Largest city: {biggest} ({biggest_pop})")
        print(f"Fastest growing: {fastest} ({cities['Growth'].max():+.2f}%)")
    else:
        print(f"Total population: {total} | Largest city: {biggest}")
        print("Growth: not available (only one year of data)")


# ---------- MENU OPTION 2: growth + charts ----------
def show_growth_and_charts(df):
    cities = analyse(df)
    growth = cities["Growth"].dropna()

    if growth.empty:
        print("Growth: not available (only one year of data)")
        return

    parts = []
    for city, g in cities["Growth"].items():
        parts.append(f"{city}: {g:+.2f}%" if pd.notna(g) else f"{city}: not available")
    print(" | ".join(parts))

    # Chart 1: bar chart of growth %
    plt.figure()
    plt.bar(growth.index, growth.values, color="tab:orange")
    plt.title("Population Growth by City")
    plt.xlabel("City")
    plt.ylabel("Growth (%)")

    # Chart 2: line chart of population over the years
    plt.figure()
    for city, group in df.groupby("City", sort=False):
        group = group.sort_values("Year")
        plt.plot(group["Year"], group["Population"], marker="o", label=city)
    plt.title("Population Trend")
    plt.xlabel("Year")
    plt.ylabel("Population")
    plt.xticks(sorted(df["Year"].unique()))
    plt.legend()

    print("Bar chart 'Population Growth by City' and line chart 'Population Trend' displayed")
    plt.show()


# ---------- MAIN: menu ----------
def main():
    df = load_and_clean()
    if df is None:
        return

    while True:
        print("\n1. Summary")
        print("2. Growth and charts")
        print("3. Exit")
        try:
            choice = input("Enter your choice: ").strip()
        except EOFError:
            break

        if choice == "1":
            show_summary(df)
        elif choice == "2":
            show_growth_and_charts(df)
        elif choice == "3":
            break
        else:
            print("Invalid choice. Please enter 1, 2 or 3.")


if __name__ == "__main__":
    main()