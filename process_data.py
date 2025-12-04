import pandas as pd
import json
import numpy as np
from collections import defaultdict

# Read the CSV data
df = pd.read_csv('expanded_syria_bi_data.csv')

# Process data for each governorate
governorates = df['Governorate'].unique()
industries = df['Industry'].unique()

governorate_data = {}

for gov in governorates:
    gov_df = df[df['Governorate'] == gov]
    
    # Calculate aggregated metrics
    metrics = {
        'total_companies': len(gov_df),
        'industries': gov_df['Industry'].value_counts().to_dict(),
        'avg_pre_bi_agility': gov_df['Pre_BI_Decision_Making_Agility_Score'].mean(),
        'avg_post_bi_agility': gov_df['Post_BI_Decision_Making_Agility_Score'].mean(),
        'avg_pre_bi_efficiency': gov_df['Pre_BI_Operational_Efficiency_Index'].mean(),
        'avg_post_bi_efficiency': gov_df['Post_BI_Operational_Efficiency_Index'].mean(),
        'avg_pre_bi_data_driven': gov_df['Pre_BI_Data_Driven_Decisions_Percentage'].mean(),
        'avg_post_bi_data_driven': gov_df['Post_BI_Data_Driven_Decisions_Percentage'].mean(),
        'avg_revenue_growth': gov_df['Revenue_Growth_After_BI_Percentage'].mean(),
        'avg_cost_reduction': gov_df['Cost_Reduction_After_BI_Percentage'].mean(),
        'avg_customer_satisfaction': gov_df['Customer_Satisfaction_Increase_After_BI_Percentage'].mean(),
        'avg_market_share': gov_df['Market_Share_Increase_After_BI_Percentage'].mean(),
        'avg_agility_improvement': gov_df['Decision_Making_Agility_Improvement'].mean(),
        'avg_efficiency_improvement': gov_df['Operational_Efficiency_Improvement'].mean(),
        'avg_data_driven_improvement': gov_df['Data_Driven_Decisions_Improvement'].mean(),
        'bi_years': sorted(gov_df['BI_Implementation_Year'].unique().tolist())
    }
    
    # Generate network nodes and links
    # Nodes: Companies (Data Sources), Industries (Processes/Silos), Governorate (Decision Maker Hub)
    nodes = []
    links = []
    
    # Add governorate as central decision maker hub
    nodes.append({
        'id': f'{gov}_hub',
        'type': 'decision_maker',
        'label': f'{gov} Hub',
        'size': 50,
        'group': 0
    })
    
    # Add industry nodes (Processes/Silos)
    industry_nodes = {}
    for idx, industry in enumerate(industries):
        industry_companies = gov_df[gov_df['Industry'] == industry]
        if len(industry_companies) > 0:
            node_id = f'{gov}_{industry}'
            industry_nodes[industry] = node_id
            nodes.append({
                'id': node_id,
                'type': 'process',
                'label': industry,
                'size': 30 + len(industry_companies) * 2,
                'group': idx + 1,
                'company_count': len(industry_companies)
            })
            
            # Link industry to governorate hub
            links.append({
                'source': f'{gov}_hub',
                'target': node_id,
                'type': 'governance',
                'strength': len(industry_companies) / 10
            })
    
    # Add company nodes (Data Sources) - sample for visualization
    company_sample_size = min(50, len(gov_df))  # Limit to 50 for performance
    sampled_companies = gov_df.sample(n=company_sample_size, random_state=42) if len(gov_df) > company_sample_size else gov_df
    
    for idx, company in sampled_companies.iterrows():
        company_id = f'company_{company["Company_ID"]}'
        industry = company['Industry']
        
        # Determine node properties based on BI metrics
        agility_score = company['Post_BI_Decision_Making_Agility_Score']
        efficiency = company['Post_BI_Operational_Efficiency_Index']
        
        nodes.append({
            'id': company_id,
            'type': 'data_source',
            'label': f"Company {company['Company_ID']}",
            'size': 10 + (agility_score + efficiency / 10),
            'group': industries.tolist().index(industry) + 1,
            'industry': industry,
            'agility': agility_score,
            'efficiency': efficiency,
            'data_driven': company['Post_BI_Data_Driven_Decisions_Percentage'],
            'revenue_growth': company['Revenue_Growth_After_BI_Percentage']
        })
        
        # Link company to its industry
        if industry in industry_nodes:
            links.append({
                'source': company_id,
                'target': industry_nodes[industry],
                'type': 'belongs_to',
                'strength': 1.0
            })
        
        # Create some inter-company connections (simulating data sharing)
        if idx % 3 == 0 and len(nodes) > 1:
            # Connect to a random company in same industry
            same_industry_companies = [n for n in nodes if n.get('industry') == industry and n['type'] == 'data_source']
            if len(same_industry_companies) > 1:
                target_company = np.random.choice([n['id'] for n in same_industry_companies if n['id'] != company_id])
                links.append({
                    'source': company_id,
                    'target': target_company,
                    'type': 'data_flow',
                    'strength': 0.5
                })
    
    # Generate pre-BI network (more fragmented, fewer connections)
    pre_bi_nodes = []
    pre_bi_links = []
    
    # Add governorate hub
    pre_bi_nodes.append({
        'id': f'{gov}_hub',
        'type': 'decision_maker',
        'label': f'{gov} Hub',
        'size': 40,
        'group': 0
    })
    
    # Add industry nodes (more isolated)
    for idx, industry in enumerate(industries):
        industry_companies = gov_df[gov_df['Industry'] == industry]
        if len(industry_companies) > 0:
            node_id = f'{gov}_{industry}'
            pre_bi_nodes.append({
                'id': node_id,
                'type': 'process',
                'label': industry,
                'size': 25 + len(industry_companies) * 1.5,
                'group': idx + 1,
                'company_count': len(industry_companies)
            })
            
            # Weaker connection to hub
            pre_bi_links.append({
                'source': f'{gov}_hub',
                'target': node_id,
                'type': 'governance',
                'strength': len(industry_companies) / 20
            })
    
    # Add company nodes with pre-BI metrics
    for idx, company in sampled_companies.iterrows():
        company_id = f'company_{company["Company_ID"]}'
        industry = company['Industry']
        
        agility_score = company['Pre_BI_Decision_Making_Agility_Score']
        efficiency = company['Pre_BI_Operational_Efficiency_Index']
        
        pre_bi_nodes.append({
            'id': company_id,
            'type': 'data_source',
            'label': f"Company {company['Company_ID']}",
            'size': 8 + (agility_score + efficiency / 15),
            'group': industries.tolist().index(industry) + 1,
            'industry': industry,
            'agility': agility_score,
            'efficiency': efficiency,
            'data_driven': company['Pre_BI_Data_Driven_Decisions_Percentage']
        })
        
        # Link company to industry (weaker)
        if industry in industry_nodes:
            pre_bi_links.append({
                'source': company_id,
                'target': industry_nodes[industry],
                'type': 'belongs_to',
                'strength': 0.7
            })
        
        # Fewer inter-company connections (fragmented)
        if idx % 7 == 0 and len(pre_bi_nodes) > 1:
            same_industry_companies = [n for n in pre_bi_nodes if n.get('industry') == industry and n['type'] == 'data_source']
            if len(same_industry_companies) > 1:
                target_company = np.random.choice([n['id'] for n in same_industry_companies if n['id'] != company_id])
                pre_bi_links.append({
                    'source': company_id,
                    'target': target_company,
                    'type': 'data_flow',
                    'strength': 0.3
                })
    
    governorate_data[gov] = {
        'metrics': metrics,
        'network': {
            'nodes': nodes,
            'links': links
        },
        'pre_bi_network': {
            'nodes': pre_bi_nodes,
            'links': pre_bi_links
        }
    }

# Save to JSON
with open('governorate_networks.json', 'w', encoding='utf-8') as f:
    json.dump(governorate_data, f, indent=2, ensure_ascii=False)

print(f"Processed {len(governorates)} governorates")
print(f"Generated network data for all governorates")
print("Data saved to governorate_networks.json")

