"""
Simple Child Assessment Analysis Function

This module provides a straightforward function to analyze child responses
from the question_responses table and generate readable insights.
"""

import sqlite3
from collections import defaultdict
from datetime import datetime


def analyze_child_assessment_responses(child_id: int, db_path: str = "assessment.db") -> str:
    """
    Analyze question response data for a child and return a readable summary.
    
    Args:
        child_id (int): The ID of the child to analyze
        db_path (str): Path to the SQLite database
    
    Returns:
        str: A readable summary with insights and recommendations
    """
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get child's name and info
        cursor.execute("SELECT child_name, age_group FROM children WHERE id = ?", (child_id,))
        child_info = cursor.fetchone()
        child_name = child_info['child_name'] if child_info else f"Child {child_id}"
        age_group = child_info['age_group'] if child_info else "Unknown"
        
        # Fetch all responses for the child
        query = """
        SELECT 
            assessment_type,
            question_id,
            question_text,
            child_answer,
            correct_answer,
            is_correct,
            response_time_seconds,
            difficulty_level,
            attempts,
            hints_used,
            created_at
        FROM question_responses 
        WHERE child_id = ?
        ORDER BY created_at DESC
        """
        
        cursor.execute(query, (child_id,))
        responses = cursor.fetchall()
        conn.close()
        
        if not responses:
            return f"No assessment data found for {child_name}. Please complete some assessments first."
        
        # Analyze responses by assessment type
        analysis = defaultdict(lambda: {
            'total': 0,
            'correct': 0,
            'incorrect': 0,
            'accuracy': 0,
            'avg_time': 0,
            'total_time': 0,
            'hints_used': 0,
            'total_attempts': 0,
            'strengths': [],
            'weaknesses': [],
            'question_details': []
        })
        
        # Process each response
        for response in responses:
            assessment_type = response['assessment_type']
            is_correct = response['is_correct'] == 'true'
            
            # Basic counts
            analysis[assessment_type]['total'] += 1
            if is_correct:
                analysis[assessment_type]['correct'] += 1
            else:
                analysis[assessment_type]['incorrect'] += 1
            
            # Time tracking
            if response['response_time_seconds']:
                analysis[assessment_type]['total_time'] += response['response_time_seconds']
            
            # Hints and attempts
            analysis[assessment_type]['hints_used'] += response['hints_used'] or 0
            analysis[assessment_type]['total_attempts'] += response['attempts'] or 1
            
            # Store question details for deeper analysis
            analysis[assessment_type]['question_details'].append({
                'question_id': response['question_id'],
                'question_text': response['question_text'],
                'child_answer': response['child_answer'],
                'correct_answer': response['correct_answer'],
                'is_correct': is_correct,
                'difficulty': response['difficulty_level'] or 1
            })
        
        # Calculate percentages and averages
        for assessment_type, data in analysis.items():
            if data['total'] > 0:
                data['accuracy'] = round((data['correct'] / data['total']) * 100, 1)
                data['avg_time'] = round(data['total_time'] / data['total'], 1) if data['total_time'] > 0 else 0
                
                # Analyze specific strengths and weaknesses
                data['strengths'], data['weaknesses'] = analyze_question_patterns(data['question_details'])
        
        # Generate readable summary
        return generate_readable_summary(child_name, age_group, dict(analysis))
        
    except sqlite3.Error as e:
        return f"Database error occurred: {e}"
    except Exception as e:
        return f"An error occurred during analysis: {e}"


