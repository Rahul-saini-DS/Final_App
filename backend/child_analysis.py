"""
Child Assessment Analysis Module

This module provides comprehensive analysis of child assessment responses,
generating detailed insights and recommendations based on performance data.
"""

import sqlite3
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import json


class ChildAssessmentAnalyzer:
    """Analyzes child assessment responses and provides detailed insights."""
    
    def __init__(self, db_path: str = "assessment.db"):
        """Initialize the analyzer with database path."""
        self.db_path = db_path
        
        # Define assessment type categories and their focus areas
        self.assessment_categories = {
            'intelligence': {
                'name': 'Intellectual Development',
                'areas': {
                    'scientific': 'Scientific Reasoning',
                    'logical': 'Logical Thinking',
                    'artistic': 'Artistic Expression',
                    'socio_emotional': 'Social-Emotional Skills'
                }
            },
            'physical': {
                'name': 'Physical Development',
                'areas': {
                    'motor_skills': 'Motor Skills',
                    'coordination': 'Hand-Eye Coordination',
                    'balance': 'Balance and Stability',
                    'strength': 'Physical Strength'
                }
            },
            'linguistic': {
                'name': 'Language Development',
                'areas': {
                    'vocabulary': 'Vocabulary Development',
                    'comprehension': 'Reading Comprehension',
                    'expression': 'Verbal Expression',
                    'phonics': 'Phonetic Awareness'
                }
            }
        }

    def get_unified_assessment_data(self, child_id: int) -> Dict:
        """Get both question responses and AI task responses for unified analysis."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get question responses
            question_query = """
            SELECT 
                qr.assessment_type,
                qr.question_id,
                qr.question_text,
                qr.child_answer,
                qr.correct_answer,
                qr.is_correct,
                qr.response_time_seconds,
                qr.difficulty_level,
                qr.attempts,
                qr.hints_used,
                qr.ai_confidence_score,
                qr.created_at,
                ar.age_group
            FROM question_responses qr
            LEFT JOIN assessment_results ar ON qr.result_id = ar.id
            WHERE qr.child_id = ?
            ORDER BY qr.created_at DESC
            """
            
            cursor.execute(question_query, (child_id,))
            question_responses = [dict(row) for row in cursor.fetchall()]
            
            # Get AI task responses
            ai_task_query = """
            SELECT 
                atr.task_type,
                atr.task_name,
                atr.success_count,
                atr.total_attempts,
                atr.completion_time_seconds,
                atr.success_rate,
                atr.ai_feedback,
                atr.was_completed,
                atr.was_skipped,
                atr.created_at,
                ar.age_group
            FROM ai_task_responses atr
            LEFT JOIN assessment_results ar ON atr.result_id = ar.id
            WHERE atr.child_id = ?
            ORDER BY atr.created_at DESC
            """
            
            cursor.execute(ai_task_query, (child_id,))
            ai_task_responses = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            
            return {
                'question_responses': question_responses,
                'ai_task_responses': ai_task_responses
            }
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return {
                'question_responses': [],
                'ai_task_responses': []
            }

    def generate_unified_assessment_report(self, child_id: int, format_type: str = "text") -> Dict:
        """
        Generate a comprehensive unified assessment report combining question responses and AI tasks.
        
        Args:
            child_id: ID of the child to analyze
            format_type: "text" for readable format, "json" for structured data
            
        Returns:
            Dict containing comprehensive report data
        """
        
        # Get unified data
        data = self.get_unified_assessment_data(child_id)
        question_responses = data['question_responses']
        ai_task_responses = data['ai_task_responses']
        
        # Get child info
        child_info = self.get_child_info(child_id)
        child_name = child_info.get('name', f'Child {child_id}')
        age_group = child_info.get('age_group', 'Unknown')
        
        # Initialize report structure
        report = {
            'child_name': child_name,
            'child_id': child_id,
            'age_group': age_group,
            'assessment_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'summary': {},
            'question_analysis': {},
            'ai_task_analysis': {},
            'unified_scoring': {},
            'recommendations': [],
            'detailed_breakdown': {},
            'formatted_report': ""
        }
        
        # Analyze question responses
        question_stats = self._analyze_question_responses(question_responses)
        report['question_analysis'] = question_stats
        
        # Analyze AI task responses
        ai_task_stats = self._analyze_ai_task_responses(ai_task_responses)
        report['ai_task_analysis'] = ai_task_stats
        
        # Calculate unified scoring
        unified_scoring = self._calculate_unified_scoring(question_stats, ai_task_stats)
        report['unified_scoring'] = unified_scoring
        
        # Generate summary
        report['summary'] = self._generate_summary(child_name, unified_scoring, question_stats, ai_task_stats)
        
        # Generate recommendations
        report['recommendations'] = self._generate_unified_recommendations(
            question_stats, ai_task_stats, unified_scoring
        )
        
        # Create detailed breakdown
        report['detailed_breakdown'] = self._create_detailed_breakdown(
            question_responses, ai_task_responses, question_stats, ai_task_stats
        )
        
        # Generate formatted report
        if format_type == "text":
            report['formatted_report'] = self._format_text_report(report)
        
        return report

    def _analyze_question_responses(self, responses: List[Dict]) -> Dict:
        """Analyze traditional question responses."""
        if not responses:
            return {
                'total_questions': 0,
                'correct_answers': 0,
                'incorrect_answers': 0,
                'accuracy_percentage': 0,
                'average_response_time': 0,
                'total_hints_used': 0,
                'by_assessment_type': {},
                'incorrect_details': []
            }
        
        total_questions = len(responses)
        correct_count = sum(1 for r in responses if r['is_correct'] == 'true')
        incorrect_count = total_questions - correct_count
        accuracy = round((correct_count / total_questions) * 100, 1) if total_questions > 0 else 0
        
        # Calculate average response time
        response_times = [r['response_time_seconds'] for r in responses if r['response_time_seconds']]
        avg_response_time = round(sum(response_times) / len(response_times), 1) if response_times else 0
        
        # Total hints used
        total_hints = sum(r['hints_used'] or 0 for r in responses)
        
        # Group by assessment type
        by_type = defaultdict(lambda: {'correct': 0, 'total': 0, 'questions': []})
        incorrect_details = []
        
        for response in responses:
            assessment_type = response['assessment_type']
            is_correct = response['is_correct'] == 'true'
            
            by_type[assessment_type]['total'] += 1
            by_type[assessment_type]['questions'].append(response)
            
            if is_correct:
                by_type[assessment_type]['correct'] += 1
            else:
                incorrect_details.append({
                    'question': response['question_text'],
                    'child_answer': response['child_answer'],
                    'correct_answer': response['correct_answer'],
                    'assessment_type': assessment_type,
                    'response_time': response['response_time_seconds']
                })
        
        # Calculate accuracy by type
        for type_name, type_data in by_type.items():
            type_data['accuracy'] = round((type_data['correct'] / type_data['total']) * 100, 1)
        
        return {
            'total_questions': total_questions,
            'correct_answers': correct_count,
            'incorrect_answers': incorrect_count,
            'accuracy_percentage': accuracy,
            'average_response_time': avg_response_time,
            'total_hints_used': total_hints,
            'by_assessment_type': dict(by_type),
            'incorrect_details': incorrect_details
        }

    def _analyze_ai_task_responses(self, responses: List[Dict]) -> Dict:
        """Analyze AI task responses (physical and linguistic)."""
        if not responses:
            return {
                'total_tasks': 0,
                'completed_tasks': 0,
                'skipped_tasks': 0,
                'total_success_count': 0,
                'total_attempts': 0,
                'overall_success_rate': 0,
                'average_completion_time': 0,
                'by_task_type': {},
                'failed_tasks': [],
                'ai_feedback_summary': []
            }
        
        total_tasks = len(responses)
        completed_count = sum(1 for r in responses if r['was_completed'] == 'true')
        skipped_count = sum(1 for r in responses if r['was_skipped'] == 'true')
        
        # Calculate total success metrics
        total_success = sum(int(r['success_count'] or 0) for r in responses)
        total_attempts = sum(int(r['total_attempts'] or 0) for r in responses)
        overall_success_rate = round((total_success / total_attempts) * 100, 1) if total_attempts > 0 else 0
        
        # Calculate average completion time
        completion_times = [r['completion_time_seconds'] for r in responses if r['completion_time_seconds']]
        avg_completion_time = round(sum(completion_times) / len(completion_times), 1) if completion_times else 0
        
        # Group by task type
        by_type = defaultdict(lambda: {
            'tasks': [], 'completed': 0, 'success_count': 0, 'attempts': 0, 'success_rate': 0
        })
        failed_tasks = []
        ai_feedback = []
        
        for response in responses:
            task_type = response['task_type']
            success_count = int(response['success_count'] or 0)
            attempts = int(response['total_attempts'] or 0)
            was_completed = response['was_completed'] == 'true'
            
            by_type[task_type]['tasks'].append(response)
            by_type[task_type]['success_count'] += success_count
            by_type[task_type]['attempts'] += attempts
            
            if was_completed:
                by_type[task_type]['completed'] += 1
            
            # Track failed or low-performance tasks
            if not was_completed or (attempts > 0 and (success_count / attempts) < 0.3):
                failed_tasks.append({
                    'task_name': response['task_name'],
                    'task_type': task_type,
                    'success_count': success_count,
                    'total_attempts': attempts,
                    'was_completed': was_completed,
                    'was_skipped': response['was_skipped'] == 'true',
                    'feedback': response['ai_feedback']
                })
            
            # Collect AI feedback
            if response['ai_feedback']:
                ai_feedback.append({
                    'task_type': task_type,
                    'task_name': response['task_name'],
                    'feedback': response['ai_feedback']
                })
        
        # Calculate success rates by type
        for type_name, type_data in by_type.items():
            if type_data['attempts'] > 0:
                type_data['success_rate'] = round((type_data['success_count'] / type_data['attempts']) * 100, 1)
        
        return {
            'total_tasks': total_tasks,
            'completed_tasks': completed_count,
            'skipped_tasks': skipped_count,
            'total_success_count': total_success,
            'total_attempts': total_attempts,
            'overall_success_rate': overall_success_rate,
            'average_completion_time': avg_completion_time,
            'by_task_type': dict(by_type),
            'failed_tasks': failed_tasks,
            'ai_feedback_summary': ai_feedback
        }

    def _calculate_unified_scoring(self, question_stats: Dict, ai_task_stats: Dict) -> Dict:
        """Calculate unified scoring across both question responses and AI tasks."""
        
        # Question-based scoring (traditional)
        question_score = question_stats['correct_answers']
        question_max = question_stats['total_questions']
        
        # AI task-based scoring (completion and success)
        ai_completion_score = ai_task_stats['completed_tasks']
        ai_max_tasks = ai_task_stats['total_tasks']
        
        # Success rate scoring (bonus points for high success rates)
        ai_success_bonus = 0
        if ai_task_stats['total_attempts'] > 0:
            # Award bonus points based on success rate
            success_rate = ai_task_stats['overall_success_rate']
            if success_rate >= 80:
                ai_success_bonus = 2
            elif success_rate >= 60:
                ai_success_bonus = 1.5
            elif success_rate >= 40:
                ai_success_bonus = 1
            elif success_rate >= 20:
                ai_success_bonus = 0.5
        
        # Calculate total score
        total_score = question_score + ai_completion_score + ai_success_bonus
        total_possible = question_max + ai_max_tasks + 2  # Max 2 bonus points
        
        # Overall accuracy
        if total_possible > 0:
            overall_accuracy = round((total_score / total_possible) * 100, 1)
        else:
            overall_accuracy = 0
        
        # Performance level
        if overall_accuracy >= 90:
            performance_level = "Exceptional"
        elif overall_accuracy >= 80:
            performance_level = "Excellent"
        elif overall_accuracy >= 70:
            performance_level = "Good"
        elif overall_accuracy >= 60:
            performance_level = "Satisfactory"
        elif overall_accuracy >= 50:
            performance_level = "Developing"
        else:
            performance_level = "Needs Support"
        
        return {
            'question_score': question_score,
            'question_max': question_max,
            'ai_completion_score': ai_completion_score,
            'ai_max_tasks': ai_max_tasks,
            'ai_success_bonus': ai_success_bonus,
            'total_score': total_score,
            'total_possible': total_possible,
            'overall_accuracy': overall_accuracy,
            'performance_level': performance_level
        }

    def _generate_summary(self, child_name: str, unified_scoring: Dict, 
                         question_stats: Dict, ai_task_stats: Dict) -> Dict:
        """Generate a comprehensive summary of the assessment."""
        
        total_tasks_attempted = question_stats['total_questions'] + ai_task_stats['total_tasks']
        total_successful = question_stats['correct_answers'] + ai_task_stats['completed_tasks']
        
        summary_text = f"{child_name} attempted {total_tasks_attempted} assessment tasks and completed {total_successful} successfully. "
        
        if question_stats['total_questions'] > 0:
            summary_text += f"In traditional questions, achieved {question_stats['accuracy_percentage']}% accuracy ({question_stats['correct_answers']}/{question_stats['total_questions']}). "
        
        if ai_task_stats['total_tasks'] > 0:
            summary_text += f"In AI-based tasks, completed {ai_task_stats['completed_tasks']}/{ai_task_stats['total_tasks']} tasks with {ai_task_stats['overall_success_rate']}% success rate. "
        
        summary_text += f"Overall performance level: {unified_scoring['performance_level']} ({unified_scoring['overall_accuracy']}%)."
        
        return {
            'text': summary_text,
            'total_tasks_attempted': total_tasks_attempted,
            'total_successful': total_successful,
            'overall_success_rate': unified_scoring['overall_accuracy']
        }

    def _generate_unified_recommendations(self, question_stats: Dict, 
                                        ai_task_stats: Dict, unified_scoring: Dict) -> List[str]:
        """Generate personalized recommendations based on performance analysis."""
        recommendations = []
        
        # Question-based recommendations
        if question_stats['total_questions'] > 0:
            if question_stats['accuracy_percentage'] < 60:
                recommendations.append("Focus on strengthening foundational knowledge through targeted practice in areas with incorrect responses.")
            
            # Type-specific recommendations
            for assessment_type, type_data in question_stats['by_assessment_type'].items():
                if type_data['accuracy'] < 70:
                    if assessment_type == 'intelligence':
                        recommendations.append("Practice cognitive exercises, puzzles, and problem-solving activities to improve intellectual development.")
                    elif assessment_type == 'physical':
                        recommendations.append("Engage in more physical activities and motor skill exercises.")
                    elif assessment_type == 'linguistic':
                        recommendations.append("Focus on language development through reading, storytelling, and vocabulary building.")
        
        # AI task-based recommendations
        if ai_task_stats['total_tasks'] > 0:
            if ai_task_stats['overall_success_rate'] < 50:
                recommendations.append("Consider breaking down complex tasks into smaller, manageable steps to build confidence.")
            
            # Type-specific AI task recommendations
            for task_type, type_data in ai_task_stats['by_task_type'].items():
                if type_data['success_rate'] < 60:
                    if task_type == 'physical':
                        recommendations.append("Practice physical coordination through games, sports, and movement activities.")
                    elif task_type == 'linguistic':
                        recommendations.append("Enhance speech and language skills through interactive conversation and pronunciation exercises.")
        
        # Failed task specific recommendations
        for failed_task in ai_task_stats['failed_tasks']:
            if failed_task['was_skipped']:
                recommendations.append(f"Encourage completion of {failed_task['task_type']} tasks - provide additional support and motivation.")
            elif failed_task['total_attempts'] > 0 and failed_task['success_count'] == 0:
                recommendations.append(f"The {failed_task['task_name']} requires additional practice - consider one-on-one guidance.")
        
        # Overall performance recommendations
        if unified_scoring['overall_accuracy'] >= 90:
            recommendations.append("Excellent performance! Consider introducing more challenging activities to continue growth.")
        elif unified_scoring['overall_accuracy'] >= 70:
            recommendations.append("Good progress! Continue current activities and gradually increase difficulty.")
        elif unified_scoring['overall_accuracy'] < 50:
            recommendations.append("Focus on building foundational skills through consistent, supportive practice sessions.")
        
        # Time-based recommendations
        if question_stats['average_response_time'] > 60:  # More than 1 minute average
            recommendations.append("Work on improving response time through timed practice sessions.")
        
        return recommendations[:6]  # Limit to top 6 recommendations

    def _create_detailed_breakdown(self, question_responses: List[Dict], 
                                 ai_task_responses: List[Dict], 
                                 question_stats: Dict, ai_task_stats: Dict) -> Dict:
        """Create detailed breakdown of all responses."""
        
        breakdown = {
            'question_details': [],
            'ai_task_details': [],
            'performance_patterns': {},
            'time_analysis': {}
        }
        
        # Question details
        for response in question_responses:
            breakdown['question_details'].append({
                'question': response['question_text'],
                'child_answer': response['child_answer'],
                'correct_answer': response['correct_answer'],
                'is_correct': response['is_correct'] == 'true',
                'assessment_type': response['assessment_type'],
                'response_time': response['response_time_seconds'],
                'hints_used': response['hints_used'] or 0
            })
        
        # AI task details
        for response in ai_task_responses:
            breakdown['ai_task_details'].append({
                'task_name': response['task_name'],
                'task_type': response['task_type'],
                'success_count': response['success_count'],
                'total_attempts': response['total_attempts'],
                'success_rate': round((int(response['success_count'] or 0) / int(response['total_attempts'] or 1)) * 100, 1) if response['total_attempts'] else 0,
                'completion_time': response['completion_time_seconds'],
                'was_completed': response['was_completed'] == 'true',
                'was_skipped': response['was_skipped'] == 'true',
                'ai_feedback': response['ai_feedback']
            })
        
        return breakdown

    def _format_text_report(self, report: Dict) -> str:
        """Format the comprehensive report as readable text."""
        
        text_report = f"""
