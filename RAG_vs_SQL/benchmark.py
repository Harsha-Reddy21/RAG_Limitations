import time
import json
import pandas as pd
from datetime import datetime

from sql_agent import query_with_sql_agent, direct_sql_query, SAMPLE_QUESTIONS
from rag_system import query_with_rag

def run_benchmark():
    """Run benchmarking tests for both RAG and SQL Agent approaches."""
    results = []
    
    print("Starting benchmarking...")
    
    for i, question in enumerate(SAMPLE_QUESTIONS):
        print(f"Processing question {i+1}/{len(SAMPLE_QUESTIONS)}: {question}")
        
        # Test SQL Agent
        start_time = time.time()
        sql_result = query_with_sql_agent(question)
        sql_time = time.time() - start_time
        
        # Test direct SQL query (alternative SQL approach)
        start_time = time.time()
        direct_sql_result = direct_sql_query(question)
        direct_sql_time = time.time() - start_time
        
        # Test RAG
        start_time = time.time()
        rag_result = query_with_rag(question)
        rag_time = time.time() - start_time
        
        # Store results
        results.append({
            "question": question,
            "sql_agent": {
                "result": sql_result.get("result", "Error"),
                "time": sql_time,
                "success": sql_result.get("success", False)
            },
            "direct_sql": {
                "result": direct_sql_result.get("results", "Error"),
                "sql_query": direct_sql_result.get("sql", ""),
                "time": direct_sql_time,
                "success": direct_sql_result.get("success", False)
            },
            "rag": {
                "result": rag_result.get("result", "Error"),
                "time": rag_time,
                "success": rag_result.get("success", False)
            }
        })
        
        # Save intermediate results
        with open(f"benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
    
    return results

def analyze_results(results):
    """Analyze benchmark results and create a comparison report."""
    # Create dataframe for analysis
    df = pd.DataFrame({
        "question": [r["question"] for r in results],
        "sql_agent_time": [r["sql_agent"]["time"] for r in results],
        "sql_agent_success": [r["sql_agent"]["success"] for r in results],
        "direct_sql_time": [r["direct_sql"]["time"] for r in results],
        "direct_sql_success": [r["direct_sql"]["success"] for r in results],
        "rag_time": [r["rag"]["time"] for r in results],
        "rag_success": [r["rag"]["success"] for r in results]
    })
    
    # Calculate summary statistics
    summary = {
        "avg_time": {
            "sql_agent": df["sql_agent_time"].mean(),
            "direct_sql": df["direct_sql_time"].mean(),
            "rag": df["rag_time"].mean()
        },
        "success_rate": {
            "sql_agent": df["sql_agent_success"].mean() * 100,
            "direct_sql": df["direct_sql_success"].mean() * 100,
            "rag": df["rag_success"].mean() * 100
        },
        "fastest_approach_count": {
            "sql_agent": sum(df.apply(lambda row: row["sql_agent_time"] < row["rag_time"] and row["sql_agent_time"] < row["direct_sql_time"], axis=1)),
            "direct_sql": sum(df.apply(lambda row: row["direct_sql_time"] < row["rag_time"] and row["direct_sql_time"] < row["sql_agent_time"], axis=1)),
            "rag": sum(df.apply(lambda row: row["rag_time"] < row["sql_agent_time"] and row["rag_time"] < row["direct_sql_time"], axis=1))
        }
    }
    
    # Generate report
    report = f"""
    # Performance Benchmark Report: RAG vs SQL Agent
    
    ## Summary Statistics
    
    | Metric | SQL Agent | Direct SQL | RAG |
    |--------|-----------|------------|-----|
    | Average Response Time (s) | {summary['avg_time']['sql_agent']:.2f} | {summary['avg_time']['direct_sql']:.2f} | {summary['avg_time']['rag']:.2f} |
    | Success Rate (%) | {summary['success_rate']['sql_agent']:.1f} | {summary['success_rate']['direct_sql']:.1f} | {summary['success_rate']['rag']:.1f} |
    | Fastest Approach Count | {summary['fastest_approach_count']['sql_agent']} | {summary['fastest_approach_count']['direct_sql']} | {summary['fastest_approach_count']['rag']} |
    
    ## Detailed Results
    
    """
    
    for i, row in df.iterrows():
        report += f"### Question {i+1}: {row['question']}\n\n"
        report += f"- SQL Agent: {row['sql_agent_time']:.2f}s, Success: {row['sql_agent_success']}\n"
        report += f"- Direct SQL: {row['direct_sql_time']:.2f}s, Success: {row['direct_sql_success']}\n"
        report += f"- RAG: {row['rag_time']:.2f}s, Success: {row['rag_success']}\n\n"
    
    # Save report
    with open("benchmark_report.md", "w") as f:
        f.write(report)
    
    return summary

if __name__ == "__main__":
    results = run_benchmark()
    summary = analyze_results(results)
    print("Benchmark completed. Results saved to benchmark_report.md") 