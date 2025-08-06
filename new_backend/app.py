from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import hashlib
import jwt
from datetime import datetime, timedelta
from functools import wraps
from timezone_utils import convert_utc_to_ist

# Import AI assessment routes
try:
    from ai_assessment_routes_improved import assessment_ai_bp
    AI_ROUTES_AVAILABLE = True
except ImportError as e:
    print(f"WARNING: AI assessment routes not available: {e}")
    AI_ROUTES_AVAILABLE = False

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Database setup
def init_db():
    conn = sqlite3.connect('assessment.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            parent_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create children table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS children (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            child_name TEXT NOT NULL,
            sex TEXT NOT NULL,
            birth_date DATE NOT NULL,
            age_group TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create assessment_results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assessment_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            child_id INTEGER,
            age_group TEXT NOT NULL,
            intelligence_score INTEGER DEFAULT 0,
            physical_score INTEGER DEFAULT 0,
            linguistic_score INTEGER DEFAULT 0,
            total_score INTEGER DEFAULT 0,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (child_id) REFERENCES children (id)
        )
    ''')
    
    # Check if we need to migrate existing assessment_results table
    try:
        cursor.execute("PRAGMA table_info(assessment_results)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # If child_id column doesn't exist, add it
        if 'child_id' not in columns:
            print("🔄 Migrating database: Adding child_id column to assessment_results...")
            cursor.execute("ALTER TABLE assessment_results ADD COLUMN child_id INTEGER")
            cursor.execute("ALTER TABLE assessment_results ADD FOREIGN KEY (child_id) REFERENCES children (id)")
            print("✅ Database migration completed")
            
        # If parent_name column doesn't exist in users table, rename full_name
        cursor.execute("PRAGMA table_info(users)")
        user_columns = [column[1] for column in cursor.fetchall()]
        if 'full_name' in user_columns and 'parent_name' not in user_columns:
            print("🔄 Migrating database: Renaming full_name to parent_name in users table...")
            # SQLite doesn't support column rename, so we need to recreate the table
            cursor.execute('''
                CREATE TABLE users_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    parent_name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute("INSERT INTO users_new (id, email, password, parent_name, created_at) SELECT id, email, password, full_name, created_at FROM users")
            cursor.execute("DROP TABLE users")
            cursor.execute("ALTER TABLE users_new RENAME TO users")
            print("✅ Users table migration completed")
            
    except Exception as e:
        print(f"⚠️  Migration warning: {e}")
    
    # Create demo user for testing if it doesn't exist
    try:
        cursor.execute('SELECT id FROM users WHERE id = 1')
        if not cursor.fetchone():
            demo_password = hashlib.sha256('demo123'.encode()).hexdigest()
            cursor.execute(
                'INSERT INTO users (id, email, password, parent_name) VALUES (?, ?, ?, ?)',
                (1, 'demo@test.com', demo_password, 'Demo Parent')
            )
            print("✅ Created demo user for testing")
            
            # Create demo child
            cursor.execute('''
                INSERT INTO children (id, user_id, child_name, sex, birth_date, age_group) 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (1, 1, 'Demo Child', 'unspecified', '2022-01-01', '2-3'))
            print("✅ Created demo child for testing")
            
    except Exception as e:
        print(f"⚠️  Demo data creation warning: {e}")
    
    conn.commit()
    conn.close()

# Authentication decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            token = token.split(' ')[1]  # Remove 'Bearer ' prefix
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except:
            return jsonify({'message': 'Token is invalid'}), 401
        return f(*args, **kwargs)
    return decorated

def calculate_ai_success_rate(ai_task_data):
    """Calculate AI task success rate with proper error handling"""
    if not ai_task_data:
        return 0.0
    
    total_success = 0
    total_attempts = 0
    
    for task in ai_task_data:
        # Use the new field names
        success_count = task.get('display_success', 0)
        attempt_count = task.get('display_attempts', 0)
        
        # Convert to numbers if they're strings
        try:
            success_count = int(success_count) if success_count else 0
            attempt_count = int(attempt_count) if attempt_count else 0
        except (ValueError, TypeError):
            success_count = 0
            attempt_count = 0
        
        total_success += success_count
        total_attempts += attempt_count
    
    # Calculate overall success rate
    if total_attempts > 0:
        return round((total_success / total_attempts) * 100, 1)
    else:
        return 0.0

def calculate_completion_time(start_time, end_time):
    """Calculate completion time with proper timestamp handling"""
    if not start_time or not end_time:
        return 0
    
    try:
        if isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        if isinstance(end_time, str):
            end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        
        delta = end_time - start_time
        return max(0, delta.total_seconds())
    except (ValueError, TypeError):
        return 0

# Real Streamlit Intelligence Questions
INTELLIGENCE_QUESTIONS = {
    "0-1": {
        "scientific": {
            "prompt": "When your baby gets a new object, what do they usually do?",
            "options": [
                "Shakes or bangs it",
                "Puts it in the mouth", 
                "Looks at it with focus",
                "Ignores or drops it"
            ],
            "image": "baby-toys.png",
            "interaction": "tap",
        },
        "logical": {
            "prompt": "Does your baby react to repeated actions or sounds?",
            "options": [
                "Laughs or gets excited every time",
                "Sometimes responds",
                "Doesn't show interest"
            ],
            "image": "peekaboo-clapping.gif",
            "interaction": "tap",
        },
        "socio_emotional": {
            "prompt": "How does your baby respond to familiar and unfamiliar faces?",
            "options": [
                "Smiles or shows excitement with familiar person",
                "Neutral to all",
                "Cries when seeing unfamiliar person"
            ],
            "image": "faces-split.png",
            "interaction": "tap",
        },
        "artistic": {
            "prompt": "Which toy does your baby focus on for longer?",
            "options": [
                "Colorful patterned toy",
                "Black-and-white toy", 
                "Plain wooden toy"
            ],
            "image": "toys-contrast.png",
            "interaction": "tap",
        }
    },
    "1-2": {
        "scientific": {
            "prompt": "Does your child enjoy figuring out how things work or move?",
            "options": [
                "Very often",
                "Sometimes",
                "Rarely"
            ],
            "image": "explore-toys.gif",
            "interaction": "tap",
        },
        "logical": {
            "prompt": "Does your child try to group similar items together?",
            "options": [
                "Yes, often",
                "Occasionally", 
                "No"
            ],
            "image": "sorting-objects.png",
            "interaction": "tap",
        },
        "socio_emotional": {
            "prompt": "What does your child do when someone is upset?",
            "options": [
                "Tries to comfort",
                "Watches silently",
                "Walks away or ignores"
            ],
            "image": "crying-child.png",
            "interaction": "tap",
        },
        "artistic": {
            "prompt": "Which of these does your child enjoy using the most?",
            "options": [
                "Scribbling or drawing",
                "Dancing or playing with music",
                "Doesn't engage with any"
            ],
            "image": "art-tools.png",
            "interaction": "tap",
        }
    },
    "2-3": {
        "scientific": {
            "prompt": "Can your child build a tower with 3-4 blocks?",
            "options": [
                "Yes, easily",
                "With some help",
                "Not yet"
            ],
            "image": "blocks-tower.png",
            "interaction": "tap",
        },
        "logical": {
            "prompt": "Does your child understand 'big' and 'small'?",
            "options": [
                "Yes, clearly",
                "Sometimes",
                "Not yet"
            ],
            "image": "size-comparison.png",
            "interaction": "tap",
        },
        "socio_emotional": {
            "prompt": "How does your child play with other children?",
            "options": [
                "Shares and takes turns",
                "Plays alongside but parallel",
                "Prefers to play alone"
            ],
            "image": "children-playing.png",
            "interaction": "tap",
        },
        "artistic": {
            "prompt": "Can your child draw a circle or line?",
            "options": [
                "Yes, recognizable shapes",
                "Attempts but unclear",
                "Only scribbles"
            ],
            "image": "drawing-shapes.png",
            "interaction": "tap",
        }
    },
    "3-4": {
        "scientific": {
            "prompt": "Can your child count to 3?",
            "options": [
                "Yes, accurately",
                "Sometimes gets confused",
                "Not yet"
            ],
            "image": "counting-objects.png",
            "interaction": "tap",
        },
        "logical": {
            "prompt": "Does your child understand simple sequences?",
            "options": [
                "Yes, can follow 2-3 step instructions",
                "Sometimes with reminders",
                "Needs one step at a time"
            ],
            "image": "sequence-cards.png",
            "interaction": "tap",
        },
        "socio_emotional": {
            "prompt": "How does your child express emotions?",
            "options": [
                "Uses words to describe feelings",
                "Shows emotions through actions",
                "Has difficulty expressing emotions"
            ],
            "image": "emotion-faces.png",
            "interaction": "tap",
        },
        "artistic": {
            "prompt": "Can your child draw a person with head and limbs?",
            "options": [
                "Yes, recognizable figure",
                "Basic shapes for body",
                "Only scribbles"
            ],
            "image": "stick-figure.png",
            "interaction": "tap",
        }
    },
    "4-5": {
        "scientific": {
            "prompt": "Can your child count to 10?",
            "options": [
                "Yes, accurately",
                "Gets confused after 5",
                "Can count to 5"
            ],
            "image": "counting-ten.png",
            "interaction": "tap",
        },
        "logical": {
            "prompt": "Does your child understand cause and effect?",
            "options": [
                "Yes, explains simple relationships",
                "Sometimes notices connections",
                "Not yet apparent"
            ],
            "image": "cause-effect.png",
            "interaction": "tap",
        },
        "socio_emotional": {
            "prompt": "How does your child interact in group activities?",
            "options": [
                "Actively participates and cooperates",
                "Participates but needs encouragement",
                "Prefers individual activities"
            ],
            "image": "group-activity.png",
            "interaction": "tap",
        },
        "artistic": {
            "prompt": "Can your child draw recognizable objects?",
            "options": [
                "Yes, detailed drawings",
                "Basic but recognizable",
                "Still learning shapes"
            ],
            "image": "detailed-drawing.png",
            "interaction": "tap",
        }
    },
    "5-6": {
        "scientific": {
            "prompt": "Can your child count to 20?",
            "options": [
                "Yes, accurately",
                "Gets confused after 15",
                "Can count to 10"
            ],
            "image": "counting-twenty.png",
            "interaction": "tap",
        },
        "logical": {
            "prompt": "Does your child understand simple math concepts?",
            "options": [
                "Yes, basic addition/subtraction",
                "Understands more/less",
                "Still learning numbers"
            ],
            "image": "simple-math.png",
            "interaction": "tap",
        },
        "socio_emotional": {
            "prompt": "How does your child handle rules and structure?",
            "options": [
                "Understands and follows rules well",
                "Needs reminders about rules",
                "Struggles with structured activities"
            ],
            "image": "following-rules.png",
            "interaction": "tap",
        },
        "artistic": {
            "prompt": "Can your child write their name or letters?",
            "options": [
                "Yes, writes name clearly",
                "Attempts letters",
                "Still developing fine motor skills"
            ],
            "image": "writing-name.png",
            "interaction": "tap",
        }
    }
}

PHYSICAL_TASKS = {
    "0-1": {
        "task": "raise_hands",
        "title": "Can baby raise both hands high?",
        "description": "Show me you can do this movement!",
        "instruction": "Wrists above head level",
        "type": "pose_detection",
        "icon": "🖐️"
    },
    "1-2": {
        "task": "one_leg",
        "title": "Can you stand on one leg?", 
        "description": "Show me your balance!",
        "instruction": "Stand on one foot for 3 seconds",
        "type": "pose_detection",
        "icon": "🦵"
    },
    "2-3": {
        "task": "turn_around",
        "title": "Can you turn around in a circle?",
        "description": "Show me how you can spin!",
        "instruction": "Turn around 360 degrees",
        "type": "pose_detection",
        "icon": "🔄"
    },
    "3-4": {
        "task": "stand_still",
        "title": "Can you stand very still?",
        "description": "Show me how still you can be!",
        "instruction": "Stand without moving for 5 seconds",
        "type": "pose_detection",
        "icon": "🧘"
    },
    "4-5": {
        "task": "frog_jump",
        "title": "Can you do a frog jump?",
        "description": "Jump like a frog!",
        "instruction": "Squat down and jump forward",
        "type": "pose_detection",
        "icon": "🐸"
    },
    "5-6": {
        "task": "kangaroo_jump",
        "title": "Can you do kangaroo jumps?",
        "description": "Jump like a kangaroo!",
        "instruction": "Jump with both feet together",
        "type": "pose_detection",
        "icon": "🦘"
    }
}

LINGUISTIC_TASKS = {
    "0-1": {
        "task": "say_mama",
        "title": "Say 'ma‑ma'",
        "description": "Can you say mama?",
        "instruction": "Say the word clearly",
        "type": "speech_recognition",
        "icon": "👶",
        "target_words": ["ma", "mama", "mumma", "mummy"]
    },
    "1-2": {
        "task": "apple",
        "title": "Say 'apple'",
        "description": "Can you say apple?",
        "instruction": "Say the word clearly",
        "type": "speech_recognition", 
        "icon": "🍎",
        "target_words": ["apple", "aple", "apel"]
    },
    "2-3": {
        "task": "rhyme_cat",
        "title": "What rhymes with 'cat'?",
        "description": "Can you say a word that rhymes with cat?",
        "instruction": "Say a word that sounds like cat",
        "type": "speech_recognition",
        "icon": "🐱",
        "target_words": ["bat", "hat", "mat", "sat", "rat", "fat"]
    },
    "3-4": {
        "task": "fill_blank",
        "title": "Fill in the blank: 'The sun is ___'",
        "description": "Complete this sentence",
        "instruction": "Say what the sun is",
        "type": "speech_recognition",
        "icon": "☀️",
        "target_words": ["bright", "hot", "yellow", "big", "warm", "shining"]
    },
    "4-5": {
        "task": "sentence_sun",
        "title": "Make a sentence about the sun",
        "description": "Tell me about the sun",
        "instruction": "Say a complete sentence about the sun",
        "type": "speech_recognition",
        "icon": "🌞",
        "target_words": ["sun", "bright", "hot", "sky", "shines", "day"]
    },
    "5-6": {
        "task": "story_kite",
        "title": "Tell a short story about a kite",
        "description": "Tell me what happens with a kite",
        "instruction": "Tell a story about flying a kite",
        "type": "speech_recognition",
        "icon": "🪁",
        "target_words": ["kite", "fly", "wind", "sky", "string", "high"]
    }
}

# Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Backend is running'})

@app.route('/api/enhanced-status', methods=['GET'])
def enhanced_status():
    """Get status of enhanced assessment capabilities"""
    try:
        # Check if enhanced tasks are available
        if AI_ROUTES_AVAILABLE:
            from tasks import get_task_manager
            task_manager = get_task_manager()
            available_tasks = task_manager.get_all_available_tasks()
            
            return jsonify({
                'enhanced_available': True,
                'ai_routes_available': AI_ROUTES_AVAILABLE,
                'capabilities': {
                    'physical_assessment': 'Enhanced pose detection with timing and confidence',
                    'linguistic_assessment': 'Advanced speech recognition with phonetic analysis',
                    'progress_tracking': 'Detailed success rates and attempt history',
                    'fallback_system': 'Graceful degradation to basic assessment'
                },
                'available_tasks': available_tasks,
                'warnings': {
                    'ffmpeg': 'Audio processing may be limited without FFmpeg',
                    'vosk_model': 'Speech recognition requires Vosk model download'
                }
            })
        else:
            return jsonify({
                'enhanced_available': False,
                'ai_routes_available': AI_ROUTES_AVAILABLE,
                'message': 'Using basic assessment mode only',
                'capabilities': {
                    'physical_assessment': 'Basic pose detection',
                    'linguistic_assessment': 'Limited without AI routes',
                    'progress_tracking': 'Basic scoring only'
                }
            })
    except Exception as e:
        return jsonify({
            'enhanced_available': False,
            'error': str(e),
            'message': 'Enhanced assessment system initialization failed'
        })

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    print(f"📥 Registration data received: {data}")  # Debug logging
    
    email = data.get('email')
    password = data.get('password')
    parent_name = data.get('parentName') or data.get('fullName') or data.get('name')
    child_data = data.get('childData', {})
    
    print(f"📋 Parsed - Email: {email}, Parent: {parent_name}, ChildData: {child_data}")  # Debug logging
    
    if not email or not password or not parent_name:
        return jsonify({'message': 'Missing required parent fields'}), 400
    
    if not child_data.get('name') or not child_data.get('dateOfBirth') or not child_data.get('sex'):
        return jsonify({'message': 'Missing required child information'}), 400
    
    # Hash password
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    # Calculate age group from birth date
    try:
        birth_date = datetime.strptime(child_data['dateOfBirth'], '%Y-%m-%d').date()
        today = datetime.now()
        age_in_months = (today.year - birth_date.year) * 12 + (today.month - birth_date.month)
        
        if age_in_months <= 12:
            age_group = "0-1"
        elif age_in_months <= 24:
            age_group = "1-2"
        elif age_in_months <= 36:
            age_group = "2-3"
        elif age_in_months <= 48:
            age_group = "3-4"
        elif age_in_months <= 60:
            age_group = "4-5"
        else:
            age_group = "5-6"
            
    except ValueError:
        return jsonify({'message': 'Invalid birth date format. Use YYYY-MM-DD'}), 400
    
    try:
        conn = sqlite3.connect('assessment.db')
        cursor = conn.cursor()
        
        # Insert parent
        cursor.execute('INSERT INTO users (email, password, parent_name) VALUES (?, ?, ?)',
                      (email, hashed_password, parent_name))
        parent_id = cursor.lastrowid
        
        # Insert child
        cursor.execute('''INSERT INTO children (user_id, child_name, sex, birth_date, age_group) 
                         VALUES (?, ?, ?, ?, ?)''',
                      (parent_id, child_data['name'], child_data['sex'], child_data['dateOfBirth'], age_group))
        child_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        # Create token
        token = jwt.encode({
            'user_id': parent_id,
            'child_id': child_id,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, app.config['SECRET_KEY'])
        
        return jsonify({
            'message': 'Registration successful',
            'token': token,
            'user': {
                'id': parent_id,
                'name': parent_name,
                'email': email
            },
            'child': {
                'id': child_id,
                'name': child_data['name'],
                'sex': child_data['sex'],
                'birthDate': child_data['dateOfBirth'],
                'ageGroup': age_group
            }
        }), 201
    except sqlite3.IntegrityError:
        return jsonify({'message': 'Email already exists'}), 400
    except Exception as e:
        return jsonify({'message': f'Registration failed: {str(e)}'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'message': 'Missing email or password'}), 400
    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    conn = sqlite3.connect('assessment.db')
    cursor = conn.cursor()
    
    # Get user information
    cursor.execute('SELECT id, parent_name FROM users WHERE email = ? AND password = ?',
                  (email, hashed_password))
    user = cursor.fetchone()
    
    if user:
        # Get child information (latest child if multiple)
        cursor.execute('''SELECT id, child_name, sex, birth_date, age_group 
                         FROM children WHERE user_id = ? 
                         ORDER BY created_at DESC LIMIT 1''', (user[0],))
        child = cursor.fetchone()
        
        conn.close()
        
        token = jwt.encode({
            'user_id': user[0],
            'child_id': child[0] if child else None,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, app.config['SECRET_KEY'])
        
        response = {
            'token': token,
            'user': {
                'id': user[0],
                'name': user[1],
                'email': email
            }
        }
        
        if child:
            response['child'] = {
                'id': child[0],
                'name': child[1],
                'sex': child[2],
                'birthDate': child[3],
                'ageGroup': child[4]
            }
        
        return jsonify(response)
    else:
        conn.close()
        return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/api/questions/<age_group>', methods=['GET'])
def get_questions(age_group):
    """Get intelligence questions for specific age group"""
    if age_group not in INTELLIGENCE_QUESTIONS:
        return jsonify({'error': f'Age group {age_group} not found'}), 404
    
    questions = INTELLIGENCE_QUESTIONS[age_group]
    formatted_questions = []
    
    for category, question_data in questions.items():
        formatted_question = {
            'id': f'{category}_{age_group}',
            'category': category,
            'question': question_data['prompt'],
            'options': question_data['options'],
            'image': question_data.get('image', ''),
            'interaction': question_data.get('interaction', 'tap'),
            'points': 1
        }
        formatted_questions.append(formatted_question)
    
    return jsonify({
        'age_group': age_group,
        'questions': formatted_questions
    })

@app.route('/api/physical/<age_group>', methods=['GET'])
def get_physical_task(age_group):
    """Get physical task for specific age group"""
    if age_group not in PHYSICAL_TASKS:
        return jsonify({'error': f'Physical task for age group {age_group} not found'}), 404
    
    return jsonify({
        'age_group': age_group,
        'task': PHYSICAL_TASKS[age_group]
    })

@app.route('/api/linguistic/<age_group>', methods=['GET'])
def get_linguistic_task(age_group):
    """Get linguistic task for specific age group"""
    if age_group not in LINGUISTIC_TASKS:
        return jsonify({'error': f'Linguistic task for age group {age_group} not found'}), 404
    
    return jsonify({
        'age_group': age_group,
        'task': LINGUISTIC_TASKS[age_group]
    })

@app.route('/api/submit-assessment', methods=['POST'])
def submit_assessment():
    data = request.get_json()
    
    # Try to extract user_id from token, fallback to demo user
    user_id = 1  # Default demo user
    child_id = None
    
    try:
        token = request.headers.get('Authorization')
        if token:
            token = token.split(' ')[1]  # Remove 'Bearer ' prefix
            decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = decoded_token['user_id']
            child_id = decoded_token.get('child_id')
    except Exception as e:
        print(f"Token extraction failed, using demo user: {e}")
        # Continue with demo user
    
    # Try to get child_id from token or find the user's latest child
    if not child_id:
        # Find the latest child for this user
        conn = sqlite3.connect('assessment.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM children WHERE user_id = ? ORDER BY created_at DESC LIMIT 1', (user_id,))
        child_result = cursor.fetchone()
        if child_result:
            child_id = child_result[0]
        conn.close()
    
    age_group = data.get('age_group')
    
    # Get detailed responses for proper calculation
    intelligence_responses = data.get('intelligence_responses', [])
    physical_details = data.get('physical_details', {})
    linguistic_details = data.get('linguistic_details', {})
    
    # CALCULATE SCORES FROM ACTUAL DATA, not from frontend
    # Intelligence: Count correct answers
    intelligence_score = sum(1 for r in intelligence_responses if r.get('correct', False))
    
    # Physical: 1 if completed successfully with sufficient success count, 0 otherwise
    # Require at least 5 successful detections for physical tasks (full completion)
    physical_score = 1 if (
        physical_details.get('completed', False) and 
        physical_details.get('success_count', 0) >= 5
    ) else 0
    
    # Linguistic: 1 if completed successfully with actual AI detection, 0 otherwise  
    # Require at least 1 successful recognition for linguistic tasks
    linguistic_score = 1 if (
        linguistic_details.get('completed', False) and 
        linguistic_details.get('success_count', 0) >= 1
    ) else 0
    
    # Calculate total score
    total_score = intelligence_score + physical_score + linguistic_score
    
    # DEBUG: Print score calculations  
    print(f"DEBUG: Score Calculations:")
    print(f"  Intelligence responses: {len(intelligence_responses)}")
    print(f"  Intelligence correct: {intelligence_score}")
    print(f"  Physical details: completed={physical_details.get('completed')}, success_count={physical_details.get('success_count')}")
    print(f"  Physical score: {physical_score}")
    print(f"  Linguistic details: completed={linguistic_details.get('completed')}, success_count={linguistic_details.get('success_count')}")
    print(f"  Linguistic score: {linguistic_score}")
    print(f"  Total score: {total_score}")
    
    conn = sqlite3.connect('assessment.db')
    cursor = conn.cursor()
    
    # Create tables if they don't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS question_responses (
            response_id INTEGER PRIMARY KEY AUTOINCREMENT,
            result_id INTEGER NOT NULL,
            child_id INTEGER,
            assessment_type TEXT NOT NULL,
            question_id TEXT NOT NULL,
            question_text TEXT NOT NULL,
            child_answer TEXT,
            correct_answer TEXT,
            is_correct TEXT DEFAULT 'false',
            response_time_seconds INTEGER,
            difficulty_level INTEGER DEFAULT 1,
            attempts INTEGER DEFAULT 1,
            hints_used INTEGER DEFAULT 0,
            ai_confidence_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ai_task_responses (
            ai_response_id INTEGER PRIMARY KEY AUTOINCREMENT,
            result_id INTEGER NOT NULL,
            child_id INTEGER,
            task_type TEXT NOT NULL,
            task_name TEXT NOT NULL,
            success_count INTEGER DEFAULT 0,
            total_attempts INTEGER DEFAULT 0,
            completion_time_seconds INTEGER,
            success_rate REAL,
            ai_feedback TEXT,
            was_completed TEXT DEFAULT 'false',
            was_skipped TEXT DEFAULT 'false',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert assessment result with proper handling of child_id
    if child_id:
        cursor.execute('''
            INSERT INTO assessment_results 
            (user_id, child_id, age_group, intelligence_score, physical_score, linguistic_score, total_score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, child_id, age_group, intelligence_score, physical_score, linguistic_score, total_score))
    else:
        cursor.execute('''
            INSERT INTO assessment_results 
            (user_id, age_group, intelligence_score, physical_score, linguistic_score, total_score)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, age_group, intelligence_score, physical_score, linguistic_score, total_score))
    
    result_id = cursor.lastrowid
    
    # Save detailed intelligence question responses
    for response in intelligence_responses:
        cursor.execute('''
            INSERT INTO question_responses 
            (result_id, child_id, assessment_type, question_id, question_text, 
             child_answer, correct_answer, is_correct, response_time_seconds, 
             difficulty_level, attempts)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            result_id, child_id, 'intelligence', 
            response.get('question_id', ''),
            response.get('question', ''),
            response.get('user_answer', ''),
            response.get('correct_answer', ''),
            'true' if response.get('correct', False) else 'false',
            response.get('response_time', 0),
            response.get('difficulty', 1),
            response.get('attempts', 1)
        ))
    
    # Save physical task details
    if physical_details:
        print(f"DEBUG: Saving physical task details: {physical_details}")
        cursor.execute('''
            INSERT INTO ai_task_responses
            (result_id, child_id, task_type, task_name, success_count, 
             total_attempts, completion_time_seconds, success_rate, ai_feedback,
             was_completed, was_skipped)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            result_id, child_id, 
            physical_details.get('task_type', 'physical'),
            physical_details.get('task_name', 'Physical Assessment'),
            physical_details.get('success_count', 0),
            physical_details.get('total_attempts', 0),
            calculate_completion_time(
                physical_details.get('start_time'),
                physical_details.get('end_time')
            ) or physical_details.get('completion_time', 0),
            calculate_ai_success_rate([physical_details]) if physical_details.get('total_attempts', 0) > 0 else 0.0,
            physical_details.get('feedback', ''),
            'true' if physical_details.get('completed', False) else 'false',
            'true' if physical_details.get('skipped', False) else 'false'
        ))
    
    # Save linguistic task details  
    if linguistic_details:
        print(f"DEBUG: Saving linguistic task details: {linguistic_details}")
        cursor.execute('''
            INSERT INTO ai_task_responses
            (result_id, child_id, task_type, task_name, success_count,
             total_attempts, completion_time_seconds, success_rate, ai_feedback,
             was_completed, was_skipped)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            result_id, child_id,
            linguistic_details.get('task_type', 'linguistic'), 
            linguistic_details.get('task_name', 'Linguistic Assessment'),
            linguistic_details.get('success_count', 0),
            linguistic_details.get('total_attempts', 0),
            calculate_completion_time(
                linguistic_details.get('start_time'),
                linguistic_details.get('end_time')
            ) or linguistic_details.get('completion_time', 0),
            calculate_ai_success_rate([linguistic_details]) if linguistic_details.get('total_attempts', 0) > 0 else 0.0,
            linguistic_details.get('feedback', ''),
            'true' if linguistic_details.get('completed', False) else 'false',
            'true' if linguistic_details.get('skipped', False) else 'false'
        ))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'message': 'Assessment submitted successfully',
        'result_id': result_id,
        'child_id': child_id,
        'total_score': total_score,
        'max_score': len(intelligence_responses) + 2,  # Dynamic based on intelligence questions + 2 binary tasks
        'breakdown': {
            'intelligence': f"{intelligence_score}/{len(intelligence_responses) if intelligence_responses else 4}",
            'physical': f"{physical_score}/1", 
            'linguistic': f"{linguistic_score}/1"
        },
        'debug_info': {
            'intelligence_responses_count': len(intelligence_responses),
            'intelligence_correct_count': intelligence_score,
            'physical_completed': physical_details.get('completed', False),
            'physical_success_count': physical_details.get('success_count', 0),
            'physical_calculated_score': physical_score,
            'linguistic_completed': linguistic_details.get('completed', False),
            'linguistic_success_count': linguistic_details.get('success_count', 0),
            'linguistic_calculated_score': linguistic_score,
            'total_calculated': total_score
        },
        'details_saved': {
            'intelligence_questions': len(intelligence_responses),
            'physical_task': bool(physical_details),
            'linguistic_task': bool(linguistic_details)
        },
        'detailed_scoring': {
            'intelligence': {
                'correct': len([r for r in intelligence_responses if r.get('correct', False)]),
                'total': len(intelligence_responses),
                'accuracy': round(len([r for r in intelligence_responses if r.get('correct', False)]) / len(intelligence_responses) * 100, 1) if intelligence_responses else 0
            },
            'physical': {
                'success_count': 1 if (physical_details and physical_details.get('completed', False) and physical_details.get('success_count', 0) > 0) else 0,
                'total_attempts': 1,  # Always show as binary (0 or 1 out of 1)
                'success_rate': 100 if (physical_details and physical_details.get('completed', False) and physical_details.get('success_count', 0) > 0) else 0,
                'completed': physical_details.get('completed', False) if physical_details else False
            },
            'linguistic': {
                'success_count': 1 if (linguistic_details and linguistic_details.get('completed', False) and linguistic_details.get('success_count', 0) > 0) else 0,
                'total_attempts': 1,  # Always show as binary (0 or 1 out of 1)
                'success_rate': 100 if (linguistic_details and linguistic_details.get('completed', False) and linguistic_details.get('success_count', 0) > 0) else 0,
                'completed': linguistic_details.get('completed', False) if linguistic_details else False
            }
        }
    })

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    conn = sqlite3.connect('assessment.db')
    cursor = conn.cursor()
    
    # Get highest score per child to avoid duplicates
    cursor.execute('''
        SELECT c.child_name, u.parent_name, ar.total_score, ar.age_group, ar.completed_at,
               COUNT(*) as attempt_count
        FROM assessment_results ar
        JOIN users u ON ar.user_id = u.id
        LEFT JOIN children c ON ar.child_id = c.id
        WHERE ar.total_score = (
            SELECT MAX(total_score) 
            FROM assessment_results ar2 
            WHERE ar2.child_id = ar.child_id OR (ar2.child_id IS NULL AND ar2.user_id = ar.user_id)
        )
        GROUP BY COALESCE(ar.child_id, ar.user_id)
        ORDER BY ar.total_score DESC
        LIMIT 10
    ''')
    results = cursor.fetchall()
    conn.close()
    
    leaderboard = []
    for i, result in enumerate(results):
        child_name = result[0] if result[0] else "Child"
        parent_name = result[1]
        score = result[2]
        age_group = result[3]
        completed_at = result[4]
        attempt_count = result[5]
        
        leaderboard.append({
            'rank': i + 1,
            'name': f"{child_name} (Parent: {parent_name})",
            'child_name': child_name,
            'parent_name': parent_name,
            'score': f"{score}/4",  # Show score out of 4
            'raw_score': score,
            'age_group': age_group,
            'completed_at': convert_utc_to_ist(completed_at),  # Convert UTC to IST
            'attempts': attempt_count,
            'badge': '🥇' if i == 0 else '🥈' if i == 1 else '🥉' if i == 2 else '⭐'
        })
    
    return jsonify(leaderboard)