═══════════════════════════════════════════════════════════════════
                    UNIFIED ASSESSMENT REPORT
═══════════════════════════════════════════════════════════════════

CHILD INFORMATION:
Name: {report['child_name']}
Age Group: {report['age_group']}
Assessment Date: {report['assessment_date']}

EXECUTIVE SUMMARY:
{report['summary']['text']}

UNIFIED SCORING:
Overall Performance: {report['unified_scoring']['performance_level']} ({report['unified_scoring']['overall_accuracy']}%)
Total Score: {report['unified_scoring']['total_score']:.1f}/{report['unified_scoring']['total_possible']:.1f}

Breakdown:
• Question Responses: {report['unified_scoring']['question_score']}/{report['unified_scoring']['question_max']} correct
• AI Task Completions: {report['unified_scoring']['ai_completion_score']}/{report['unified_scoring']['ai_max_tasks']} completed
• Success Rate Bonus: {report['unified_scoring']['ai_success_bonus']:.1f}/2.0 points

QUESTION ANALYSIS:
"""
        
        if report['question_analysis']['total_questions'] > 0:
            text_report += f"""• Total Questions: {report['question_analysis']['total_questions']}
• Correct Answers: {report['question_analysis']['correct_answers']}
• Accuracy: {report['question_analysis']['accuracy_percentage']}%
• Average Response Time: {report['question_analysis']['average_response_time']} seconds
• Hints Used: {report['question_analysis']['total_hints_used']}

