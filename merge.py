import pandas as pd

agent_data = pd.read_csv('agent_data.csv')
agent_details = pd.read_csv('agent_details.csv')

merged_df = pd.merge(agent_data, agent_details, on='URL', how='left')

merged_df.to_csv('all_data.csv', index=False)

print("CSV files have been successfully merged and saved as 'all_data.csv'.")
