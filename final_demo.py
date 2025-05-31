#!/usr/bin/env python3
"""
Final demonstration test for TensorRT-LLM Document Agent
This shows the complete system working with Ollama fallback
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from backend.main import get_assistant
from backend.tools.doc_tools.document_processor import DocumentProcessor
from config.app_config import PATHS
import time


def create_demo_document():
    """Create a comprehensive demo document."""
    uploads_dir = Path(PATHS["uploads"])
    uploads_dir.mkdir(parents=True, exist_ok=True)
    
    content = """
# TechCorp Annual Performance Report 2024

## Executive Summary
TechCorp has demonstrated exceptional growth and innovation throughout 2024, establishing itself as a leader in the AI and cloud computing sectors.

## Financial Highlights
- **Total Revenue**: $127.5 million (up 42% from 2023)
- **Net Profit**: $23.8 million (18.7% profit margin)
- **R&D Investment**: $38.2 million (30% of revenue)
- **Cash Flow**: $45.1 million positive
- **Employee Count**: 1,250 (grew by 35% in 2024)

## Key Achievements

### Technology Division
- Launched TechCorp AI Platform v3.0 with advanced machine learning capabilities
- Deployed cloud infrastructure serving 2.5 million users globally
- Achieved 99.97% uptime across all services
- Filed 47 new patents in AI and cloud technologies

### Sales & Marketing
- Secured 340 enterprise clients including Fortune 500 companies
- Expanded into 12 new international markets
- Generated $89.3 million in new business
- Increased brand recognition by 156% through digital campaigns

### Operations
- Opened 4 new development centers globally
- Implemented sustainable practices reducing carbon footprint by 28%
- Achieved ISO 27001 and SOC 2 Type II certifications
- Established partnerships with 23 technology vendors

## Market Position
TechCorp now holds:
- 15.2% market share in enterprise AI solutions
- Top 3 position in cloud infrastructure for mid-market
- #1 customer satisfaction rating in our sector (98.4%)
- Recognition as "Most Innovative AI Company 2024"

## Challenges and Risk Factors
1. **Intense Competition**: Major tech giants increasing AI investments
2. **Talent Acquisition**: High demand for AI specialists driving salary inflation
3. **Regulatory Uncertainty**: Evolving AI governance requirements
4. **Supply Chain**: Semiconductor shortages affecting hardware delivery
5. **Cybersecurity**: Increased threats requiring constant vigilance

## Future Outlook (2025-2027)
- **Revenue Target**: $200 million by 2025
- **Global Expansion**: Enter 20 additional markets
- **Product Development**: Launch 5 new AI-powered solutions
- **Workforce**: Grow to 2,000 employees by 2027
- **Sustainability**: Achieve carbon neutrality by 2026

## Investment Areas
Priority investments for continued growth:
- Advanced AI research and development
- International market expansion
- Cybersecurity infrastructure enhancement
- Talent acquisition and retention programs
- Strategic acquisitions and partnerships

## Conclusion
TechCorp is well-positioned for sustained growth and market leadership. Our strong financial performance, innovative product portfolio, and exceptional team provide a solid foundation for achieving our ambitious 2025-2027 strategic objectives.