By Assessment Type:
"""
            for assessment_type, stats in report['question_analysis']['by_assessment_type'].items():
                text_report += f"  - {assessment_type.title()}: {stats['correct']}/{stats['total']} ({stats['accuracy']}%)\n"
            
            if report['question_analysis']['incorrect_details']:
                text_report += "\nIncorrect Responses:\n"
                for incorrect in report['question_analysis']['incorrect_details'][:3]:  # Show top 3
                    text_report += f"  • Q: {incorrect['question'][:60]}...\n"
                    text_report += f"    Child's Answer: {incorrect['child_answer']}\n"
                    text_report += f"    Correct Answer: {incorrect['correct_answer']}\n\n"
        else:
            text_report += "No traditional questions completed.\n"
        
        text_report += "\nAI TASK ANALYSIS:\n"
        
        if report['ai_task_analysis']['total_tasks'] > 0:
            text_report += f"""• Total AI Tasks: {report['ai_task_analysis']['total_tasks']}
• Completed Tasks: {report['ai_task_analysis']['completed_tasks']}
• Skipped Tasks: {report['ai_task_analysis']['skipped_tasks']}
• Overall Success Rate: {report['ai_task_analysis']['overall_success_rate']}%
• Success Count: {report['ai_task_analysis']['total_success_count']}/{report['ai_task_analysis']['total_attempts']} attempts
• Average Completion Time: {report['ai_task_analysis']['average_completion_time']} seconds

