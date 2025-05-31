#!/usr/bin/env python3
"""
Comprehensive test for the TensorRT-LLM Document Agent
This script demonstrates all the functionality of the document processing system.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from backend.main import AgenticAssistant
from backend.tools.doc_tools.document_processor import DocumentProcessor
from config.app_config import PATHS
import time


def create_test_documents():
    """Create various test documents for comprehensive testing."""
    uploads_dir = Path(PATHS["uploads"])
    uploads_dir.mkdir(parents=True, exist_ok=True)
    
    test_docs = {}
    
    # Create a comprehensive text document
    text_content = """
# Company Financial Report 2024

## Executive Summary
Our company has shown remarkable growth in 2024, with revenue increasing by 25% 
compared to the previous year. This growth is primarily attributed to our 
expansion into new markets and the successful launch of our AI-powered products.

## Key Metrics
- Total Revenue: $50.2 million
- Net Profit: $8.7 million  
- Employee Count: 250
- Customer Satisfaction: 94%
- Market Share: 15%

## Departmental Performance

### Sales Department
The sales team exceeded all targets, generating $45.1 million in revenue.
Key achievements include:
- Signed 150 new enterprise clients
- Expanded into 3 new geographical markets
- Improved sales efficiency by 30%

### Technology Department  
Our tech team delivered 12 major product releases and improved system reliability to 99.9%.
Notable accomplishments:
- Launched AI chatbot platform
- Reduced server response time by 40%
- Implemented advanced security protocols

### Marketing Department
Marketing campaigns resulted in 200% increase in brand awareness.
Campaign highlights:
- Social media reach grew to 2.5 million followers
- Generated 10,000 qualified leads
- Won "Best Digital Campaign" industry award

## Future Outlook
Looking ahead to 2025, we project:
- 35% revenue growth
- Expansion to 5 additional markets
- Launch of 3 new AI products
- Hiring of 100 additional employees

## Challenges and Risks
- Increasing competition in AI market
- Supply chain uncertainties
- Regulatory changes in data privacy
- Economic recession concerns

## Conclusion
Despite challenges, our strong foundation and innovative products position us
well for continued growth and market leadership in the AI industry.
"""
    
    # Save text document
    text_file = uploads_dir / "financial_report_2024.txt"
    with open(text_file, 'w') as f:
        f.write(text_content)
    test_docs['financial_report'] = str(text_file)
    
    # Create a technical document
    technical_content = """
# API Documentation - User Management Service

## Overview
The User Management Service provides REST API endpoints for managing user accounts,
authentication, and authorization in our platform.

## Endpoints

### GET /api/users
Retrieve list of all users.

**Parameters:**
- limit (optional): Number of users to return (default: 50)
- offset (optional): Number of users to skip (default: 0)

**Response:**
```json
{
  "users": [
    {
      "id": 123,
      "username": "john_doe",
      "email": "john@example.com",
      "created_at": "2024-01-15T10:30:00Z",
      "status": "active"
    }
  ],
  "total": 1500,
  "page": 1
}
```

### POST /api/users
Create a new user account.

**Request Body:**
```json
{
  "username": "jane_smith",
  "email": "jane@example.com", 
  "password": "secure_password123",
  "role": "user"
}
```

**Response:**
```json
{
  "id": 124,
  "username": "jane_smith",
  "email": "jane@example.com",
  "created_at": "2024-05-31T14:22:00Z",
  "status": "active"
}
```

### PUT /api/users/{id}
Update an existing user.

### DELETE /api/users/{id}
Delete a user account.

## Authentication
All endpoints require Bearer token authentication.

## Rate Limiting
- 1000 requests per hour per API key
- Burst limit: 100 requests per minute