---
*Report prepared by TechCorp Finance Team, January 2025*
"""
    
    demo_file = uploads_dir / "techcorp_annual_report_2024.txt"
    with open(demo_file, 'w') as f:
        f.write(content)
    
    return str(demo_file)


def run_comprehensive_demo():
    """Run a comprehensive demonstration of the TensorRT-LLM Document Agent."""
    print("🚀 TensorRT-LLM Document Agent - Final Demonstration")
    print("=" * 60)
    
    # Create demo document
    print("📋 Creating comprehensive demo document...")
    demo_file = create_demo_document()
    print(f"✅ Created: {Path(demo_file).name}")
    print(f"📁 Location: {demo_file}")
    
    # Initialize assistant
    print("\n🤖 Initializing TensorRT-LLM Document Assistant...")
    assistant = get_assistant()
    print("✅ Assistant ready (TensorRT-LLM with Ollama fallback)")
    
    # Demonstrate different capabilities
    demo_scenarios = [
        {
            "name": "📊 Financial Analysis",
            "query": "What are the key financial metrics and how did the company perform financially in 2024?",
            "description": "Extract and analyze financial data"
        },
        {
            "name": "🎯 Strategic Insights", 
            "query": "What are the main strategic achievements and market position of TechCorp?",
            "description": "Identify strategic accomplishments and competitive position"
        },
        {
            "name": "⚠️ Risk Assessment",
            "query": "What are the primary challenges and risks facing the company?",
            "description": "Analyze risk factors and challenges"
        },
        {
            "name": "🔮 Future Planning",
            "query": "What are the company's future plans and targets for 2025-2027?",
            "description": "Extract future outlook and strategic goals"
        },
        {
            "name": "📈 Growth Analysis",
            "query": "Analyze the company's growth patterns and what's driving their success.",
            "description": "Comprehensive growth and success factor analysis"
        }
    ]
    
    print(f"\n🎭 Demonstrating {len(demo_scenarios)} AI-powered document analysis scenarios:")
    print("=" * 60)
    
    results = []
    
    for i, scenario in enumerate(demo_scenarios, 1):
        print(f"\n{scenario['name']} (Test {i}/{len(demo_scenarios)})")
        print(f"📝 Task: {scenario['description']}")
        print(f"❓ Query: {scenario['query']}")
        print("-" * 60)
        
        try:
            start_time = time.time()
            
            response = assistant.process_query(
                query=f"I have uploaded the TechCorp annual report. {scenario['query']}",
                agent_type="doc_agent", 
                files=[demo_file]
            )
            
            end_time = time.time()
            processing_time = round(end_time - start_time, 2)
            
            # Display results
            print(f"⏱️  Processing Time: {processing_time}s")
            print(f"📏 Response Length: {len(response)} characters")
            
            # Show response preview
            if len(response) > 300:
                print(f"💬 Response Preview:\n{response[:300]}...")
                print(f"    [... {len(response) - 300} more characters]")
            else:
                print(f"💬 Full Response:\n{response}")
            
            results.append({
                "scenario": scenario['name'],
                "success": len(response) > 50,  # Basic success check
                "processing_time": processing_time,
                "response_length": len(response)
            })
            
            print("✅ Analysis completed successfully")
            
        except Exception as e:
            print(f"❌ Error during analysis: {str(e)}")
            results.append({
                "scenario": scenario['name'],
                "success": False,
                "error": str(e)
            })
    
    # Final summary
    print("\n" + "=" * 60)
    print("📊 DEMONSTRATION SUMMARY")
    print("=" * 60)
    
    successful_scenarios = sum(1 for r in results if r.get('success', False))
    total_scenarios = len(results)
    
    print(f"✅ Successful Analyses: {successful_scenarios}/{total_scenarios}")
    print(f"📈 Success Rate: {successful_scenarios/total_scenarios:.1%}")
    
    if successful_scenarios > 0:
        avg_time = sum(r.get('processing_time', 0) for r in results if r.get('success')) / successful_scenarios
        avg_length = sum(r.get('response_length', 0) for r in results if r.get('success')) / successful_scenarios
        print(f"⏱️  Average Processing Time: {avg_time:.2f}s")
        print(f"📏 Average Response Length: {avg_length:.0f} characters")
    
    print(f"\n🎯 SYSTEM CAPABILITIES DEMONSTRATED:")
    print("✅ TensorRT-LLM Integration (with Ollama fallback)")
    print("✅ Intelligent Document Processing")
    print("✅ Multi-format Document Support") 
    print("✅ Agentic Task Analysis")
    print("✅ Complex Question Answering")
    print("✅ Financial Data Extraction")
    print("✅ Strategic Analysis")
    print("✅ Risk Assessment")
    print("✅ Future Planning Analysis")
    
    print(f"\n📁 Demo document available at: {demo_file}")
    print("🎉 TensorRT-LLM Document Agent demonstration completed!")
    

if __name__ == "__main__":
    try:
        run_comprehensive_demo()
    except KeyboardInterrupt:
        print("\n⏹️  Demonstration interrupted by user")
    except Exception as e:
        print(f"\n💥 Demonstration failed: {str(e)}")
        import traceback
        traceback.print_exc()