By Task Type:
"""
            for task_type, stats in report['ai_task_analysis']['by_task_type'].items():
                text_report += f"  - {task_type.title()}: {stats['completed']} completed, {stats['success_rate']}% success rate\n"
            
            if report['ai_task_analysis']['failed_tasks']:
                text_report += "\nChallenging Tasks:\n"
                for failed in report['ai_task_analysis']['failed_tasks']:
                    status = "Skipped" if failed['was_skipped'] else f"{failed['success_count']}/{failed['total_attempts']} attempts"
                    text_report += f"  • {failed['task_name']}: {status}\n"
            
            if report['ai_task_analysis']['ai_feedback_summary']:
                text_report += "\nAI Feedback:\n"
                for feedback in report['ai_task_analysis']['ai_feedback_summary'][:2]:  # Show top 2
                    text_report += f"  • {feedback['task_type'].title()}: {feedback['feedback']}\n"
        else:
            text_report += "No AI tasks completed.\n"
        
        text_report += "\nPERSONALIZED RECOMMENDATIONS:\n"
        for i, rec in enumerate(report['recommendations'], 1):
            text_report += f"{i}. {rec}\n"
        
        text_report += f"""
═══════════════════════════════════════════════════════════════════
Report generated on {report['assessment_date']}
═══════════════════════════════════════════════════════════════════
"""
        
        return text_report

    def get_child_responses(self, child_id: int) -> List[Dict]:
        """Fetch all question responses for a specific child."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
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
                ai_confidence_score,
                created_at
            FROM question_responses 
            WHERE child_id = ?
            ORDER BY created_at DESC
            """
            
            cursor.execute(query, (child_id,))
            responses = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return responses
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []

    def categorize_question(self, question_id: str, question_text: str) -> str:
        """Categorize a question based on its ID and content."""
        question_lower = question_text.lower()
        
        # Intelligence categories
        if any(word in question_lower for word in ['count', 'number', 'math', 'calculate']):
            return 'scientific'
        elif any(word in question_lower for word in ['sequence', 'order', 'pattern', 'logic']):
            return 'logical'
        elif any(word in question_lower for word in ['draw', 'color', 'create', 'art', 'picture']):
            return 'artistic'
        elif any(word in question_lower for word in ['feel', 'emotion', 'friend', 'share', 'help']):
            return 'socio_emotional'
        
        # Physical categories
        elif any(word in question_lower for word in ['jump', 'run', 'move', 'walk', 'balance']):
            return 'motor_skills'
        elif any(word in question_lower for word in ['catch', 'throw', 'hold', 'grip']):
            return 'coordination'
        elif any(word in question_lower for word in ['stand', 'sit', 'balance']):
            return 'balance'
        elif any(word in question_lower for word in ['lift', 'carry', 'push', 'pull']):
            return 'strength'
        
        # Linguistic categories
        elif any(word in question_lower for word in ['word', 'name', 'vocabulary', 'meaning']):
            return 'vocabulary'
        elif any(word in question_lower for word in ['story', 'read', 'understand', 'comprehend']):
            return 'comprehension'
        elif any(word in question_lower for word in ['say', 'speak', 'tell', 'express']):
            return 'expression'
        elif any(word in question_lower for word in ['sound', 'rhyme', 'letter', 'phonics']):
            return 'phonics'
        
        return 'general'

    def analyze_child_performance(self, child_id: int) -> Dict:
        """Analyze comprehensive performance data for a child."""
        responses = self.get_child_responses(child_id)
        
        if not responses:
            return {
                'summary': "No assessment data found for this child.",
                'recommendations': "Please complete some assessments first.",
                'detailed_analysis': {}
            }
        
        # Group responses by assessment type
        type_analysis = defaultdict(lambda: {
            'total_questions': 0,
            'correct_answers': 0,
            'incorrect_answers': 0,
            'accuracy_percentage': 0,
            'strengths': [],
            'areas_for_improvement': [],
            'average_response_time': 0,
            'total_hints_used': 0,
            'total_attempts': 0,
            'questions_by_category': defaultdict(list)
        })
        
        # Process each response
        for response in responses:
            assessment_type = response['assessment_type']
            is_correct = response['is_correct'] == 'true'
            
            # Basic statistics
            type_analysis[assessment_type]['total_questions'] += 1
            if is_correct:
                type_analysis[assessment_type]['correct_answers'] += 1
            else:
                type_analysis[assessment_type]['incorrect_answers'] += 1
            
            # Time and attempts tracking
            if response['response_time_seconds']:
                type_analysis[assessment_type]['average_response_time'] += response['response_time_seconds']
            
            type_analysis[assessment_type]['total_hints_used'] += response['hints_used'] or 0
            type_analysis[assessment_type]['total_attempts'] += response['attempts'] or 1
            
            # Categorize question for detailed analysis
            category = self.categorize_question(response['question_id'], response['question_text'])
            type_analysis[assessment_type]['questions_by_category'][category].append({
                'question': response['question_text'],
                'correct': is_correct,
                'child_answer': response['child_answer'],
                'correct_answer': response['correct_answer'],
                'difficulty': response['difficulty_level'] or 1
            })
        
        # Calculate percentages and identify strengths/weaknesses
        for assessment_type, data in type_analysis.items():
            if data['total_questions'] > 0:
                data['accuracy_percentage'] = round(
                    (data['correct_answers'] / data['total_questions']) * 100, 1
                )
                data['average_response_time'] = round(
                    data['average_response_time'] / data['total_questions'], 1
                )
                
                # Identify strengths and areas for improvement
                for category, questions in data['questions_by_category'].items():
                    correct_in_category = sum(1 for q in questions if q['correct'])
                    total_in_category = len(questions)
                    category_accuracy = (correct_in_category / total_in_category) * 100
                    
                    category_name = self.assessment_categories.get(assessment_type, {}).get('areas', {}).get(category, category.title())
                    
                    if category_accuracy >= 75:
                        data['strengths'].append(f"{category_name} ({category_accuracy:.0f}% accuracy)")
                    elif category_accuracy < 50:
                        data['areas_for_improvement'].append(f"{category_name} ({category_accuracy:.0f}% accuracy)")
        
        # Generate comprehensive analysis
        return self.generate_analysis_summary(dict(type_analysis), child_id)

    def generate_analysis_summary(self, type_analysis: Dict, child_id: int) -> Dict:
        """Generate a comprehensive, readable analysis summary."""
        
        # Get child info
        child_info = self.get_child_info(child_id)
        child_name = child_info.get('name', f'Child {child_id}')
        age_group = child_info.get('age_group', 'Unknown')
        
        # Overall performance summary
        total_questions = sum(data['total_questions'] for data in type_analysis.values())
        total_correct = sum(data['correct_answers'] for data in type_analysis.values())
        overall_accuracy = round((total_correct / total_questions) * 100, 1) if total_questions > 0 else 0
        
        # Performance level categorization
        if overall_accuracy >= 80:
            performance_level = "excellent"
        elif overall_accuracy >= 65:
            performance_level = "good"
        elif overall_accuracy >= 50:
            performance_level = "satisfactory"
        else:
            performance_level = "needs improvement"
        
        # Generate summary paragraphs
        summary_paragraphs = []
        
        # Overall performance paragraph
        summary_paragraphs.append(
            f"{child_name} (Age Group: {age_group}) has completed {total_questions} assessment questions "
            f"with an overall accuracy of {overall_accuracy}%. This represents {performance_level} performance "
            f"across all developmental areas assessed."
        )
        
        # Assessment-specific analysis
        assessment_insights = []
        recommendations = []
        
        for assessment_type, data in type_analysis.items():
            type_name = self.assessment_categories.get(assessment_type, {}).get('name', assessment_type.title())
            accuracy = data['accuracy_percentage']
            
            # Performance description
            if accuracy >= 80:
                performance_desc = "shows excellent mastery"
            elif accuracy >= 65:
                performance_desc = "demonstrates good understanding"
            elif accuracy >= 50:
                performance_desc = "shows developing skills"
            else:
                performance_desc = "needs focused support"
            
            # Assessment-specific insights
            insights = f"In {type_name}, {child_name} {performance_desc} with {accuracy}% accuracy across {data['total_questions']} questions."
            
            # Add timing information if available
            if data['average_response_time'] > 0:
                insights += f" The average response time was {data['average_response_time']} seconds."
            
            # Add attempts and hints information
            if data['total_hints_used'] > 0:
                insights += f" {data['total_hints_used']} hints were used across all questions."
            
            assessment_insights.append(insights)
            
            # Strengths
            if data['strengths']:
                strengths_text = f"Key strengths in {type_name} include: " + ", ".join(data['strengths']) + "."
                assessment_insights.append(strengths_text)
            
            # Areas for improvement and recommendations
            if data['areas_for_improvement']:
                improvement_text = f"Areas needing attention in {type_name}: " + ", ".join(data['areas_for_improvement']) + "."
                assessment_insights.append(improvement_text)
                
                # Generate specific recommendations
                if assessment_type == 'intelligence':
                    if any('scientific' in area.lower() for area in data['areas_for_improvement']):
                        recommendations.append("Practice counting, number recognition, and simple math concepts through daily activities and educational games.")
                    if any('artistic' in area.lower() for area in data['areas_for_improvement']):
                        recommendations.append("Encourage drawing, coloring, and creative activities to develop artistic expression and fine motor skills.")
                    if any('logical' in area.lower() for area in data['areas_for_improvement']):
                        recommendations.append("Use puzzles, pattern games, and sequence activities to strengthen logical thinking skills.")
                    if any('social' in area.lower() or 'emotional' in area.lower() for area in data['areas_for_improvement']):
                        recommendations.append("Focus on emotional vocabulary, social interaction activities, and discussing feelings during daily situations.")
                
                elif assessment_type == 'physical':
                    recommendations.append("Incorporate more physical activities, playground time, and movement-based games to improve physical development.")
                    recommendations.append("Practice activities that involve balance, coordination, and motor skill development.")
                
                elif assessment_type == 'linguistic':
                    recommendations.append("Read together daily, engage in storytelling, and encourage verbal expression through conversations.")
                    recommendations.append("Use vocabulary games, rhyming activities, and phonics practice to strengthen language skills.")
        
        # Combine all insights
        full_summary = " ".join(summary_paragraphs + assessment_insights)
        
        # Generate final recommendations paragraph
        if recommendations:
            recommendation_text = f"To support {child_name}'s continued development, consider the following: " + " ".join(recommendations)
        else:
            recommendation_text = f"{child_name} is performing well across all areas. Continue with regular practice and introduce slightly more challenging activities to maintain growth."
        
        return {
            'child_name': child_name,
            'age_group': age_group,
            'overall_accuracy': overall_accuracy,
            'performance_level': performance_level,
            'total_questions_completed': total_questions,
            'summary': full_summary,
            'recommendations': recommendation_text,
            'detailed_analysis': type_analysis,
            'analysis_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def get_child_info(self, child_id: int) -> Dict:
        """Get basic child information."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = """
            SELECT child_name as name, age_group
            FROM children 
            WHERE id = ?
            """
            
            cursor.execute(query, (child_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return dict(result)
            return {'name': f'Child {child_id}', 'age_group': 'Unknown'}
            
        except sqlite3.Error:
            return {'name': f'Child {child_id}', 'age_group': 'Unknown'}

    def generate_formatted_report(self, child_id: int) -> str:
        """Generate a formatted text report for the child."""
        analysis = self.analyze_child_performance(child_id)
        
        report = f"""
