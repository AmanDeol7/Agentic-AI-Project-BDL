#!/usr/bin/env python3
"""
Create a sample Excel file for testing the document processing system.
"""

import pandas as pd
from pathlib import Path
import sys
import os

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.append(str(PROJECT_ROOT))

from config.app_config import PATHS

def create_sample_excel():
    """Create a comprehensive sample Excel file for testing."""
    
    # Ensure uploads directory exists
    upload_dir = PATHS["uploads"]
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Create sample data
    excel_file = upload_dir / "sample_business_data.xlsx"
    
    # Create a Pandas Excel writer
    with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
        
        # Sheet 1: Sales Data
        sales_data = {
            'Date': pd.date_range('2024-01-01', periods=12, freq='M'),
            'Product': ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Webcam', 'Headset', 
                       'Tablet', 'Smartphone', 'Printer', 'Scanner', 'Speaker', 'Charger'],
            'Category': ['Electronics', 'Accessories', 'Accessories', 'Electronics', 'Accessories', 'Accessories',
                        'Electronics', 'Electronics', 'Office', 'Office', 'Audio', 'Accessories'],
            'Units_Sold': [150, 300, 200, 80, 120, 90, 60, 200, 45, 30, 110, 250],
            'Unit_Price': [899.99, 29.99, 79.99, 299.99, 89.99, 129.99, 
                          499.99, 699.99, 199.99, 149.99, 79.99, 39.99],
            'Revenue': [134998.50, 8997.00, 15998.00, 23999.20, 10798.80, 11699.10,
                       29999.40, 139998.00, 8999.55, 4499.70, 8798.90, 9997.50],
            'Salesperson': ['Alice Johnson', 'Bob Smith', 'Carol Davis', 'David Wilson', 'Eva Brown', 'Frank Miller',
                           'Grace Lee', 'Henry Garcia', 'Iris Chen', 'Jack Taylor', 'Kate Anderson', 'Leo Martinez']
        }
        sales_df = pd.DataFrame(sales_data)
        sales_df.to_excel(writer, sheet_name='Sales_Data', index=False)
        
        # Sheet 2: Employee Information
        employee_data = {
            'Employee_ID': [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008],
            'Name': ['Alice Johnson', 'Bob Smith', 'Carol Davis', 'David Wilson', 
                    'Eva Brown', 'Frank Miller', 'Grace Lee', 'Henry Garcia'],
            'Department': ['Sales', 'Sales', 'Marketing', 'IT', 'HR', 'Finance', 'Sales', 'IT'],
            'Position': ['Senior Sales Rep', 'Sales Rep', 'Marketing Manager', 'Software Engineer',
                        'HR Specialist', 'Financial Analyst', 'Sales Rep', 'DevOps Engineer'],
            'Hire_Date': ['2020-03-15', '2021-06-01', '2019-08-20', '2022-01-10',
                         '2020-11-05', '2021-09-15', '2023-02-28', '2022-07-12'],
            'Salary': [75000, 55000, 85000, 90000, 65000, 70000, 52000, 95000],
            'Performance_Rating': [4.5, 4.2, 4.8, 4.3, 4.1, 4.6, 4.0, 4.7],
            'Status': ['Active', 'Active', 'Active', 'Active', 'Active', 'Active', 'Active', 'Active']
        }
        employee_df = pd.DataFrame(employee_data)
        employee_df.to_excel(writer, sheet_name='Employees', index=False)
        
        # Sheet 3: Financial Summary
        financial_data = {
            'Quarter': ['Q1 2024', 'Q2 2024', 'Q3 2024', 'Q4 2024'],
            'Revenue': [450000, 520000, 485000, 610000],
            'Expenses': [320000, 365000, 340000, 425000],
            'Net_Income': [130000, 155000, 145000, 185000],
            'Profit_Margin': [28.9, 29.8, 29.9, 30.3],
            'Growth_Rate': [12.5, 15.6, -6.7, 25.8]
        }
        financial_df = pd.DataFrame(financial_data)
        financial_df.to_excel(writer, sheet_name='Financial_Summary', index=False)
        
        # Sheet 4: Inventory
        inventory_data = {
            'Product_ID': ['P001', 'P002', 'P003', 'P004', 'P005', 'P006', 'P007', 'P008'],
            'Product_Name': ['Gaming Laptop', 'Wireless Mouse', 'Mechanical Keyboard', '4K Monitor',
                            'HD Webcam', 'Noise-Canceling Headset', 'Tablet Pro', 'Smartphone X'],
            'Stock_Quantity': [25, 150, 80, 40, 60, 35, 15, 90],
            'Reorder_Level': [10, 50, 30, 15, 20, 15, 5, 30],
            'Supplier': ['TechCorp', 'AccessoryPlus', 'KeyboardCo', 'DisplayTech',
                        'CameraTech', 'AudioMax', 'TabletInc', 'PhonePro'],
            'Last_Ordered': ['2024-01-15', '2024-02-20', '2024-01-30', '2024-02-10',
                           '2024-02-25', '2024-01-20', '2024-02-28', '2024-02-15'],
            'Unit_Cost': [750.00, 20.00, 60.00, 220.00, 65.00, 95.00, 400.00, 550.00]
        }
        inventory_df = pd.DataFrame(inventory_data)
        inventory_df.to_excel(writer, sheet_name='Inventory', index=False)
        
        # Sheet 5: Customer Data
        customer_data = {
            'Customer_ID': ['C001', 'C002', 'C003', 'C004', 'C005', 'C006'],
            'Company_Name': ['TechStart Inc', 'Business Solutions LLC', 'Creative Agency', 
                           'Manufacturing Corp', 'Retail Chain', 'Consulting Group'],
            'Contact_Person': ['John Smith', 'Sarah Johnson', 'Mike Brown', 
                              'Lisa Davis', 'Tom Wilson', 'Emma Garcia'],
            'Email': ['john@techstart.com', 'sarah@bizsolute.com', 'mike@creative.com',
                     'lisa@manufacturing.com', 'tom@retailchain.com', 'emma@consulting.com'],
            'Industry': ['Technology', 'Business Services', 'Creative', 'Manufacturing', 'Retail', 'Consulting'],
            'Annual_Revenue': [2500000, 5000000, 1200000, 8500000, 15000000, 3200000],
            'Account_Status': ['Active', 'Active', 'Prospect', 'Active', 'Active', 'Active'],
            'Last_Purchase': ['2024-02-15', '2024-01-30', None, '2024-02-28', '2024-02-20', '2024-01-25']
        }
        customer_df = pd.DataFrame(customer_data)
        customer_df.to_excel(writer, sheet_name='Customers', index=False)
    
    print(f"✅ Created sample Excel file: {excel_file}")
    print(f"📊 The file contains {len(sales_df)} sales records, {len(employee_df)} employees, {len(financial_df)} quarters, {len(inventory_df)} products, and {len(customer_df)} customers")
    
    # Display summary of each sheet
    print("\n📋 Sheet Summary:")
    print("1. Sales_Data: Monthly sales data with products, revenue, and salespeople")
    print("2. Employees: Employee information including departments, salaries, and performance")
    print("3. Financial_Summary: Quarterly financial performance data")
    print("4. Inventory: Current stock levels and supplier information")
    print("5. Customers: Customer database with contact and business information")
    
    return str(excel_file)

if __name__ == "__main__":
    try:
        excel_file = create_sample_excel()
        print(f"\n🎉 Sample Excel file created successfully!")
        print(f"📁 File location: {excel_file}")
        print("\nYou can now upload this file in the Streamlit app to test:")
        print("- Document extraction and processing")
        print("- Data analysis and insights")
        print("- Question answering about the data")
        print("- Summarization of business information")
        
    except Exception as e:
        print(f"❌ Error creating sample Excel file: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
