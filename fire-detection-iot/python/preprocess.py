import pandas as pd
import numpy as np
from sklearn.utils import resample

# Load the CSV file
df = pd.read_csv('sensor_data.csv')

# Step 1: Drop the LDR column
df = df.drop(columns=['LDR'])

# Step 2: Rename the 'IR' column to 'isFlame'
df = df.rename(columns={'IR': 'isFlame'})

df['isFlame'] = np.where(
    (df['MQ2'] > 100) | (df['MQ7'] > 250) | (df['Flame'] < 700),
    1,  # Set to 1 if the condition is met
    df['isFlame']  # Keep the original value if not
)

# Step 4: Save the preprocessed data to a new CSV file
df.to_csv('preprocessed_sensor_data.csv', index=False)

# Step 5: Data Augmentation to generate more data points
def augment_data(df, target_rows=10000):
    # Separate the dataset into two groups: isFlame == 0 and isFlame == 1
    df_isFlame_0 = df[df['isFlame'] == 0]
    df_isFlame_1 = df[df['isFlame'] == 1]
    
    # Calculate how many rows we already have
    current_rows = len(df)
    
    # Calculate how many more rows are needed
    rows_needed = target_rows - current_rows
    
    # If more rows are needed, augment the dataset
    if rows_needed > 0:
        # Randomly sample from the existing groups and apply jittering
        augmented_data = []
        
        # Alternate augmenting isFlame == 0 and isFlame == 1 groups
        for _ in range(rows_needed):
            if len(df_isFlame_1) > 0:
                # Add rows from isFlame == 1 group
                sampled_row = df_isFlame_1.sample(1).copy()
            else:
                # Fallback if no isFlame == 1 rows
                sampled_row = df_isFlame_0.sample(1).copy()
            
            # Add small random integer noise (jittering) to the numerical values
            noise = np.random.randint(-5, 6, sampled_row.shape)  # Random integer between -5 and 5
            augmented_row = sampled_row + noise
            
            # Ensure values are within valid ranges, e.g., MQ2, MQ7, etc.
            augmented_row['MQ2'] = augmented_row['MQ2'].clip(lower=0, upper=1024)
            augmented_row['MQ7'] = augmented_row['MQ7'].clip(lower=0, upper=1024)
            augmented_row['Flame'] = augmented_row['Flame'].clip(lower=0, upper=1024)
            
            # Ensure isFlame is correctly set for augmented data
            augmented_row['isFlame'] = 1 if augmented_row['MQ2'].iloc[0] > 100 or augmented_row['MQ7'].iloc[0] > 250 or augmented_row['Flame'].iloc[0] < 700 else 0
            
            # Append the augmented row
            augmented_data.append(augmented_row)
        
        # Combine the augmented data
        augmented_df = pd.concat(augmented_data, ignore_index=True)
        
        # Append the augmented rows to the original dataframe
        df = pd.concat([df, augmented_df], ignore_index=True)
    
    return df

# Augment data and save to a new file
augmented_df = augment_data(df, target_rows=10000)

augmented_df['isFlame'] = np.where(
    (augmented_df['MQ2'] > 100) | (augmented_df['MQ7'] > 250) | (augmented_df['Flame'] < 700),
    1,  # Set to 1 if the condition is met
    augmented_df['isFlame']  # Keep the original value if not
)

# Separate the majority and minority classes
df_majority = augmented_df[augmented_df['isFlame'] == 1]
df_minority = augmented_df[augmented_df['isFlame'] == 0]

# Upsample the minority class
df_minority_upsampled = resample(
    df_minority,
    replace=True,  # Sample with replacement
    n_samples=len(df_majority),  # Match the number of majority class
    random_state=42  # For reproducibility
)

# Combine the majority class with the upsampled minority class
balanced_df = pd.concat([df_majority, df_minority_upsampled])

# Shuffle the dataset
balanced_df = balanced_df.sample(frac=1, random_state=42).reset_index(drop=True)

print(balanced_df['isFlame'].value_counts())
balanced_df.to_csv('balanced_sensor_data_upsampled.csv', index=False)

# counts = augmented_df['isFlame'].value_counts()



# augmented_df.to_csv('augmented_sensor_data.csv', index=False)

print("Preprocessing and data augmentation completed.")