@app.route('/api/progress/<int:child_id>', methods=['GET'])
def get_child_progress(child_id):
    """Get assessment progress for a specific child"""
    conn = sqlite3.connect('assessment.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT DATE(completed_at) as date, total_score, age_group, completed_at
        FROM assessment_results 
        WHERE child_id = ? 
        ORDER BY completed_at ASC
    ''', (child_id,))
    
    results = cursor.fetchall()
    conn.close()
    
    if len(results) < 2:
        return jsonify({
            'message': 'Not enough data for progress tracking',
            'data': [],
            'summary': {
                'total_attempts': len(results),
                'latest_score': results[0][1] if results else 0,
                'improvement': 'N/A'
            }
        })
    
    progress_data = []
    for result in results:
        progress_data.append({
            'date': result[0],
            'score': result[1],
            'age_group': result[2],
            'timestamp': result[3]
        })
    
    # Calculate improvement
    first_score = results[0][1]
    latest_score = results[-1][1]
    improvement = round(((latest_score - first_score) / first_score) * 100, 1) if first_score > 0 else 0
    
    return jsonify({
        'data': progress_data,
        'summary': {
            'total_attempts': len(results),
            'first_score': first_score,
            'latest_score': latest_score,
            'improvement': f"{improvement:+.1f}%" if improvement != 0 else "No change",
            'average_score': round(sum(r[1] for r in results) / len(results), 1)
        }
    })

@app.route('/api/age-group-stats/<age_group>', methods=['GET'])
def get_age_group_stats(age_group):
    """Get statistics for a specific age group"""
    conn = sqlite3.connect('assessment.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT total_score, intelligence_score, physical_score, linguistic_score
        FROM assessment_results 
        WHERE age_group = ?
    ''', (age_group,))
    
    results = cursor.fetchall()
    conn.close()
    
    if not results:
        return jsonify({
            'message': f'No data available for age group {age_group}',
            'stats': None
        })
    
    total_scores = [r[0] for r in results]
    intelligence_scores = [r[1] for r in results]
    physical_scores = [r[2] for r in results]
    linguistic_scores = [r[3] for r in results]
    
    return jsonify({
        'age_group': age_group,
        'sample_size': len(results),
        'stats': {
            'total': {
                'average': round(sum(total_scores) / len(total_scores), 1),
                'max': max(total_scores),
                'min': min(total_scores)
            },
            'intelligence': {
                'average': round(sum(intelligence_scores) / len(intelligence_scores), 1),
                'max': max(intelligence_scores)
            },
            'physical': {
                'success_rate': round((sum(physical_scores) / len(physical_scores)) * 100, 1)
            },
            'linguistic': {
                'success_rate': round((sum(linguistic_scores) / len(linguistic_scores)) * 100, 1)
            }
        }
    })

