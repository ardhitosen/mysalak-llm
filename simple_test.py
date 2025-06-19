#!/usr/bin/env python3
"""
Simple test script for MySalak Chatbot (No pandas required)
Usage: python simple_test.py
"""

import requests
import json
import time
from datetime import datetime

class SimpleChatbotTester:
    def __init__(self, base_url: str = "https://rasa.mysalak.com"):
        self.base_url = base_url
        self.test_results = []
        
    def test_query(self, question: str, expected_keywords: list = None) -> dict:
        """Test a single query"""
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/chat",
                json={"question": question},
                timeout=30
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                bot_response = response.json()["response"]
                
                result = {
                    "question": question,
                    "response": bot_response,
                    "response_length": len(bot_response),
                    "status": "success",
                    "response_time": response_time
                }
                
                # Check keywords if provided
                if expected_keywords:
                    found_keywords = []
                    for keyword in expected_keywords:
                        if keyword.lower() in bot_response.lower():
                            found_keywords.append(keyword)
                    
                    result["expected_keywords"] = expected_keywords
                    result["found_keywords"] = found_keywords
                    result["keyword_accuracy"] = len(found_keywords) / len(expected_keywords)
                
                return result
            else:
                return {
                    "question": question,
                    "response": f"Error: {response.status_code}",
                    "status": "error",
                    "response_time": response_time
                }
                
        except Exception as e:
            return {
                "question": question,
                "response": f"Exception: {str(e)}",
                "status": "error",
                "response_time": 0
            }
    
    def run_tests(self):
        """Run all tests"""
        
        test_cases = [
            # General questions
            ("Halo", ["halo", "mysalak", "bantu"]),
            ("Siapa kamu?", ["asisten", "chatbot", "mysalak"]),
            ("Apa itu MySalak?", ["aplikasi", "pertanian", "pintar", "pengendalian", "hama"]),
            
            # Login questions
            ("Bagaimana cara login sebagai petani?", ["nama lengkap", "no telepon", "kelompok tani", "masuk"]),
            ("Cara login admin?", ["email", "password", "masuk"]),
            ("Bagaimana membuat akun baru?", ["nama lengkap", "no telepon", "kelompok tani", "buat akun"]),
            
            # Feature questions
            ("Apa itu FTD?", ["fruit flies", "trap", "day", "tangkap"]),
            ("Bagaimana cara menggunakan fitur foto hitung hama?", ["kamera", "foto", "hitung", "otomatis"]),
            ("Apa fungsi peta persebaran hama?", ["peta", "persebaran", "kebun", "status"]),
            
            # Weather questions
            ("Bagaimana cara melihat informasi cuaca?", ["cuaca", "prediksi", "suhu", "hujan"]),
            
            # Article questions
            ("Bagaimana cara mencari artikel?", ["artikel", "pencarian", "cari"]),
            
            # Admin questions
            ("Bagaimana cara verifikasi anggota?", ["verifikasi", "anggota", "centang"]),
            ("Bagaimana cara mengirim peringatan ke kelompok tani?", ["peringatan", "notifikasi", "kirim"]),
            
            # Edge cases
            ("Apa yang tidak ada dalam panduan?", ["maaf", "tidak memiliki", "informasi"]),
            ("", []),
        ]
        
        print("Starting MySalak Chatbot Tests...")
        print("=" * 50)
        
        for i, (question, keywords) in enumerate(test_cases, 1):
            print(f"Test {i}/{len(test_cases)}: {question[:50]}...")
            result = self.test_query(question, keywords)
            self.test_results.append(result)
            time.sleep(1)  # Avoid overwhelming the server
        
        return self.calculate_metrics()
    
    def calculate_metrics(self):
        """Calculate metrics from test results"""
        
        successful_tests = [r for r in self.test_results if r["status"] == "success"]
        failed_tests = [r for r in self.test_results if r["status"] == "error"]
        
        # Basic metrics
        total_tests = len(self.test_results)
        success_rate = len(successful_tests) / total_tests if total_tests > 0 else 0
        
        # Response time metrics
        response_times = [r["response_time"] for r in successful_tests]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Keyword accuracy
        keyword_tests = [r for r in successful_tests if "keyword_accuracy" in r]
        avg_keyword_accuracy = sum(r["keyword_accuracy"] for r in keyword_tests) / len(keyword_tests) if keyword_tests else 0
        
        # Response length
        response_lengths = [r["response_length"] for r in successful_tests]
        avg_response_length = sum(response_lengths) / len(response_lengths) if response_lengths else 0
        
        return {
            "total_tests": total_tests,
            "successful_tests": len(successful_tests),
            "failed_tests": len(failed_tests),
            "success_rate": success_rate,
            "avg_keyword_accuracy": avg_keyword_accuracy,
            "avg_response_time": avg_response_time,
            "avg_response_length": avg_response_length,
            "results": self.test_results
        }
    
    def print_report(self, metrics):
        """Print test report"""
        
        print("\n" + "=" * 50)
        print("MY SALAK CHATBOT TEST RESULTS")
        print("=" * 50)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        print("SUMMARY:")
        print(f"  Total Tests: {metrics['total_tests']}")
        print(f"  Successful: {metrics['successful_tests']}")
        print(f"  Failed: {metrics['failed_tests']}")
        print(f"  Success Rate: {metrics['success_rate']:.2%}")
        print(f"  Average Keyword Accuracy: {metrics['avg_keyword_accuracy']:.2%}")
        print(f"  Average Response Time: {metrics['avg_response_time']:.3f}s")
        print(f"  Average Response Length: {metrics['avg_response_length']:.0f} chars")
        
        print("\n" + "=" * 50)
        print("DETAILED RESULTS:")
        print("=" * 50)
        
        for i, result in enumerate(metrics['results'], 1):
            print(f"\nTest {i}:")
            print(f"  Question: {result['question']}")
            print(f"  Status: {result['status']}")
            print(f"  Response Time: {result['response_time']:.3f}s")
            
            if result['status'] == 'success':
                print(f"  Response Length: {result['response_length']} chars")
                if 'keyword_accuracy' in result:
                    print(f"  Keyword Accuracy: {result['keyword_accuracy']:.2%}")
                    print(f"  Expected: {result['expected_keywords']}")
                    print(f"  Found: {result['found_keywords']}")
                print(f"  Response: {result['response'][:100]}...")
            else:
                print(f"  Error: {result['response']}")
            
            print("-" * 40)
        
        # Performance assessment
        print("\n" + "=" * 50)
        print("PERFORMANCE ASSESSMENT:")
        print("=" * 50)
        
        success_rate = metrics['success_rate']
        keyword_accuracy = metrics['avg_keyword_accuracy']
        response_time = metrics['avg_response_time']
        
        if success_rate >= 0.9:
            print("✓ EXCELLENT: High success rate")
        elif success_rate >= 0.7:
            print("✓ GOOD: Acceptable success rate")
        elif success_rate >= 0.5:
            print("⚠ FAIR: Moderate success rate")
        else:
            print("✗ POOR: Low success rate")
        
        if keyword_accuracy >= 0.8:
            print("✓ EXCELLENT: High keyword accuracy")
        elif keyword_accuracy >= 0.6:
            print("✓ GOOD: Acceptable keyword accuracy")
        elif keyword_accuracy >= 0.4:
            print("⚠ FAIR: Moderate keyword accuracy")
        else:
            print("✗ POOR: Low keyword accuracy")
        
        if response_time <= 2.0:
            print("✓ EXCELLENT: Fast response time")
        elif response_time <= 5.0:
            print("✓ GOOD: Acceptable response time")
        elif response_time <= 10.0:
            print("⚠ FAIR: Slow response time")
        else:
            print("✗ POOR: Very slow response time")

def main():
    print("MySalak Chatbot Simple Test Suite")
    print("=" * 50)
    
    # Check if chatbot is running
    try:
        tester = SimpleChatbotTester("https://rasa.mysalak.com")
        print("✓ Chatbot server detected at https://rasa.mysalak.com")
    except Exception as e:
        print("✗ Error: Could not connect to chatbot server")
        print("Make sure your chatbot is running on https://rasa.mysalak.com")
        print(f"Error details: {e}")
        return
    
    # Run tests
    print("\nStarting tests...")
    metrics = tester.run_tests()
    
    # Print report
    tester.print_report(metrics)

if __name__ == "__main__":
    main() 