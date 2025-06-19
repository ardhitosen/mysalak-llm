import requests
import json
import time
from typing import List, Dict, Tuple
import pandas as pd
from datetime import datetime

class ChatbotTester:
    def __init__(self, base_url: str = "http://localhost:5005"):
        self.base_url = base_url
        self.test_results = []
        
    def test_single_query(self, question: str, expected_keywords: List[str] = None, 
                         expected_response_type: str = "informative") -> Dict:
        """Test a single query and return results"""
        try:
            response = requests.post(
                f"{self.base_url}/chat",
                json={"question": question},
                timeout=30
            )
            
            if response.status_code == 200:
                bot_response = response.json()["response"]
                
                # Calculate metrics
                result = {
                    "question": question,
                    "response": bot_response,
                    "response_length": len(bot_response),
                    "status": "success",
                    "response_time": response.elapsed.total_seconds()
                }
                
                # Check for expected keywords
                if expected_keywords:
                    keyword_matches = sum(1 for keyword in expected_keywords 
                                        if keyword.lower() in bot_response.lower())
                    result["keyword_accuracy"] = keyword_matches / len(expected_keywords)
                    result["expected_keywords"] = expected_keywords
                    result["found_keywords"] = [kw for kw in expected_keywords 
                                              if kw.lower() in bot_response.lower()]
                
                # Check response type
                if expected_response_type == "informative":
                    result["is_informative"] = len(bot_response) > 50
                elif expected_response_type == "general":
                    result["is_general"] = any(greeting in bot_response.lower() 
                                             for greeting in ["halo", "hai", "selamat"])
                
                return result
            else:
                return {
                    "question": question,
                    "response": f"Error: {response.status_code}",
                    "status": "error",
                    "response_time": response.elapsed.total_seconds()
                }
                
        except Exception as e:
            return {
                "question": question,
                "response": f"Exception: {str(e)}",
                "status": "error",
                "response_time": 0
            }
    
    def run_comprehensive_tests(self) -> Dict:
        """Run comprehensive tests on the chatbot"""
        
        # Test cases with expected keywords and response types
        test_cases = [
            # General questions
            {
                "question": "Halo",
                "expected_keywords": ["halo", "mysalak", "bantu"],
                "expected_type": "general"
            },
            {
                "question": "Siapa kamu?",
                "expected_keywords": ["asisten", "chatbot", "mysalak"],
                "expected_type": "general"
            },
            {
                "question": "Apa itu MySalak?",
                "expected_keywords": ["aplikasi", "pertanian", "pintar", "pengendalian", "hama"],
                "expected_type": "informative"
            },
            
            # Login related questions
            {
                "question": "Bagaimana cara login sebagai petani?",
                "expected_keywords": ["nama lengkap", "no telepon", "kelompok tani", "masuk"],
                "expected_type": "informative"
            },
            {
                "question": "Cara login admin?",
                "expected_keywords": ["email", "password", "masuk"],
                "expected_type": "informative"
            },
            {
                "question": "Bagaimana membuat akun baru?",
                "expected_keywords": ["nama lengkap", "no telepon", "kelompok tani", "buat akun"],
                "expected_type": "informative"
            },
            
            # Feature specific questions
            {
                "question": "Apa itu FTD?",
                "expected_keywords": ["fruit flies", "trap", "day", "tangkap"],
                "expected_type": "informative"
            },
            {
                "question": "Bagaimana cara menggunakan fitur foto hitung hama?",
                "expected_keywords": ["kamera", "foto", "hitung", "otomatis"],
                "expected_type": "informative"
            },
            {
                "question": "Apa fungsi peta persebaran hama?",
                "expected_keywords": ["peta", "persebaran", "kebun", "status"],
                "expected_type": "informative"
            },
            
            # Weather related questions
            {
                "question": "Bagaimana cara melihat informasi cuaca?",
                "expected_keywords": ["cuaca", "prediksi", "suhu", "hujan"],
                "expected_type": "informative"
            },
            
            # Article related questions
            {
                "question": "Bagaimana cara mencari artikel?",
                "expected_keywords": ["artikel", "pencarian", "cari"],
                "expected_type": "informative"
            },
            
            # Admin features
            {
                "question": "Bagaimana cara verifikasi anggota?",
                "expected_keywords": ["verifikasi", "anggota", "centang"],
                "expected_type": "informative"
            },
            {
                "question": "Bagaimana cara mengirim peringatan ke kelompok tani?",
                "expected_keywords": ["peringatan", "notifikasi", "kirim"],
                "expected_type": "informative"
            },
            
            # Edge cases
            {
                "question": "Apa yang tidak ada dalam panduan?",
                "expected_keywords": ["maaf", "tidak memiliki", "informasi"],
                "expected_type": "informative"
            },
            {
                "question": "",
                "expected_keywords": [],
                "expected_type": "error"
            },
            {
                "question": "x" * 1000,  # Very long question
                "expected_keywords": [],
                "expected_type": "informative"
            }
        ]
        
        print("Starting comprehensive chatbot tests...")
        print("=" * 50)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"Test {i}/{len(test_cases)}: {test_case['question'][:50]}...")
            
            result = self.test_single_query(
                test_case["question"],
                test_case["expected_keywords"],
                test_case["expected_type"]
            )
            
            self.test_results.append(result)
            time.sleep(1)  # Avoid overwhelming the server
        
        return self.calculate_metrics()
    
    def calculate_metrics(self) -> Dict:
        """Calculate comprehensive metrics from test results"""
        
        successful_tests = [r for r in self.test_results if r["status"] == "success"]
        failed_tests = [r for r in self.test_results if r["status"] == "error"]
        
        # Basic metrics
        total_tests = len(self.test_results)
        success_rate = len(successful_tests) / total_tests if total_tests > 0 else 0
        
        # Response time metrics
        response_times = [r["response_time"] for r in successful_tests]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        
        # Keyword accuracy
        keyword_tests = [r for r in successful_tests if "keyword_accuracy" in r]
        avg_keyword_accuracy = sum(r["keyword_accuracy"] for r in keyword_tests) / len(keyword_tests) if keyword_tests else 0
        
        # Response length metrics
        response_lengths = [r["response_length"] for r in successful_tests]
        avg_response_length = sum(response_lengths) / len(response_lengths) if response_lengths else 0
        
        # Informative response rate
        informative_tests = [r for r in successful_tests if r.get("is_informative", False)]
        informative_rate = len(informative_tests) / len(successful_tests) if successful_tests else 0
        
        # General response rate
        general_tests = [r for r in successful_tests if r.get("is_general", False)]
        general_rate = len(general_tests) / len(successful_tests) if successful_tests else 0
        
        metrics = {
            "summary": {
                "total_tests": total_tests,
                "successful_tests": len(successful_tests),
                "failed_tests": len(failed_tests),
                "success_rate": success_rate,
                "avg_keyword_accuracy": avg_keyword_accuracy,
                "informative_response_rate": informative_rate,
                "general_response_rate": general_rate
            },
            "performance": {
                "avg_response_time": avg_response_time,
                "max_response_time": max_response_time,
                "min_response_time": min_response_time,
                "avg_response_length": avg_response_length
            },
            "detailed_results": self.test_results
        }
        
        return metrics
    
    def generate_report(self, metrics: Dict, output_file: str = None) -> str:
        """Generate a detailed test report"""
        
        report = f"""
CHATBOT PERFORMANCE TEST REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*50}

SUMMARY METRICS:
- Total Tests: {metrics['summary']['total_tests']}
- Successful Tests: {metrics['summary']['successful_tests']}
- Failed Tests: {metrics['summary']['failed_tests']}
- Success Rate: {metrics['summary']['success_rate']:.2%}
- Average Keyword Accuracy: {metrics['summary']['avg_keyword_accuracy']:.2%}
- Informative Response Rate: {metrics['summary']['informative_response_rate']:.2%}
- General Response Rate: {metrics['summary']['general_response_rate']:.2%}

PERFORMANCE METRICS:
- Average Response Time: {metrics['performance']['avg_response_time']:.3f}s
- Maximum Response Time: {metrics['performance']['max_response_time']:.3f}s
- Minimum Response Time: {metrics['performance']['min_response_time']:.3f}s
- Average Response Length: {metrics['performance']['avg_response_length']:.0f} characters

DETAILED RESULTS:
"""
        
        for i, result in enumerate(metrics['detailed_results'], 1):
            report += f"\nTest {i}:\n"
            report += f"  Question: {result['question']}\n"
            report += f"  Status: {result['status']}\n"
            report += f"  Response Time: {result['response_time']:.3f}s\n"
            
            if result['status'] == 'success':
                report += f"  Response Length: {result['response_length']} chars\n"
                if 'keyword_accuracy' in result:
                    report += f"  Keyword Accuracy: {result['keyword_accuracy']:.2%}\n"
                    report += f"  Expected Keywords: {result.get('expected_keywords', [])}\n"
                    report += f"  Found Keywords: {result.get('found_keywords', [])}\n"
                report += f"  Response: {result['response'][:100]}...\n"
            else:
                report += f"  Error: {result['response']}\n"
            
            report += "-" * 40 + "\n"
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"Report saved to {output_file}")
        
        return report
    
    def save_results_to_csv(self, filename: str = "chatbot_test_results.csv"):
        """Save test results to CSV file"""
        df = pd.DataFrame(self.test_results)
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"Results saved to {filename}")

def main():
    # Initialize tester
    tester = ChatbotTester("http://localhost:5005")
    
    # Run tests
    print("Starting chatbot performance tests...")
    metrics = tester.run_comprehensive_tests()
    
    # Generate and display report
    report = tester.generate_report(metrics, "chatbot_test_report.txt")
    print(report)
    
    # Save results to CSV
    tester.save_results_to_csv()
    
    # Print summary
    print("\n" + "="*50)
    print("TEST SUMMARY:")
    print(f"Success Rate: {metrics['summary']['success_rate']:.2%}")
    print(f"Average Keyword Accuracy: {metrics['summary']['avg_keyword_accuracy']:.2%}")
    print(f"Average Response Time: {metrics['performance']['avg_response_time']:.3f}s")
    print("="*50)

if __name__ == "__main__":
    main() 