def analyze_question_patterns(question_details):
    """Analyze question patterns to identify strengths and weaknesses."""
    strengths = []
    weaknesses = []
    
    # Group questions by type/topic
    topic_performance = defaultdict(lambda: {'correct': 0, 'total': 0})
    
    for question in question_details:
        # Categorize questions based on content
        topic = categorize_question_topic(question['question_text'])
        topic_performance[topic]['total'] += 1
        if question['is_correct']:
            topic_performance[topic]['correct'] += 1
    
    # Identify strengths (>75% accuracy) and weaknesses (<50% accuracy)
    for topic, performance in topic_performance.items():
        accuracy = (performance['correct'] / performance['total']) * 100
        if performance['total'] >= 2:  # Only consider topics with multiple questions
            if accuracy >= 75:
                strengths.append(f"{topic} ({accuracy:.0f}% accuracy)")
            elif accuracy < 50:
                weaknesses.append(f"{topic} ({accuracy:.0f}% accuracy)")
    
    return strengths, weaknesses


def categorize_question_topic(question_text):
    """Categorize a question into a topic based on its content."""
    question_lower = question_text.lower()
    
    # Intelligence categories
    if any(word in question_lower for word in ['count', 'number', 'math', 'calculate', 'add', 'subtract']):
        return 'Mathematical Skills'
    elif any(word in question_lower for word in ['draw', 'color', 'create', 'art', 'picture', 'painting']):
        return 'Artistic Expression'
    elif any(word in question_lower for word in ['sequence', 'order', 'pattern', 'logic', 'next', 'follow']):
        return 'Logical Thinking'
    elif any(word in question_lower for word in ['feel', 'emotion', 'friend', 'share', 'help', 'happy', 'sad']):
        return 'Emotional Recognition'
    
    # Physical categories
    elif any(word in question_lower for word in ['jump', 'run', 'move', 'walk', 'balance', 'hop']):
        return 'Motor Skills'
    elif any(word in question_lower for word in ['catch', 'throw', 'hold', 'grip', 'ball']):
        return 'Hand-Eye Coordination'
    
    # Linguistic categories
    elif any(word in question_lower for word in ['word', 'name', 'vocabulary', 'meaning', 'say']):
        return 'Vocabulary Development'
    elif any(word in question_lower for word in ['story', 'read', 'understand', 'book']):
        return 'Reading Comprehension'
    elif any(word in question_lower for word in ['rhyme', 'sound', 'letter', 'phonics']):
        return 'Phonetic Awareness'
    
    return 'General Skills'


def generate_readable_summary(child_name, age_group, analysis):
    """Generate a comprehensive, readable summary."""
    
    # Calculate overall performance
    total_questions = sum(data['total'] for data in analysis.values())
    total_correct = sum(data['correct'] for data in analysis.values())
    overall_accuracy = round((total_correct / total_questions) * 100, 1) if total_questions > 0 else 0
    
    # Determine performance level
    if overall_accuracy >= 80:
        performance_level = "excellent"
        encouragement = "Keep up the fantastic work!"
    elif overall_accuracy >= 65:
        performance_level = "good"
        encouragement = "Great progress! Continue practicing to maintain this level."
    elif overall_accuracy >= 50:
        performance_level = "satisfactory"
        encouragement = "Good effort! With focused practice, improvement is definitely achievable."
    else:
        performance_level = "developing"
        encouragement = "Every child learns at their own pace. Consistent practice will lead to improvement."
    
    # Start building the summary
    summary = f"""Assessment Analysis for {child_name} (Age Group: {age_group})
{'=' * 60}

OVERALL PERFORMANCE SUMMARY:
{child_name} has completed {total_questions} assessment questions across different developmental areas with an overall accuracy of {overall_accuracy}%. This represents {performance_level} performance for their age group. {encouragement}

"""
    
    # Add detailed analysis for each assessment type
    assessment_names = {
        'intelligence': 'Intellectual Development',
        'physical': 'Physical Development', 
        'linguistic': 'Language Development'
    }
    
    for assessment_type, data in analysis.items():
        type_name = assessment_names.get(assessment_type, assessment_type.title())
        
        summary += f"\n{type_name.upper()}:\n"
        summary += f"Questions completed: {data['total']} | Accuracy: {data['accuracy']}% | "
        summary += f"Correct: {data['correct']} | Incorrect: {data['incorrect']}\n"
        
        if data['avg_time'] > 0:
            summary += f"Average response time: {data['avg_time']} seconds\n"
        
        if data['hints_used'] > 0:
            summary += f"Hints used: {data['hints_used']} times\n"
        
        # Performance description
        if data['accuracy'] >= 80:
            description = f"{child_name} shows excellent mastery in {type_name.lower()}"
        elif data['accuracy'] >= 65:
            description = f"{child_name} demonstrates good understanding of {type_name.lower()}"
        elif data['accuracy'] >= 50:
            description = f"{child_name} shows developing skills in {type_name.lower()}"
        else:
            description = f"{child_name} would benefit from additional support in {type_name.lower()}"
        
        summary += f"\nAnalysis: {description}. "
        
        # Add strengths
        if data['strengths']:
            summary += f"Key strengths include: {', '.join(data['strengths'])}. "
        
        # Add areas for improvement
        if data['weaknesses']:
            summary += f"Areas needing attention: {', '.join(data['weaknesses'])}."
        
        summary += "\n"
    
    # Add specific recommendations
    summary += f"\nRECOMMendations for {child_name}:\n"
    summary += generate_recommendations(analysis, child_name)
    
    summary += f"\nAnalysis completed on: {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}"
    
    return summary


