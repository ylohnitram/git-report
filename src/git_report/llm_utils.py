from openai import OpenAI

def analyze_commit_with_llm(commit_message, diff, api_key, model="gpt-4"):
    """Use LLM to analyze commit message and code changes"""
    if not api_key:
        return "LLM analysis unavailable - missing API key"
    
    try:
        client = OpenAI(api_key=api_key)
        
        # Limit diff size for API
        diff_preview = diff[:4000] + "..." if len(diff) > 4000 else diff
        
        prompt = f"""
        Analyze this Git commit:
        
        # Commit Message
        {commit_message}
        
        # Code Changes
        ```
        {diff_preview}
        ```
        
        Provide:
        1. A concise summary of the changes
        2. The main purpose of this commit
        3. Potential implications or challenges
        4. Suggested improved commit message
        """
        
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Error in LLM analysis: {str(e)}"