CHILD ASSESSMENT ANALYSIS REPORT
Generated on: {analysis['analysis_date']}
=====================================

CHILD INFORMATION:
Name: {analysis['child_name']}
Age Group: {analysis['age_group']}
Overall Performance: {analysis['performance_level'].title()} ({analysis['overall_accuracy']}% accuracy)
Total Questions Completed: {analysis['total_questions_completed']}

PERFORMANCE SUMMARY:
{analysis['summary']}

RECOMMENDATIONS:
{analysis['recommendations']}

DETAILED BREAKDOWN:
"""
        
        for assessment_type, data in analysis['detailed_analysis'].items():
            type_name = self.assessment_categories.get(assessment_type, {}).get('name', assessment_type.title())
            report += f"""
{type_name}:
- Questions Completed: {data['total_questions']}
- Accuracy: {data['accuracy_percentage']}%
- Correct Answers: {data['correct_answers']}
- Incorrect Answers: {data['incorrect_answers']}
- Average Response Time: {data['average_response_time']} seconds
- Hints Used: {data['total_hints_used']}
- Total Attempts: {data['total_attempts']}
"""
            
            if data['strengths']:
                report += f"- Strengths: {', '.join(data['strengths'])}\n"
            if data['areas_for_improvement']:
                report += f"- Areas for Improvement: {', '.join(data['areas_for_improvement'])}\n"
        
        return report


# Example usage functions
def analyze_child(child_id: int, db_path: str = "assessment.db") -> Dict:
    """Quick function to analyze a child's performance."""
    analyzer = ChildAssessmentAnalyzer(db_path)
    return analyzer.analyze_child_performance(child_id)