# ===== DETAILED RESPONSE ANALYSIS ENDPOINTS =====

@app.route('/api/child-responses/<int:child_id>', methods=['GET'])
@token_required
def get_child_detailed_responses(child_id):
    """Get all detailed responses for a specific child, grouped by attempts"""
    conn = sqlite3.connect('assessment.db')
    cursor = conn.cursor()
    
    # Get all assessment results for this child (each result = one attempt)
    cursor.execute('''
        SELECT ar.id, ar.completed_at, ar.age_group, ar.intelligence_score, ar.physical_score, ar.linguistic_score, ar.total_score
        FROM assessment_results ar
        WHERE ar.child_id = ?
        ORDER BY ar.completed_at DESC
    ''', (child_id,))
    assessment_results = cursor.fetchall()
    
    if not assessment_results:
        conn.close()
        return jsonify({
            'child_id': child_id,
            'attempts': [],
            'summary': {
                'total_attempts': 0,
                'latest_attempt': None
            }
        })
    
    # Process each attempt
    attempts = []
    for attempt in assessment_results:
        result_id, completed_at, age_group, intelligence_score, physical_score, linguistic_score, total_score = attempt
        
        # Get intelligence question responses for this attempt
        cursor.execute('''
            SELECT qr.*
            FROM question_responses qr
            WHERE qr.result_id = ?
            ORDER BY qr.created_at ASC
        ''', (result_id,))
        intelligence_responses = cursor.fetchall()
        
        # Get AI task responses for this attempt
        cursor.execute('''
            SELECT atr.*
            FROM ai_task_responses atr
            WHERE atr.result_id = ?
            ORDER BY atr.created_at ASC
        ''', (result_id,))
        ai_task_responses = cursor.fetchall()
        
        # Format intelligence responses for this attempt
        intelligence_data = []
        for resp in intelligence_responses:
            # Ensure child_answer is properly handled (not None or empty)
            child_answer = resp[6] if resp[6] else "No answer provided"
            correct_answer = resp[7] if resp[7] else "No correct answer"
            
            intelligence_data.append({
                'response_id': resp[0],
                'question_id': resp[4],
                'question_text': resp[5] if resp[5] else "Question text not available",
                'child_answer': child_answer,
                'correct_answer': correct_answer,
                'is_correct': resp[8] == 'true',
                'response_time': resp[9] if resp[9] else 0,
                'difficulty_level': resp[10] if resp[10] else 1,
                'attempts': resp[11] if resp[11] else 1
            })
        
        # Format AI task responses for this attempt - ENSURE BINARY (0 or 1) for physical/linguistic
        ai_task_data = []
        physical_binary = 0
        linguistic_binary = 0
        
        print(f"\n=== DEBUG: Processing result_id {result_id} ===")
        
        for resp in ai_task_responses:
            task_type = resp[3]  # task_type (correct index)
            original_success = resp[5]  # success_count (correct index)
            was_skipped = resp[11] == 'true'
            was_completed = resp[10] == 'true'
            
            print(f"Task: {task_type}, success_count: {original_success}, completed: {was_completed}, skipped: {was_skipped}")
            
            # CORRECT LOGIC: Apply proper thresholds for each task type
            if task_type == 'physical' or task_type == 'physical_assessment':
                task_success = 1 if (was_completed and original_success >= 5) else 0
                physical_binary = task_success
                print(f"  -> Physical binary set to: {physical_binary}")
            elif task_type == 'linguistic' or task_type == 'linguistic_assessment':
                task_success = 1 if (was_completed and original_success >= 1) else 0
                linguistic_binary = task_success
                print(f"  -> Linguistic binary set to: {linguistic_binary}")
            else:
                task_success = 1 if (was_completed and original_success > 0) else 0
            
            # Create proper task description
            task_description = resp[4] if resp[4] else f"{task_type.replace('_', ' ').title()} Development Assessment"
            
            ai_task_data.append({
                'task_type': task_type,
                'task_name': task_description,
                'description': task_description,
                'success': task_success,  # 0 if not completed or no success, 1 if completed with success
                'was_skipped': was_skipped,
                'was_completed': was_completed,
                'completion_time': resp[7] if resp[7] else 0,
                'ai_feedback': resp[9] if resp[9] else f"Task {'completed successfully' if task_success == 1 else 'not completed or failed'}"
            })
        
        # Calculate scores for this attempt
        intelligence_correct = sum(1 for r in intelligence_data if r['is_correct'])
        intelligence_total = len(intelligence_data) if intelligence_data else 4  # Default to 4 questions
        
        print(f"Final calculated scores: physical_binary={physical_binary}, linguistic_binary={linguistic_binary}")
        
        # Calculate correct attempt number (counting from newest to oldest, starting at 1)
        current_attempt_number = len(assessment_results) - len(attempts)
        
        attempt_data = {
            'attempt_number': current_attempt_number,  # Correct chronological order
            'result_id': result_id,
            'assessment_date': convert_utc_to_ist(completed_at),  # Convert UTC to IST
            'age_group': age_group,
            'scores': {
                'intelligence': intelligence_correct,
                'intelligence_total': intelligence_total,
                'intelligence_percentage': round((intelligence_correct / intelligence_total) * 100, 1) if intelligence_total > 0 else 0,
                'physical': physical_binary,  # ALWAYS 0 or 1
                'linguistic': linguistic_binary,  # ALWAYS 0 or 1
                'total': intelligence_correct + physical_binary + linguistic_binary,
                'max_total': intelligence_total + 2  # Intelligence questions + 2 binary tasks
            },
            'intelligence_responses': intelligence_data,
            'ai_tasks': ai_task_data
        }
        
        attempts.append(attempt_data)
    
    conn.close()
    
    # Latest attempt summary
    latest = attempts[0] if attempts else None
    
    return jsonify({
        'child_id': child_id,
        'attempts': attempts,
        'summary': {
            'total_attempts': len(attempts),
            'latest_attempt': {
                'date': latest['assessment_date'],
                'age_group': latest['age_group'],
                'total_score': latest['scores']['total'],
                'max_score': latest['scores']['max_total'],
                'intelligence_score': latest['scores']['intelligence'],
                'physical_score': latest['scores']['physical'],  # 0 or 1
                'linguistic_score': latest['scores']['linguistic']  # 0 or 1
            } if latest else None
        }
    })

