from flask import jsonify
import mysql.connector
import os

def get_db_connection():
    """Create database connection"""
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'af_db'),
        user=os.getenv('DB_USER', 'frontend'),
        password=os.getenv('DB_PASSWORD', 'frontend-secret-password'),
        database=os.getenv('DB_DATABASE', 'af-frontend'),
        port=int(os.getenv('DB_PORT', 3306))
    )

def getUserStats(userId):
    """Get user task statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Single optimized query instead of 4 separate queries
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT t.id) as total,
                SUM(CASE WHEN r.state = 2 THEN 1 ELSE 0 END) as finished,
                SUM(CASE WHEN r.state = 1 THEN 1 ELSE 0 END) as running,
                SUM(CASE WHEN r.state = 0 THEN 1 ELSE 0 END) as failed
            FROM af_tasks t
            LEFT JOIN af_results r ON t.id = r.id
            WHERE t.userId = %s
        """, (userId,))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return {
            'total_tasks': result['total'] or 0,
            'finished_tasks': result['finished'] or 0,
            'running_tasks': result['running'] or 0,
            'failed_tasks': result['failed'] or 0
        }
    except Exception as e:
        print(f"Error: {e}")
        return None

def createEntrypoints(app):
    """Create API endpoints"""
    
    @app.route('/api/user/<int:userId>/stats', methods=['GET'])
    def get_user_stats(userId):
        stats = getUserStats(userId)
        return jsonify(stats) if stats else jsonify({'error': 'Failed'}), 200 if stats else 500
    
    @app.route('/api/user/<int:userId>/dashboard', methods=['GET'])
    def get_user_dashboard(userId):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, name, email, is_admin, enabled, last_login FROM af_users WHERE id = %s", (userId,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            return jsonify({'user': user, 'stats': getUserStats(userId)}), 200
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({'error': 'Failed'}), 500