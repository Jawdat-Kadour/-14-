#!/usr/bin/env python3
"""Verify that the data file is correctly generated"""

import json
import os

if not os.path.exists('governorate_networks.json'):
    print("❌ Error: governorate_networks.json not found!")
    print("   Please run: python process_data.py")
    exit(1)

with open('governorate_networks.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("✅ Data file loaded successfully!")
print(f"\n📊 Governorates: {len(data)}")
print("\n📋 Governorate Summary:")
print("-" * 50)

for gov in sorted(data.keys()):
    metrics = data[gov]['metrics']
    nodes = len(data[gov]['network']['nodes'])
    links = len(data[gov]['network']['links'])
    print(f"  {gov:20} | Companies: {metrics['total_companies']:4} | Nodes: {nodes:3} | Links: {links:3}")

print("\n✅ All governorates processed successfully!")
print("🚀 Ready to use! Run: python start_server.py")