def generate_child_report(child_id: int, db_path: str = "assessment.db") -> str:
    """Quick function to generate a formatted report."""
    analyzer = ChildAssessmentAnalyzer(db_path)
    return analyzer.generate_formatted_report(child_id)


def generate_unified_report(child_id: int, db_path: str = "assessment.db", format_type: str = "text") -> Dict:
    """
    Generate a comprehensive unified assessment report combining question responses and AI tasks.
    
    Args:
        child_id: ID of the child to analyze
        db_path: Path to the SQLite database
        format_type: "text" for readable format, "json" for structured data
        
    Returns:
        Dict containing comprehensive report data with unified scoring
    """
    analyzer = ChildAssessmentAnalyzer(db_path)
    return analyzer.generate_unified_assessment_report(child_id, format_type)


def get_unified_summary(child_id: int, db_path: str = "assessment.db") -> str:
    """Get a quick unified summary for a child."""
    report = generate_unified_report(child_id, db_path, "json")
    return report.get('summary', {}).get('text', 'No assessment data available.')


def analyze_child_assessment_responses(child_id: int, db_path: str = "assessment.db") -> str:
    """
    Compatibility function for existing simple_child_analysis.py integration.
    Returns comprehensive readable analysis.
    """
    report = generate_unified_report(child_id, db_path, "text")
    return report.get('formatted_report', 'No assessment data available.')