@app.route('/api/question-analysis/<question_id>', methods=['GET'])
def get_question_analysis(question_id):
    """Get analysis for a specific question across all children"""
    conn = sqlite3.connect('assessment.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT qr.*, c.child_name, ar.age_group
        FROM question_responses qr
        JOIN assessment_results ar ON qr.result_id = ar.id
        LEFT JOIN children c ON qr.child_id = c.id
        WHERE qr.question_id = ?
        ORDER BY qr.created_at DESC
    ''', (question_id,))
    
    responses = cursor.fetchall()
    conn.close()
    
    if not responses:
        return jsonify({
            'message': f'No responses found for question {question_id}',
            'data': []
        })
    
    # Analyze responses
    total_responses = len(responses)
    correct_responses = sum(1 for r in responses if r[8] == 'true')
    accuracy_rate = round((correct_responses / total_responses) * 100, 1)
    
    # Group by age group
    age_group_stats = {}
    for resp in responses:
        age_group = resp[-1]
        if age_group not in age_group_stats:
            age_group_stats[age_group] = {'total': 0, 'correct': 0}
        age_group_stats[age_group]['total'] += 1
        if resp[8] == 'true':
            age_group_stats[age_group]['correct'] += 1
    
    # Calculate age group accuracy rates
    for age_group in age_group_stats:
        stats = age_group_stats[age_group]
        stats['accuracy_rate'] = round((stats['correct'] / stats['total']) * 100, 1)
    
    # Common wrong answers
    wrong_answers = [r[6] for r in responses if r[8] == 'false' and r[6]]
    common_wrong_answers = {}
    for answer in wrong_answers:
        common_wrong_answers[answer] = common_wrong_answers.get(answer, 0) + 1
    
    return jsonify({
        'question_id': question_id,
        'question_text': responses[0][5],
        'correct_answer': responses[0][7],
        'statistics': {
            'total_responses': total_responses,
            'correct_responses': correct_responses,
            'accuracy_rate': accuracy_rate,
            'average_response_time': round(sum(r[9] or 0 for r in responses) / total_responses, 1),
            'average_attempts': round(sum(r[11] or 1 for r in responses) / total_responses, 1)
        },
        'age_group_breakdown': age_group_stats,
        'common_wrong_answers': sorted(common_wrong_answers.items(), key=lambda x: x[1], reverse=True)[:5]
    })

@app.route('/api/assessment-insights/<int:result_id>', methods=['GET'])
@token_required
def get_assessment_insights(result_id):
    """Get detailed insights for a specific assessment"""
    conn = sqlite3.connect('assessment.db')
    cursor = conn.cursor()
    
    # Get assessment basic info
    cursor.execute('''
        SELECT ar.*, c.child_name, u.parent_name
        FROM assessment_results ar
        LEFT JOIN children c ON ar.child_id = c.id
        JOIN users u ON ar.user_id = u.id
        WHERE ar.id = ?
    ''', (result_id,))
    
    assessment = cursor.fetchone()
    if not assessment:
        conn.close()
        return jsonify({'error': 'Assessment not found'}), 404
    
    # Get question responses for this assessment
    cursor.execute('''
        SELECT * FROM question_responses WHERE result_id = ?
    ''', (result_id,))
    question_responses = cursor.fetchall()
    
    # Get AI task responses for this assessment
    cursor.execute('''
        SELECT * FROM ai_task_responses WHERE result_id = ?
    ''', (result_id,))
    ai_responses = cursor.fetchall()
    
    conn.close()
    
    # Generate insights
    insights = {
        'assessment_id': result_id,
        'child_name': assessment[8] if assessment[8] else 'Child',
        'parent_name': assessment[9],
        'age_group': assessment[3],
        'total_score': assessment[7],
        'completed_at': assessment[2],
        'performance_breakdown': {
            'intelligence': {
                'score': assessment[4],
                'max_score': 2,
                'questions_answered': len(question_responses),
                'accuracy': round(sum(1 for r in question_responses if r[8] == 'true') / len(question_responses) * 100, 1) if question_responses else 0
            },
            'physical': {
                'score': assessment[5],
                'max_score': 1,
                'tasks_completed': len([r for r in ai_responses if r[4].startswith('physical') or r[4] in ['raise_hands', 'one_leg', 'turn_around', 'stand_still', 'frog_jump', 'kangaroo_jump']]),
                'success_rate': round(sum(r[9] or 0 for r in ai_responses if r[4].startswith('physical') or r[4] in ['raise_hands', 'one_leg', 'turn_around', 'stand_still', 'frog_jump', 'kangaroo_jump']) / max(len([r for r in ai_responses if r[4].startswith('physical') or r[4] in ['raise_hands', 'one_leg', 'turn_around', 'stand_still', 'frog_jump', 'kangaroo_jump']]), 1), 1)
            },
            'linguistic': {
                'score': assessment[6],
                'max_score': 1,
                'tasks_completed': len([r for r in ai_responses if r[4].startswith('linguistic') or r[4] in ['say_mama', 'say_apple', 'rhyme_cat', 'fill_blank', 'sentence_sun', 'story_kite']]),
                'success_rate': round(sum(r[9] or 0 for r in ai_responses if r[4].startswith('linguistic') or r[4] in ['say_mama', 'say_apple', 'rhyme_cat', 'fill_blank', 'sentence_sun', 'story_kite']) / max(len([r for r in ai_responses if r[4].startswith('linguistic') or r[4] in ['say_mama', 'say_apple', 'rhyme_cat', 'fill_blank', 'sentence_sun', 'story_kite']]), 1), 1)
            }
        },
        'strengths': [],
        'areas_for_improvement': [],
        'recommendations': []
    }
    
    # Generate personalized insights
    if insights['performance_breakdown']['intelligence']['accuracy'] >= 75:
        insights['strengths'].append('Strong cognitive problem-solving abilities')
    elif insights['performance_breakdown']['intelligence']['accuracy'] < 50:
        insights['areas_for_improvement'].append('Focus on cognitive development through puzzles and logic games')
    
    if insights['performance_breakdown']['physical']['success_rate'] >= 80:
        insights['strengths'].append('Excellent motor skills and physical coordination')
    elif insights['performance_breakdown']['physical']['success_rate'] < 50:
        insights['areas_for_improvement'].append('Encourage more physical activities and movement exercises')
    
    if insights['performance_breakdown']['linguistic']['success_rate'] >= 80:
        insights['strengths'].append('Great language and communication skills')
    elif insights['performance_breakdown']['linguistic']['success_rate'] < 50:
        insights['areas_for_improvement'].append('Practice speaking, reading, and vocabulary building activities')
    
    # Generate recommendations based on age group and performance
    age_group = assessment[3]
    if '0-1' in age_group:
        insights['recommendations'].extend([
            'Focus on sensory play and simple cause-and-effect toys',
            'Read colorful picture books daily',
            'Practice tummy time and encourage crawling'
        ])
    elif '1-2' in age_group:
        insights['recommendations'].extend([
            'Encourage walking and climbing activities',
            'Introduce simple words and gestures',
            'Play with stacking toys and shape sorters'
        ])
    elif '2-3' in age_group:
        insights['recommendations'].extend([
            'Practice jumping, running, and ball activities',
            'Encourage singing and storytelling',
            'Work on puzzle solving and matching games'
        ])
    
    return jsonify(insights)

@app.route('/api/child-comprehensive-analysis/<int:child_id>', methods=['GET'])
@token_required
def get_child_comprehensive_analysis(child_id):
    """
    Comprehensive analysis endpoint - Currently disabled.
    """
    return jsonify({
        'error': 'Comprehensive analysis feature is currently unavailable',
        'child_id': child_id,
        'message': 'This feature requires additional analysis modules that are not currently installed.'
    }), 501

if __name__ == '__main__':
    init_db()
    
    # Register AI assessment routes if available
    if AI_ROUTES_AVAILABLE:
        app.register_blueprint(assessment_ai_bp)
        print("✅ AI Assessment routes registered (MediaPipe + Vosk)")
    else:
        print("⚠️  AI Assessment routes not available - using basic UI only")
    
    print("🚀 Starting Flask backend on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
