#!/usr/bin/env python3
"""
Simple test runner for the MySalak Chatbot
Usage: python run_tests.py
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from test_chatbot import ChatbotTester

def main():
    print("MySalak Chatbot Performance Test Suite")
    print("=" * 50)
    
    # Check if chatbot is running
    try:
        tester = ChatbotTester("http://localhost:5005")
        print("✓ Chatbot server detected at http://localhost:5005")
    except Exception as e:
        print("✗ Error: Could not connect to chatbot server")
        print("Make sure your chatbot is running on port 5005")
        print(f"Error details: {e}")
        return
    
    # Run tests
    print("\nStarting tests...")
    metrics = tester.run_comprehensive_tests()
    
    # Display results
    print("\n" + "=" * 50)
    print("TEST RESULTS SUMMARY")
    print("=" * 50)
    print(f"Total Tests: {metrics['summary']['total_tests']}")
    print(f"Successful: {metrics['summary']['successful_tests']}")
    print(f"Failed: {metrics['summary']['failed_tests']}")
    print(f"Success Rate: {metrics['summary']['success_rate']:.2%}")
    print(f"Average Keyword Accuracy: {metrics['summary']['avg_keyword_accuracy']:.2%}")
    print(f"Average Response Time: {metrics['performance']['avg_response_time']:.3f}s")
    print(f"Average Response Length: {metrics['performance']['avg_response_length']:.0f} chars")
    
    # Generate detailed report
    report = tester.generate_report(metrics, "chatbot_test_report.txt")
    tester.save_results_to_csv("chatbot_test_results.csv")
    
    print("\nDetailed report saved to: chatbot_test_report.txt")
    print("CSV results saved to: chatbot_test_results.csv")
    
    # Performance assessment
    print("\n" + "=" * 50)
    print("PERFORMANCE ASSESSMENT")
    print("=" * 50)
    
    success_rate = metrics['summary']['success_rate']
    keyword_accuracy = metrics['summary']['avg_keyword_accuracy']
    response_time = metrics['performance']['avg_response_time']
    
    if success_rate >= 0.9:
        print("✓ Excellent: High success rate")
    elif success_rate >= 0.7:
        print("✓ Good: Acceptable success rate")
    elif success_rate >= 0.5:
        print("⚠ Fair: Moderate success rate")
    else:
        print("✗ Poor: Low success rate")
    
    if keyword_accuracy >= 0.8:
        print("✓ Excellent: High keyword accuracy")
    elif keyword_accuracy >= 0.6:
        print("✓ Good: Acceptable keyword accuracy")
    elif keyword_accuracy >= 0.4:
        print("⚠ Fair: Moderate keyword accuracy")
    else:
        print("✗ Poor: Low keyword accuracy")
    
    if response_time <= 2.0:
        print("✓ Excellent: Fast response time")
    elif response_time <= 5.0:
        print("✓ Good: Acceptable response time")
    elif response_time <= 10.0:
        print("⚠ Fair: Slow response time")
    else:
        print("✗ Poor: Very slow response time")

if __name__ == "__main__":
    main() 