if __name__ == "__main__":
    # Example usage with enhanced unified reporting
    print("Child Assessment Analyzer - Unified Reporting")
    print("=" * 50)
    
    # Test with a child ID (you can change this)
    test_child_id = 5  # Replace with actual child ID from your database
    
    try:
        # Generate unified report
        print(f"\n🔍 Generating Unified Report for Child {test_child_id}...")
        unified_report = generate_unified_report(test_child_id, "assessment.db", "text")
        
        print(f"\n📊 Quick Summary:")
        print("-" * 30)
        print(unified_report['summary']['text'])
        
        print(f"\n📈 Unified Scoring:")
        print(f"Total Score: {unified_report['unified_scoring']['total_score']:.1f}/{unified_report['unified_scoring']['total_possible']:.1f}")
        print(f"Performance Level: {unified_report['unified_scoring']['performance_level']}")
        print(f"Overall Accuracy: {unified_report['unified_scoring']['overall_accuracy']}%")
        
        print(f"\n💡 Top Recommendations:")
        for i, rec in enumerate(unified_report['recommendations'][:3], 1):
            print(f"{i}. {rec}")
        
        # Show full formatted report
        print(f"\n📋 FULL UNIFIED REPORT:")
        print("=" * 50)
        print(unified_report['formatted_report'])
        
        # Test JSON format
        print(f"\n🔧 Testing JSON Format...")
        json_report = generate_unified_report(test_child_id, "assessment.db", "json")
        print(f"JSON Report Keys: {list(json_report.keys())}")
        print(f"Question Analysis Keys: {list(json_report['question_analysis'].keys())}")
        print(f"AI Task Analysis Keys: {list(json_report['ai_task_analysis'].keys())}")
        
    except Exception as e:
        print(f"❌ Error analyzing child data: {e}")
        print("Please ensure the database exists and contains assessment data.")
        
        # Show sample usage
        print(f"\n📖 Sample Usage:")
        print("# Generate text report")
        print("report = generate_unified_report(child_id=5)")
        print("print(report['formatted_report'])")
        print("")
        print("# Generate JSON data for API")
        print("data = generate_unified_report(child_id=5, format_type='json')")
        print("return jsonify(data)")
        print("")
        print("# Quick summary")
        print("summary = get_unified_summary(child_id=5)")
        print("print(summary)")
