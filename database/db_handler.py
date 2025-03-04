import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

class SceneDatabase:
    def __init__(self, db_path: str = 'scenes.db'):
        self.conn = sqlite3.connect(db_path)
        self._create_tables()
        
    def _create_tables(self):
        with self.conn:
            self.conn.executescript('''
                -- Include the schema SQL from above here
                ''')

    def add_scene(self, metadata: Dict):
        sql = '''INSERT INTO scenes (
            timestamp, latitude, longitude, resolution, 
            camera_id, media_path
        ) VALUES (?, ?, ?, ?, ?, ?)'''
        values = (
            metadata['timestamp'],
            metadata.get('latitude'),
            metadata.get('longitude'),
            metadata.get('resolution'),
            metadata['camera_id'],
            metadata['media_path']
        )
        cursor = self.conn.cursor()
        cursor.execute(sql, values)
        return cursor.lastrowid

    def add_detections(self, scene_id: int, detections: List[Dict]):
        sql = '''INSERT INTO detections (
            scene_id, class_label, confidence,
            x_min, y_min, x_max, y_max
        ) VALUES (?, ?, ?, ?, ?, ?, ?)'''
        
        values = [(scene_id, d['class'], d['confidence'], 
                  d['bbox'][0], d['bbox'][1], 
                  d['bbox'][2], d['bbox'][3]) 
                 for d in detections]
        
        with self.conn:
            self.conn.executemany(sql, values)

    def add_annotation(self, scene_id: int, annotation: Dict):
        sql = '''INSERT INTO annotations (
            scene_id, label_type, description,
            class_label, x_min, y_min, x_max, y_max, annotated_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        
        values = (
            scene_id,
            annotation['label_type'],
            annotation.get('description'),
            annotation.get('class_label'),
            annotation.get('x_min'),
            annotation.get('y_min'),
            annotation.get('x_max'),
            annotation.get('y_max'),
            annotation.get('annotated_by')
        )
        with self.conn:
            self.conn.execute(sql, values)

    def get_scenes_by_time_range(self, start: datetime, end: datetime):
        sql = '''SELECT * FROM scenes 
                WHERE timestamp BETWEEN ? AND ?'''
        return self.conn.execute(sql, (start.isoformat(), end.isoformat())).fetchall()

    def get_detections_by_class(self, class_label: str, confidence_threshold: float = 0.5):
        sql = '''SELECT * FROM detections 
                WHERE class_label = ? AND confidence >= ?'''
        return self.conn.execute(sql, (class_label, confidence_threshold)).fetchall()

    def assign_to_dataset(self, scene_ids: List[int], dataset_type: str):
        sql = '''INSERT INTO datasets (scene_id, dataset_type) 
                 VALUES (?, ?)'''
        values = [(sid, dataset_type) for sid in scene_ids]
        with self.conn:
            self.conn.executemany(sql, values)

    def get_training_data(self):
        sql = '''SELECT s.*, d.description 
                 FROM scenes s
                 JOIN datasets ds ON s.scene_id = ds.scene_id
                 LEFT JOIN scene_descriptions d ON s.scene_id = d.scene_id
                 WHERE ds.dataset_type = 'train' '''
        return self.conn.execute(sql).fetchall()

    def add_scene_description(self, scene_id: int, description: str, 
                            confidence: float, model_version: str):
        sql = '''INSERT INTO scene_descriptions 
                 (scene_id, description, confidence, model_version)
                 VALUES (?, ?, ?, ?)'''
        with self.conn:
            self.conn.execute(sql, (scene_id, description, confidence, model_version))

    def incremental_update(self, new_scenes: List[Dict]):
        with self.conn:
            for scene in new_scenes:
                scene_id = self.add_scene(scene['metadata'])
                if 'detections' in scene:
                    self.add_detections(scene_id, scene['detections'])
                if 'description' in scene:
                    self.add_scene_description(scene_id, scene['description'], 
                                             scene['confidence'], scene['model_version'])

    def close(self):
        self.conn.close()


    # CRUD Operations for Scenes
    def create_scene(self, metadata: Dict) -> int:
        """Create a new scene entry"""
        return self.add_scene(metadata)  # Existing method

    def get_scene(self, scene_id: int) -> Optional[Dict]:
        """Read a single scene by ID"""
        sql = '''SELECT * FROM scenes WHERE scene_id = ?'''
        cursor = self.conn.execute(sql, (scene_id,))
        row = cursor.fetchone()
        return self._row_to_dict(row, cursor.description) if row else None

    def update_scene(self, scene_id: int, updates: Dict):
        """Update scene metadata"""
        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        sql = f'''UPDATE scenes SET {set_clause} WHERE scene_id = ?'''
        values = list(updates.values()) + [scene_id]
        
        with self.conn:
            self.conn.execute(sql, values)

    def delete_scene(self, scene_id: int):
        """Delete a scene and its related data (cascade delete)"""
        sql = '''DELETE FROM scenes WHERE scene_id = ?'''
        with self.conn:
            self.conn.execute(sql, (scene_id,))

    # CRUD Operations for Detections
    def get_detection(self, detection_id: int) -> Optional[Dict]:
        """Read a single detection by ID"""
        sql = '''SELECT * FROM detections WHERE detection_id = ?'''
        cursor = self.conn.execute(sql, (detection_id,))
        row = cursor.fetchone()
        return self._row_to_dict(row, cursor.description) if row else None

    def update_detection(self, detection_id: int, updates: Dict):
        """Update detection attributes"""
        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        sql = f'''UPDATE detections SET {set_clause} WHERE detection_id = ?'''
        values = list(updates.values()) + [detection_id]
        
        with self.conn:
            self.conn.execute(sql, values)

    def delete_detection(self, detection_id: int):
        """Delete a specific detection"""
        sql = '''DELETE FROM detections WHERE detection_id = ?'''
        with self.conn:
            self.conn.execute(sql, (detection_id,))

    # CRUD Operations for Annotations
    def get_annotation(self, annotation_id: int) -> Optional[Dict]:
        """Read a single annotation by ID"""
        sql = '''SELECT * FROM annotations WHERE annotation_id = ?'''
        cursor = self.conn.execute(sql, (annotation_id,))
        row = cursor.fetchone()
        return self._row_to_dict(row, cursor.description) if row else None

    def update_annotation(self, annotation_id: int, updates: Dict):
        """Update annotation details"""
        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        sql = f'''UPDATE annotations SET {set_clause} WHERE annotation_id = ?'''
        values = list(updates.values()) + [annotation_id]
        
        with self.conn:
            self.conn.execute(sql, values)

    def delete_annotation(self, annotation_id: int):
        """Delete a specific annotation"""
        sql = '''DELETE FROM annotations WHERE annotation_id = ?'''
        with self.conn:
            self.conn.execute(sql, (annotation_id,))

    # Utility Methods
    def _row_to_dict(self, row, description):
        """Convert SQLite row to dictionary"""
        return {description[i][0]: value for i, value in enumerate(row)}

    # Enhanced Query Methods
    def get_all_scenes(self, limit: int = 100) -> List[Dict]:
        """Read all scenes with pagination"""
        sql = '''SELECT * FROM scenes ORDER BY timestamp DESC LIMIT ?'''
        cursor = self.conn.execute(sql, (limit,))
        return [self._row_to_dict(row, cursor.description) for row in cursor.fetchall()]

    def get_scene_detections(self, scene_id: int) -> List[Dict]:
        """Get all detections for a specific scene"""
        sql = '''SELECT * FROM detections WHERE scene_id = ?'''
        cursor = self.conn.execute(sql, (scene_id,))
        return [self._row_to_dict(row, cursor.description) for row in cursor.fetchall()]