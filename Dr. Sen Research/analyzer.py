import pandas as pd
import numpy as np

def analyze_excel(file_path):
    try:
        # Read the Excel file
        df = pd.read_excel(file_path)
        
        # Display column titles
        print("\nColumn Titles:")
        print("-------------")
        for col in df.columns:
            print(f"- {col}")
            
        # Display first 5 rows
        print("\nFirst 5 Rows:")
        print("-------------")
        print(df.head().to_string())
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print("Please check:")
        print("1. The file path is correct")
        print("2. The file exists")
        print("3. You have proper read permissions")
        
def find_closest_facilities(df, facility_id, n=5):
    """
    Find n closest facilities to the given facility ID.
    
    Args:
        df: DataFrame containing facility data
        facility_id: ID of the target facility
        n: Number of closest facilities to find (default 5)
    """
    try:
        # Get the target facility's coordinates
        target = df[df['ID'] == facility_id].iloc[0]
        target_x, target_y = target['x'], target['y']
        
        # Calculate distances to all other facilities
        df['distance'] = np.sqrt((df['x'] - target_x)**2 + (df['y'] - target_y)**2)
        
        # Sort by distance and get n closest facilities (excluding the target facility)
        closest = df[df['ID'] != facility_id].nsmallest(n, 'distance')
        
        print(f"\nTarget Facility (ID: {facility_id}):")
        print(f"Location: ({target_x}, {target_y})")
        print(f"Functionality: {target['Func']}")
        
        print(f"\n{n} Closest Facilities:")
        print("-" * 50)
        print("ID    Distance    Coordinates (x, y)    Functionality")
        print("-" * 50)
        
        for _, facility in closest.iterrows():
            print(f"{facility['ID']:<6} {facility['distance']:9.2f}    ({facility['x']:<3}, {facility['y']:<3})           {facility['Func']}")
            
        # Drop the temporary distance column
        df.drop('distance', axis=1, inplace=True)
        
    except IndexError:
        print(f"Error: Facility ID {facility_id} not found in the dataset.")
    except Exception as e:
        print(f"Error: {str(e)}")

# Example usage - update the path to your Excel file
if __name__ == "__main__":
    file_path = r"C:\Users\johnt\OneDrive\Desktop\Hobbies\Coding\PersonalProjects\Cursor AI\Dr. Sen Research\Sandeep's - importance_factor (Func change from 0.3 through 0.7 in facilty 2002).xlsx"
    df = pd.read_excel(file_path)
    
    # Display basic file analysis
    analyze_excel(file_path)
    
    # Example: Find 5 closest facilities to facility with ID 1
    facility= input("Enter the facility ID:")
    print("\nFinding closest facilities...")
    find_closest_facilities(df, facility_id= int(facility))
