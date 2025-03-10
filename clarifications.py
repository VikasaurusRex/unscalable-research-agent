from pydantic import BaseModel
from ollama import chat  # Add this import
import re
import os
from datetime import datetime

local_model = 'deepseek-r1:32b'

class Question(BaseModel):
    next_question: str
    is_complete: bool
    research_goal: str

def clean_response(response_str: str) -> str:
    """Extract only the JSON content between ```json and ``` markers."""
    pattern = r'```json\s*(.*?)\s*```'
    match = re.search(pattern, response_str, re.DOTALL)
    if match:
        return match.group(1).strip()
    return response_str.strip()

def get_next_question(context: str, model: str = local_model) -> Question:
    """Get the next question based on current context."""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    system_prompt = (
        f"It is currently {current_time}. You are an expert researcher understanding the goal of a research paper. \n"
        "next_question. Provide exactly one next question to narrow the scope and purpose of the report... (only report scope and scale questions)\n"
        "is_complete. Enough clarity on scope and purpose of the research to begin architecting the report...\n"
        "research_goal. Summarize current understanding of the goal...\n"
        "Note: The goal is the scope and aims of the research.\n"
        "Respond with EXACTLY one JSON object with parameters: `next_question`, `is_complete`, `research_goal`"
    )
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": context}
    ]
    
    response_str = ""
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\nConsidering clarifying questions...\n")
    
    for part in chat(model, messages=messages, stream=True):
        content = part['message']['content']
        response_str += content
        print(content, end='', flush=True)
    
    try:
        return Question.model_validate_json(clean_response(response_str))


    except Exception as e:
        print(f"Error parsing response: {e}")
        # Extract any thinking logic between <think> tags
        think_match = re.search(r'<think>(.*?)</think>', response_str, flags=re.DOTALL)
        response_logic = think_match.group(1).strip() if think_match else 'Goal same as prompt.'
        
        # Remove think tags from final response
        response_str = re.sub(r'<think>.*?</think>', '', response_str, flags=re.DOTALL)
        
        # Fallback to basic Question object if JSON parsing failed
        return Question(
            next_question=f"{response_str}\n('complete' to finish)",
            is_complete=False,
            research_goal=response_logic
        )

def gather_clarifications(research_query: str) -> str:
    """Gather clarifications on research scope and research aims through questions."""
    context = f"INITIAL QUERY: {research_query}\n\nQUESTION HISTORY:\n"
    question_count = 0
    answer = ""
    
    while True:
        # Append completion hints based on question count
        current_context = context
        
        response = get_next_question(current_context)

        os.system('cls' if os.name == 'nt' else 'clear')
        
        print(f"You want: \033[91m\n{research_query}\033[0m")
        print(f"\033[92m\n{response.research_goal}\033[0m")
        
        if response.is_complete:
            context += f"\nFINAL RESEARCH GOAL: {response.research_goal}"
            return context
        
        question_count += 1
        if question_count > 5:
            answer = input(f"\n{response.next_question}\nYour answer ('complete' to begin research): ")
            if question_count >= 12:
                answer += "\nNOTE: We have gathered extensive information through 12 questions. The information is now certifiably complete, please return true to avoid annoying the user."
            elif question_count >= 6:
                answer += "\nNOTE: We have gathered substantial information through 6 questions. The information is likely sufficiently complete."
        else:
            answer = input(f"\n{response.next_question}\nYour answer: ")
            if answer.lower() == 'complete':
                context += f"\nFINAL RESEARCH GOAL: {response.research_goal}"
                context += "\n\nNOTE: Research goal is now complete based on user input."
                return context
        
        

        
        context += f"\nQ: {response.next_question}\nA: {answer}\n"