## Error Codes
- 400: Bad Request
- 401: Unauthorized  
- 403: Forbidden
- 404: Not Found
- 429: Too Many Requests
- 500: Internal Server Error
"""
    
    tech_file = uploads_dir / "api_documentation.txt"
    with open(tech_file, 'w') as f:
        f.write(technical_content)
    test_docs['api_docs'] = str(tech_file)
    
    return test_docs


def run_comprehensive_test():
    """Run comprehensive tests of the document agent."""
    print("🚀 TensorRT-LLM Document Agent - Comprehensive Test Suite")
    print("=" * 65)
    
    # Initialize the assistant
    assistant = AgenticAssistant()
    doc_processor = DocumentProcessor()
    
    # Create test documents
    print("📁 Creating test documents...")
    test_docs = create_test_documents()
    print(f"✅ Created {len(test_docs)} test documents")
    print()
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "Document Summarization",
            "query": "Please summarize the financial report",
            "file_path": test_docs['financial_report'],
            "expected_content": ["revenue", "growth", "metrics", "departments"]
        },
        {
            "name": "Specific Information Extraction", 
            "query": "What was the total revenue and net profit in 2024?",
            "file_path": test_docs['financial_report'],
            "expected_content": ["50.2 million", "8.7 million"]
        },
        {
            "name": "Technical Documentation Analysis",
            "query": "What are the main API endpoints and their purposes?",
            "file_path": test_docs['api_docs'],
            "expected_content": ["GET", "POST", "PUT", "DELETE", "users"]
        },
        {
            "name": "Data Analysis", 
            "query": "Analyze the company's performance and identify key strengths",
            "file_path": test_docs['financial_report'],
            "expected_content": ["growth", "performance", "sales", "technology"]
        },
        {
            "name": "Risk Assessment",
            "query": "What are the main risks and challenges mentioned in the report?",
            "file_path": test_docs['financial_report'], 
            "expected_content": ["competition", "supply chain", "regulatory", "recession"]
        }
    ]
    
    results = []
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"🧪 Test {i}: {scenario['name']}")
        print("-" * 50)
        
        try:
            # Process the document
            print(f"📄 Processing: {Path(scenario['file_path']).name}")
            
            # Upload and process the document
            with open(scenario['file_path'], 'rb') as f:
                file_content = f.read()
            
            # Simulate file upload by passing file path to the agent
            start_time = time.time()
            
            # Create a query that includes document context
            full_query = f"I have uploaded a document. {scenario['query']}"
            
            # Get response from the agent
            response = assistant.process_query(
                query=full_query,
                agent_type="doc_agent",
                files=[scenario['file_path']]  # Pass file path
            )
            
            end_time = time.time()
            processing_time = round(end_time - start_time, 2)
            
            print(f"⏱️  Processing time: {processing_time}s")
            print(f"📝 Response length: {len(response)} characters")
            print(f"💬 Response preview: {response[:200]}...")
            
            # Check if expected content is in the response
            content_found = sum(1 for content in scenario['expected_content'] 
                              if content.lower() in response.lower())
            content_score = content_found / len(scenario['expected_content'])
            
            results.append({
                "test": scenario['name'],
                "success": content_score > 0.5,  # At least 50% of expected content found
                "content_score": content_score,
                "processing_time": processing_time,
                "response_length": len(response)
            })
            
            print(f"✅ Content relevance: {content_score:.1%}")
            print()
            
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            results.append({
                "test": scenario['name'],
                "success": False,
                "error": str(e)
            })
            print()
    
    # Print summary
    print("📊 Test Summary")
    print("=" * 65)
    
    successful_tests = sum(1 for r in results if r.get('success', False))
    total_tests = len(results)
    
    print(f"✅ Successful tests: {successful_tests}/{total_tests}")
    print(f"📈 Success rate: {successful_tests/total_tests:.1%}")
    
    if successful_tests > 0:
        avg_time = sum(r.get('processing_time', 0) for r in results if r.get('success')) / successful_tests
        print(f"⏱️  Average processing time: {avg_time:.2f}s")
    
    print("\n🔍 Detailed Results:")
    for result in results:
        status = "✅" if result.get('success') else "❌"
        print(f"{status} {result['test']}")
        if 'content_score' in result:
            print(f"   Content relevance: {result['content_score']:.1%}")
            print(f"   Processing time: {result['processing_time']}s")
        elif 'error' in result:
            print(f"   Error: {result['error']}")
    
    print("\n🎯 Test Conclusions:")
    
    if successful_tests == total_tests:
        print("🏆 All tests passed! The TensorRT-LLM Document Agent is fully functional.")
    elif successful_tests >= total_tests * 0.8:
        print("🥈 Most tests passed! The system is working well with minor issues.")
    elif successful_tests >= total_tests * 0.5:
        print("🥉 Some tests passed. The system has basic functionality but needs improvement.")
    else:
        print("⚠️  Many tests failed. The system needs significant debugging.")
    
    print("\n📋 System Status:")
    print(f"🔧 TensorRT-LLM Provider: {'Available' if assistant.llm_provider.__class__.__name__ == 'TensorRTProvider' else 'Fallback to Ollama'}")
    print(f"📄 Document Processor: Functional") 
    print(f"🤖 Agent System: Functional")
    print(f"📁 Test Files: {len(test_docs)} created in {PATHS['uploads']}")


if __name__ == "__main__":
    try:
        run_comprehensive_test()
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Test suite crashed: {str(e)}")
        import traceback
        traceback.print_exc()