def generate_recommendations(analysis, child_name):
    """Generate specific recommendations based on performance analysis."""
    recommendations = []
    
    for assessment_type, data in analysis.items():
        if data['accuracy'] < 65:  # Areas needing improvement
            if assessment_type == 'intelligence':
                if any('mathematical' in weakness.lower() for weakness in data['weaknesses']):
                    recommendations.append("• Practice counting and number recognition through daily activities like counting toys, snacks, or stairs.")
                if any('artistic' in weakness.lower() for weakness in data['weaknesses']):
                    recommendations.append("• Encourage drawing, coloring, and creative activities. Provide art supplies and dedicated creative time daily.")
                if any('logical' in weakness.lower() for weakness in data['weaknesses']):
                    recommendations.append("• Use simple puzzles, pattern games, and sequencing activities to build logical thinking skills.")
                if any('emotional' in weakness.lower() for weakness in data['weaknesses']):
                    recommendations.append("• Practice identifying emotions through picture books, role-play, and discussing feelings during daily situations.")
            
            elif assessment_type == 'physical':
                recommendations.append("• Increase physical activity time with playground visits, dancing, or simple movement games.")
                recommendations.append("• Practice activities that develop balance and coordination, such as walking on lines or playing catch.")
            
            elif assessment_type == 'linguistic':
                recommendations.append("• Read together daily and engage in conversations about the stories.")
                recommendations.append("• Play word games, sing songs with rhymes, and practice naming objects around the house.")
    
    # Add general positive reinforcement
    strong_areas = []
    for assessment_type, data in analysis.items():
        if data['accuracy'] >= 75:
            type_names = {
                'intelligence': 'intellectual skills',
                'physical': 'physical abilities',
                'linguistic': 'language skills'
            }
            strong_areas.append(type_names.get(assessment_type, assessment_type))
    
    if strong_areas:
        recommendations.append(f"• Continue to nurture {child_name}'s strength in {', '.join(strong_areas)} through challenging and engaging activities.")
    
    recommendations.append(f"• Maintain a positive learning environment and celebrate {child_name}'s progress, no matter how small.")
    recommendations.append("• Remember that every child develops at their own pace. Consistent, patient practice leads to improvement.")
    
    return '\n'.join(recommendations) if recommendations else f"Continue current activities and maintain {child_name}'s excellent progress across all areas!"


# Quick usage example
if __name__ == "__main__":
    # Example usage - replace with actual child ID
    child_id = 3
    analysis_result = analyze_child_assessment_responses(child_id)
    print(analysis_result)
